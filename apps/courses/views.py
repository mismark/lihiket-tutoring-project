import os

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import darkblue
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
import qrcode

from apps.certificates.models import Certificate
from apps.accounts.permissions import has_course_access, get_teacher_courses
from .models import Course, Enrollment, CourseProgress
from .forms import CourseForm


def _is_teacher_or_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.role in ("teacher", "admin")
    )


def _student_can_enroll(student, course):
    """
    A student can enroll only if their grade_level matches
    the course's subject grade_level.
    """
    if not student.grade_level:
        return False, "Your grade level is not set. Please update your profile."
    if not course.subject:
        return True, ""
    if student.grade_level != course.subject.grade_level:
        grade_display = course.subject.get_grade_level_display()
        return False, (
            f"This course is for {grade_display} students only. "
            f"Your grade level does not match."
        )
    return True, ""


@login_required
def course_list(request):

    query = request.GET.get("q", "")
    level = request.GET.get("level", "")
    status = request.GET.get("status", "")
    sort = request.GET.get("sort", "")

    # Scope queryset by role
    if request.user.role == "teacher":
        # Teacher sees only courses in their assigned subjects
        courses = get_teacher_courses(request.user)
    elif request.user.role == "student":
        # Student sees only published courses matching their grade level
        if request.user.grade_level:
            courses = Course.objects.filter(
                status="published",
                subject__grade_level=request.user.grade_level,
            )
        else:
            courses = Course.objects.none()
    else:
        # Admin / parent / superuser sees all
        courses = Course.objects.all()

    # Search
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    # Filter by level
    if level:
        courses = courses.filter(level=level)

    # Filter by status
    if status:
        courses = courses.filter(status=status)

    # Sorting
    if sort == "oldest":
        courses = courses.order_by("created_at")

    elif sort == "title":
        courses = courses.order_by("title")

    elif sort == "price_low":
        courses = courses.order_by("price")

    elif sort == "price_high":
        courses = courses.order_by("-price")

    else:
        courses = courses.order_by("-created_at")

    # Pagination (AFTER filtering and sorting)
    paginator = Paginator(courses, 6)

    page_number = request.GET.get("page")

    courses = paginator.get_page(page_number)
    # Recent courses
    recent_courses = Course.objects.order_by("-created_at")[:5]


    return render(
        request,
        "courses/course_list.html",
        {
            "courses": courses,
            "query": query,
            "level": level,
            "status": status,
            "sort": sort,
            "is_teacher_or_admin": _is_teacher_or_admin(request.user),

            "total_courses": Course.objects.count(),
            "published_courses": Course.objects.filter(status="published").count(),
            "draft_courses": Course.objects.filter(status="draft").count(),

            "beginner_courses": Course.objects.filter(level="beginner").count(),
            "intermediate_courses": Course.objects.filter(level="intermediate").count(),
            "advanced_courses": Course.objects.filter(level="advanced").count(),

            "recent_courses": recent_courses,
        }
    )
 

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)

    is_enrolled = False
    can_enroll  = False
    enroll_blocked_reason = ""
    progress    = None

    # ── Student-specific context ───────────────────────────────────
    student_ctx = {}
    if request.user.role == "student":
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=course
        ).exists()

        if not is_enrolled:
            can_enroll, enroll_blocked_reason = _student_can_enroll(request.user, course)

        if is_enrolled:
            progress, _ = CourseProgress.objects.get_or_create(
                student=request.user, course=course,
            )
            from django.utils import timezone as tz
            from apps.assignments.models import Assignment, AssignmentSubmission
            from apps.documents.models import Document
            from apps.lessons.models import Lesson
            from apps.quizzes.models import Quiz
            from apps.exams.models import Exam
            from apps.live_classes.models import LiveClass

            now_dt         = tz.now()
            assignments_qs = Assignment.objects.filter(course=course, is_active=True).order_by("due_date")
            my_submissions = AssignmentSubmission.objects.filter(
                assignment__course=course, student=request.user
            )
            submission_map = {s.assignment_id: s for s in my_submissions}
            submitted_ids  = set(submission_map.keys())

            assignments_list = list(assignments_qs)
            for a in assignments_list:
                a.my_submission = submission_map.get(a.pk)
                a.is_past_due   = now_dt > a.due_date

            documents    = Document.objects.filter(
                course=course, visibility__in=["public", "students"]
            ).order_by("-created_at")
            lessons      = Lesson.objects.filter(course=course, status="published").order_by("lesson_order")
            quizzes      = Quiz.objects.filter(course=course, is_active=True)
            exams        = Exam.objects.filter(course=course, is_active=True)
            live_classes = LiveClass.objects.filter(
                course=course
            ).exclude(status="cancelled").order_by("start_datetime")

            student_ctx = {
                "assignments_count":  len(assignments_list),
                "submitted_count":    len(submitted_ids),
                "pending_count":      len(assignments_list) - len(submitted_ids),
                "documents_count":    documents.count(),
                "lessons_count":      lessons.count(),
                "quizzes_count":      quizzes.count(),
                "exams_count":        exams.count(),
                "live_classes_count": live_classes.count(),
                "assignments":        assignments_list,
                "submitted_ids":      submitted_ids,
                "documents":          documents,
                "lessons":            lessons,
                "quizzes":            quizzes,
                "exams":              exams,
                "live_classes":       live_classes,
                "now_ts":             int(now_dt.timestamp()),
            }

    # ── Teacher / admin context ────────────────────────────────────
    teacher_ctx = {}
    if request.user.role in ("teacher", "admin") or request.user.is_superuser:
        from apps.lessons.models import Lesson
        from apps.documents.models import Document
        from apps.assignments.models import Assignment
        from apps.quizzes.models import Quiz
        from apps.exams.models import Exam
        from apps.live_classes.models import LiveClass
        from django.utils import timezone as tz

        enrolled_students = Enrollment.objects.filter(course=course).count()
        t_lessons     = Lesson.objects.filter(course=course).order_by("lesson_order")
        t_documents   = Document.objects.filter(course=course).order_by("-created_at")
        t_assignments = Assignment.objects.filter(course=course).order_by("due_date")
        t_quizzes     = Quiz.objects.filter(course=course)
        t_exams       = Exam.objects.filter(course=course)
        t_live_classes = LiveClass.objects.filter(course=course).order_by("start_datetime")

        teacher_ctx = {
            "enrolled_students_count": enrolled_students,
            "t_lessons":               t_lessons,
            "t_documents":             t_documents,
            "t_assignments":           t_assignments,
            "t_quizzes":               t_quizzes,
            "t_exams":                 t_exams,
            "t_live_classes":          t_live_classes,
            "t_lessons_count":         t_lessons.count(),
            "t_documents_count":       t_documents.count(),
            "t_assignments_count":     t_assignments.count(),
            "t_quizzes_count":         t_quizzes.count(),
            "t_exams_count":           t_exams.count(),
            "t_live_classes_count":    t_live_classes.count(),
            "now_ts":                  int(tz.now().timestamp()),
        }

    return render(request, "courses/course_detail.html", {
        "course":               course,
        "is_enrolled":          is_enrolled,
        "can_enroll":           can_enroll,
        "enroll_blocked_reason": enroll_blocked_reason,
        "progress":             progress,
        "can_edit":             has_course_access(request.user, course),
        **student_ctx,
        **teacher_ctx,
    })
    

@login_required
def enroll_course(request, pk):

    course = get_object_or_404(Course, pk=pk)

    # Only students can enroll
    if request.user.role != "student":
        messages.error(request, "Only students can enroll in courses.")
        return redirect("courses:course_detail", pk=course.pk)

    # Grade level must match the course's subject grade level
    can_enroll, reason = _student_can_enroll(request.user, course)
    if not can_enroll:
        messages.error(request, reason)
        return redirect("courses:course_detail", pk=course.pk)

    # Course must be published
    if course.status != "published":
        messages.error(request, "This course is not available for enrollment.")
        return redirect("courses:course_detail", pk=course.pk)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
    )

    if created:
        messages.success(request, f'You have successfully enrolled in "{course.title}"!')
    else:
        messages.info(request, "You are already enrolled in this course.")

    return redirect("courses:course_detail", pk=course.pk)

@login_required
def update_progress(request, pk):

    course = get_object_or_404(Course, pk=pk)

    if request.user.role != "student":
        messages.error(
            request,
            "Only students can update progress."
        )
        return redirect("courses:course_detail", pk=course.pk)

    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course=course
    )

    progress, created = CourseProgress.objects.get_or_create(
        student=request.user,
        course_id=pk
    )

    if request.method == "POST":

        percent = int(request.POST.get("progress", 0))

        if percent < 0:
            percent = 0

        if percent > 100:
            percent = 100

        progress.progress = percent

        if percent == 100:
            enrollment.status = "completed"
            enrollment.save()

        progress.save()

        messages.success(
            request,
            "Progress updated successfully."
        )

    return redirect(
        "courses:course_detail",
        pk=course.pk
    )

@login_required
def course_certificate(request, pk):

    course = get_object_or_404(Course, pk=pk)

    enrollment = get_object_or_404(
        Enrollment,
        student=request.user,
        course=course,
    )

    progress = get_object_or_404(
        CourseProgress,
        student=request.user,
        course=course,
    )

    if progress.progress < 100:
        messages.error(request, "Complete the course to access your certificate.")
        return redirect("courses:course_detail", pk=course.pk)

    # Get or create the certificate record
    certificate, _ = Certificate.objects.get_or_create(
        student=request.user,
        course=course,
    )

    # Build QR code as base64 data URI so template can render it inline
    import base64
    qr_data   = request.build_absolute_uri(f"/certificates/verify/{certificate.certificate_id}/")
    qr        = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_code_b64 = "data:image/png;base64," + base64.b64encode(qr_buffer.getvalue()).decode()

    return render(request, "courses/certificate.html", {
        "course":      course,
        "progress":    progress,
        "enrollment":  enrollment,
        "certificate": certificate,
        "qr_code":     qr_code_b64,
    })
    

# for couce certificate generations and download as pdf file 

@login_required
def download_certificate(request, pk):
    
    from reportlab.platypus import Image as PDFImage
    from reportlab.lib.pagesizes import landscape
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from django.conf import settings
    import os
    
    
        
    def add_certificate_images(canvas, doc):

        canvas.saveState()


        # =====================
        # BORDER
        # =====================

        canvas.setLineWidth(3)

        canvas.rect(
            20,
            20,
            842-40,
            595-40
        )


        # =====================
        # LOGO
        # =====================

        logo_path = os.path.join(
            settings.MEDIA_ROOT,
            "certificates",
            "logo.png"
        )


        if os.path.exists(logo_path):

            canvas.drawImage(
                ImageReader(logo_path),
                371, 470,
                width=100, height=100,
                mask="auto"
            )


        # =====================
        # SIGNATURE
        # =====================

        signature_path = os.path.join(
            settings.MEDIA_ROOT,
            "certificates",
            "signature.png"
        )


        if os.path.exists(signature_path):

            canvas.drawImage(
                ImageReader(signature_path),
                120,
                60,
                width=120,
                height=50,
                mask="auto"
            )


        # =====================
        # SEAL
        # =====================

        seal_path = os.path.join(
            settings.MEDIA_ROOT,
            "certificates",
            "seal.png"
        )


        if os.path.exists(seal_path):

            canvas.drawImage(
                ImageReader(seal_path),
                650,
                50,
                width=100,
                height=100,
                mask="auto"
            )


        canvas.restoreState()

    course = get_object_or_404(
        Course,
        pk=pk
    )


    progress = get_object_or_404(
        CourseProgress,
        student=request.user,
        course=course,
    )


    if progress.progress < 100:

        messages.error(
            request,
            "Complete the course first."
        )

        return redirect(
            "courses:course_detail",
            pk=pk
        )


    # Create certificate record if it does not exist

    certificate, created = Certificate.objects.get_or_create(
    student=request.user,
    course=course,
    )


    # QR CODE VERIFICATION LINK
    qr_data = request.build_absolute_uri(
        f"/certificates/verify/{certificate.certificate_id}/"
    )


    qr = qrcode.make(qr_data)


    qr_buffer = BytesIO()

    qr.save(
        qr_buffer,
        format="PNG"
    )

    qr_buffer.seek(0)


    qr_image = Image(
        qr_buffer,
        width=100,
        height=100,
    )


    buffer = BytesIO()


    doc = SimpleDocTemplate(
    buffer,
    pagesize=landscape(A4)
)


    styles = getSampleStyleSheet()


    title = ParagraphStyle(
    "CertificateTitle",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontSize=32,
    textColor=darkblue,
)
    title.alignment = TA_CENTER


    heading = styles["Heading2"]
    heading.alignment = TA_CENTER


    normal = styles["BodyText"]
    normal.alignment = TA_CENTER


    story = []
    
    
    
    story.append(
    Spacer(1,80)
    )


    story.append(
        Paragraph(
            f"Certificate Number: <b>{certificate.certificate_number}</b>",
            normal
        )
    )


    story.append(
        Paragraph(
            f"Issued Date: {certificate.issued_at.strftime('%d %B %Y')}",
            normal
        )
    )


    story.append(
        Spacer(1,20)
    )


    story.append(
        Paragraph(
            "Verify this certificate online using the QR code.",
            normal
        )
    )




    story.append(
        Spacer(1,20)
    )


    story.append(
        Paragraph(
            "Certificate of Completion",
            title
        )
    )


    story.append(
        Spacer(1,40)
    )


    story.append(
        Paragraph(
            f"""
            This certifies that 
            <b>
            {request.user.get_full_name() or request.user.username}
            </b>
            """,
            heading
        )
    )


    story.append(
        Spacer(1,30)
    )


    story.append(
        Paragraph(
            "has successfully completed",
            normal
        )
    )


    story.append(
        Spacer(1,20)
    )


    story.append(
        Paragraph(
            f"<b>{course.title}</b>",
            heading
        )
    )


    story.append(
        Spacer(1,40)
    )


    story.append(
        Paragraph(
            f"""
            Certificate Number:
            <b>{certificate.certificate_number}</b>
            """,
            normal
        )
    )


    story.append(
        Spacer(1,20)
    )


    story.append(
    Paragraph(
        f"""
        Certificate ID:
        <b>{certificate.certificate_id}</b>
        """,
        normal
    )
   )


    story.append(
        Spacer(1,30)
    )


    story.append(
        qr_image
    )


    story.append(
        Spacer(1,10)
    )


    story.append(
            Paragraph(
                "Scan to Verify Certificate",
                normal
            )
        )
    
    story.append(
    Spacer(1,30)
   )


    story.append(
        Paragraph(
            f"""
            Issued Date:
            <b>
            {certificate.issued_at.strftime("%B %d, %Y")}
            </b>
            """,
            normal
        )
    )



    doc.build(
    story,
    onFirstPage=add_certificate_images,
    onLaterPages=add_certificate_images
)


    pdf = buffer.getvalue()
        
        
    from apps.certificates.utils import send_certificate_email



    send_certificate_email(

        request.user,

        certificate,

        pdf

    )


    buffer.close()


    response = HttpResponse(
        pdf,
        content_type="application/pdf"
    )


    response["Content-Disposition"] = (
        f'attachment; filename="{course.title}_certificate.pdf"'
    )


    return response
 
    
@login_required
def my_courses(request):

    if request.user.role != "student":
        messages.error(request, "Only students can access this page.")
        return redirect("courses:course_list")

    query  = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    enrollments = Enrollment.objects.filter(
        student=request.user
    ).select_related("course")

    if query:
        enrollments = enrollments.filter(course__title__icontains=query)
    if status:
        enrollments = enrollments.filter(status=status)

    progress_records = CourseProgress.objects.filter(student=request.user)

    progress_map = {p.course_id: p for p in progress_records}

    total_courses     = Enrollment.objects.filter(student=request.user).count()
    completed_courses = progress_records.filter(progress=100).count()

    average_progress = (
        sum(p.progress for p in progress_records) / total_courses
        if total_courses > 0 else 0
    )

    return render(request, "courses/my_courses.html", {
        "enrollments":      enrollments,
        "progress_map":     progress_map,
        "total_courses":    total_courses,
        "completed_courses": completed_courses,
        "average_progress": round(average_progress, 1),
        "query":  query,
        "status": status,
    })
    
    

@login_required
def course_create(request):

    if not _is_teacher_or_admin(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            # If teacher is creating, auto-set themselves as teacher
            if request.user.role == "teacher":
                course.teacher = request.user
            course.save()

            messages.success(request, "Course created successfully.")
            return redirect("courses:course_list")

    else:
        form = CourseForm(user=request.user)
        # Pre-select teacher field for teachers
        if request.user.role == "teacher":
            form.fields["teacher"].initial = request.user
            form.fields["teacher"].widget.attrs["readonly"] = True

    return render(request, "courses/course_create.html", {"form": form})


@login_required
def course_update(request, pk):

    course = get_object_or_404(Course, pk=pk)

    if not has_course_access(request.user, course):
        messages.error(request, "You are not allowed to edit this course.")
        return redirect("courses:course_detail", pk=course.pk)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully.")
            return redirect("courses:course_detail", pk=course.pk)

    else:
        form = CourseForm(instance=course, user=request.user)

    return render(request, "courses/course_update.html", {
        "form": form,
        "course": course,
    })


@login_required
def course_delete(request, pk):

    course = get_object_or_404(Course, pk=pk)

    # Check if user has access to this course
    if not has_course_access(request.user, course):
        messages.error(request, "You are not allowed to delete this course.")
        return redirect("courses:course_detail", pk=course.pk)

    if request.method == "POST":
        course.delete()

        messages.success(
            request,
            "Course deleted successfully."
        )

        return redirect("courses:course_list")

    return render(
        request,
        "courses/course_delete.html",
        {
            "course": course
        }
    )