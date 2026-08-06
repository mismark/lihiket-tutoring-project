from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.courses.models import Course, Enrollment
from apps.lessons.models import Lesson
from .forms import DocumentForm
from .models import Document


# ── Helpers ────────────────────────────────────────────────────────────────────

def _can_manage_document(user, document=None):
    """True if user can create/edit/delete documents (teacher for own, admin for all)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.role == "admin":
        return True
    if user.role == "teacher":
        if document is None:
            return True  # creating
        return document.teacher == user
    return False


def _student_can_see(user, document):
    """True if a student is allowed to read/download this document."""
    if document.visibility == "public":
        return True
    if document.visibility == "students":
        # Must be enrolled in the document's course
        return Enrollment.objects.filter(
            student=user, course=document.course
        ).exists()
    return False


def _get_documents_for_user(user):
    """Return scoped Document queryset based on role."""
    qs = Document.objects.select_related("subject", "course", "lesson", "teacher")

    if user.is_superuser or user.role == "admin":
        return qs

    if user.role == "teacher":
        # Own documents + public ones from other teachers in same subjects
        return qs.filter(
            Q(teacher=user) |
            Q(visibility="public")
        ).distinct()

    if user.role == "student":
        # Enrolled course IDs for this student
        enrolled_course_ids = Enrollment.objects.filter(
            student=user
        ).values_list("course_id", flat=True)

        return qs.filter(
            Q(visibility="public") |
            Q(visibility="students", course_id__in=enrolled_course_ids)
        ).distinct()

    # Parent — public only
    return qs.filter(visibility="public")


# ── Views ───────────────────────────────────────────────────────────────────────

@login_required
def document_list(request):
    search = request.GET.get("search", "").strip()
    subject_id = request.GET.get("subject", "").strip()
    course_id  = request.GET.get("course", "").strip()

    documents = _get_documents_for_user(request.user)

    if search:
        documents = documents.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(course__title__icontains=search) |
            Q(subject__name__icontains=search)
        )

    if subject_id:
        documents = documents.filter(subject_id=subject_id)

    if course_id:
        documents = documents.filter(course_id=course_id)

    # Build filter options
    if request.user.role == "teacher":
        from apps.subjects.models import Subject
        subjects = Subject.objects.filter(teachers=request.user, is_active=True)
        courses  = Course.objects.filter(teacher=request.user)
    elif request.user.role == "student":
        enrolled_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list("course_id", flat=True)
        courses  = Course.objects.filter(pk__in=enrolled_ids)
        from apps.subjects.models import Subject
        subjects = Subject.objects.filter(
            grade_level=request.user.grade_level, is_active=True
        ) if request.user.grade_level else Subject.objects.none()
    else:
        from apps.subjects.models import Subject
        subjects = Subject.objects.filter(is_active=True)
        courses  = Course.objects.all()

    return render(request, "documents/document_list.html", {
        "documents":    documents,
        "search":       search,
        "subject_id":   subject_id,
        "course_id":    course_id,
        "subjects":     subjects,
        "courses":      courses,
        "can_upload":   _can_manage_document(request.user),
    })


@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Permission check
    if request.user.role == "student":
        if not _student_can_see(request.user, document):
            raise Http404()

    elif request.user.role == "teacher":
        if document.visibility == "private" and document.teacher != request.user:
            raise Http404()

    return render(request, "documents/document_detail.html", {
        "document":    document,
        "can_manage":  _can_manage_document(request.user, document),
    })


@login_required
def document_create(request):
    if not _can_manage_document(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            document = form.save(commit=False)
            # Teacher is always the logged-in teacher
            if request.user.role == "teacher":
                document.teacher = request.user
            elif not document.teacher_id:
                # Admin creating without specifying — use course teacher
                document.teacher = document.course.teacher
            document.save()

            messages.success(request, "Document uploaded successfully.")
            return redirect("documents:document_list")

    else:
        form = DocumentForm(user=request.user)

    return render(request, "documents/document_create.html", {"form": form})


@login_required
def document_update(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if not _can_manage_document(request.user, document):
        messages.error(request, "You do not have permission to edit this document.")
        return redirect("documents:document_list")

    if request.method == "POST":
        form = DocumentForm(
            request.POST, request.FILES,
            instance=document, user=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Document updated successfully.")
            return redirect("documents:document_detail", pk=document.pk)

    else:
        form = DocumentForm(instance=document, user=request.user)

    return render(request, "documents/document_update.html", {
        "form":     form,
        "document": document,
    })


@login_required
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)

    if not _can_manage_document(request.user, document):
        messages.error(request, "You do not have permission to delete this document.")
        return redirect("documents:document_list")

    if request.method == "POST":
        document.delete()
        messages.success(request, "Document deleted successfully.")
        return redirect("documents:my_documents")

    return render(request, "documents/document_delete.html", {"document": document})


@login_required
def my_documents(request):
    """
    Teacher — their own uploaded documents.
    Student — documents from courses they're enrolled in.
    Admin   — all documents.
    """
    if request.user.is_superuser or request.user.role == "admin":
        documents = Document.objects.all()
    elif request.user.role == "teacher":
        documents = Document.objects.filter(teacher=request.user)
    else:
        enrolled_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list("course_id", flat=True)
        documents = Document.objects.filter(
            Q(visibility="public") |
            Q(visibility="students", course_id__in=enrolled_ids)
        )

    return render(request, "documents/my_documents.html", {
        "documents": documents.select_related("subject", "course", "lesson", "teacher"),
    })


@login_required
def download_document(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Students: must be enrolled in the course
    if request.user.role == "student":
        if not _student_can_see(request.user, document):
            raise Http404()

    # Teachers: can only download their own private docs
    elif request.user.role == "teacher":
        if document.visibility == "private" and document.teacher != request.user:
            raise Http404()

    document.download_count += 1
    document.save(update_fields=["download_count"])

    return FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=document.file_name,
    )


# ── AJAX endpoints ─────────────────────────────────────────────────────────────

@login_required
def load_courses(request):
    """Return courses for a given subject, scoped to the current teacher."""
    subject_id = request.GET.get("subject")

    courses = Course.objects.filter(subject_id=subject_id).order_by("title")

    if request.user.role == "teacher":
        courses = courses.filter(teacher=request.user)

    data = [{"id": c.id, "title": c.title} for c in courses]
    return JsonResponse(data, safe=False)


@login_required
def load_lessons(request):
    """Return lessons for a given course."""
    course_id = request.GET.get("course")
    lessons   = Lesson.objects.filter(course_id=course_id).order_by("title")
    data      = [{"id": l.id, "title": l.title} for l in lessons]
    return JsonResponse(data, safe=False)
