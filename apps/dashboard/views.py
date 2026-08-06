from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from apps.accounts.models import User
from apps.subjects.models import Subject
from apps.courses.models import Course, Enrollment, CourseProgress


@login_required
def global_search(request):
    q = request.GET.get("q", "").strip()
    results = {}

    if q and len(q) >= 2:
        from apps.lessons.models import Lesson
        from apps.documents.models import Document
        from apps.live_classes.models import LiveClass
        from django.db.models import Q

        results["courses"] = Course.objects.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        ).select_related("teacher", "subject")[:8]

        results["subjects"] = Subject.objects.filter(
            Q(name__icontains=q)
        )[:6]

        results["lessons"] = Lesson.objects.filter(
            Q(title__icontains=q), status="published"
        ).select_related("course")[:6]

        results["documents"] = Document.objects.filter(
            Q(title__icontains=q) | Q(description__icontains=q),
            visibility__in=["public", "students"],
        )[:6]

        results["live_classes"] = LiveClass.objects.filter(
            Q(title__icontains=q)
        ).select_related("course", "teacher")[:5]

        results["total"] = sum(r.count() for r in results.values())

    return render(request, "dashboard/search_results.html", {
        "q":       q,
        "results": results,
    })


@login_required
def ajax_search(request):
    """Returns JSON for the live navbar dropdown."""
    q = request.GET.get("q", "").strip()
    data = {"results": [], "q": q}

    if q and len(q) >= 2:
        from apps.lessons.models import Lesson
        from apps.live_classes.models import LiveClass
        from django.db.models import Q

        items = []

        for c in Course.objects.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        ).select_related("teacher")[:4]:
            items.append({
                "type": "Course",
                "icon": "fas fa-book-open",
                "color": "#667eea",
                "title": c.title,
                "sub": c.teacher.get_full_name() or c.teacher.username,
                "url": f"/courses/{c.pk}/",
            })

        for s in Subject.objects.filter(name__icontains=q)[:3]:
            items.append({
                "type": "Subject",
                "icon": "fas fa-book",
                "color": "#43e97b",
                "title": s.name,
                "sub": s.get_grade_level_display(),
                "url": f"/subjects/{s.slug}/",
            })

        for l in Lesson.objects.filter(
            Q(title__icontains=q), status="published"
        ).select_related("course")[:3]:
            items.append({
                "type": "Lesson",
                "icon": "fas fa-play-circle",
                "color": "#4facfe",
                "title": l.title,
                "sub": l.course.title,
                "url": f"/lessons/{l.slug}/",
            })

        for lc in LiveClass.objects.filter(
            Q(title__icontains=q)
        ).select_related("course")[:2]:
            items.append({
                "type": "Live Class",
                "icon": "fas fa-video",
                "color": "#f5576c",
                "title": lc.title,
                "sub": lc.course.title,
                "url": f"/live-classes/{lc.pk}/",
            })

        data["results"] = items
        data["total"]   = len(items)

    return JsonResponse(data)


@login_required
def home(request):
    user = request.user

    # ── ADMIN ─────────────────────────────────────────────────────
    if user.role == "admin" or user.is_superuser:
        from apps.assignments.models import Assignment
        from apps.live_classes.models import LiveClass

        live_classes = LiveClass.objects.select_related("course", "teacher")
        live_now  = [lc for lc in live_classes if lc.status == "live"]
        upcoming  = [lc for lc in live_classes if lc.status == "upcoming"][:5]

        return render(request, "dashboard/admin_dashboard.html", {
            "total_students":    User.objects.filter(role="student").count(),
            "total_teachers":    User.objects.filter(role="teacher").count(),
            "total_parents":     User.objects.filter(role="parent").count(),
            "total_courses":     Course.objects.count(),
            "published_courses": Course.objects.filter(status="published").count(),
            "draft_courses":     Course.objects.filter(status="draft").count(),
            "total_subjects":    Subject.objects.count(),
            "total_enrollments": Enrollment.objects.count(),
            "recent_users":      User.objects.order_by("-date_joined")[:6],
            "recent_courses":    Course.objects.select_related("teacher").order_by("-created_at")[:5],
            "live_now":          live_now,
            "upcoming_classes":  upcoming,
        })

    # ── TEACHER ───────────────────────────────────────────────────
    elif user.role == "teacher":
        from apps.assignments.models import Assignment, AssignmentSubmission
        from apps.live_classes.models import LiveClass
        from apps.lessons.models import Lesson

        my_courses      = Course.objects.filter(teacher=user).select_related("subject")
        enrolled_count  = Enrollment.objects.filter(course__teacher=user).count()
        pending_subs    = AssignmentSubmission.objects.filter(
            assignment__created_by=user, status="submitted"
        ).select_related("student", "assignment")[:5]

        live_classes    = LiveClass.objects.filter(teacher=user).select_related("course")
        live_now        = [lc for lc in live_classes if lc.status == "live"]
        upcoming        = [lc for lc in live_classes if lc.status == "upcoming"][:3]

        recent_lessons  = Lesson.objects.filter(
            course__teacher=user
        ).select_related("course").order_by("-created_at")[:5]

        return render(request, "dashboard/teacher_dashboard.html", {
            "my_courses":        my_courses,
            "total_courses":     my_courses.count(),
            "enrolled_count":    enrolled_count,
            "pending_subs":      pending_subs,
            "pending_count":     pending_subs.count(),
            "live_now":          live_now,
            "upcoming":          upcoming,
            "recent_lessons":    recent_lessons,
        })

    # ── STUDENT ───────────────────────────────────────────────────
    elif user.role == "student":
        from apps.assignments.models import Assignment, AssignmentSubmission
        from apps.live_classes.models import LiveClass
        from apps.certificates.models import Certificate

        enrollments     = Enrollment.objects.filter(student=user).select_related("course")
        progress_recs   = CourseProgress.objects.filter(student=user)
        progress_map    = {p.course_id: p.progress for p in progress_recs}

        avg_progress    = (
            sum(progress_map.values()) / len(progress_map)
            if progress_map else 0
        )

        submitted_count = AssignmentSubmission.objects.filter(student=user).count()
        graded_count    = AssignmentSubmission.objects.filter(
            student=user, status="graded"
        ).count()
        cert_count      = Certificate.objects.filter(student=user).count()

        live_classes    = LiveClass.objects.filter(
            course__in=enrollments.values("course")
        ).select_related("course", "teacher")
        live_now        = [lc for lc in live_classes if lc.status == "live"]
        upcoming        = [lc for lc in live_classes if lc.status == "upcoming"][:3]

        for e in enrollments:
            e.progress = progress_map.get(e.course_id, 0)

        return render(request, "dashboard/student_dashboard.html", {
            "enrollments":       enrollments[:6],
            "enrolled_count":    enrollments.count(),
            "avg_progress":      round(avg_progress, 1),
            "submitted_count":   submitted_count,
            "graded_count":      graded_count,
            "cert_count":        cert_count,
            "live_now":          live_now,
            "upcoming":          upcoming,
        })

    # ── PARENT / OTHER ────────────────────────────────────────────
    else:
        return render(request, "dashboard/parent_dashboard.html", {})
