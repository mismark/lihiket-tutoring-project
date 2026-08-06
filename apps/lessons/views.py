from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.courses.models import Course, Enrollment
from .forms import LessonForm
from .models import Lesson


# ── Helpers ────────────────────────────────────────────────────────────────────

def _can_manage_lesson(user, lesson=None):
    """True if user may create / edit / delete lessons."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.role == "admin":
        return True
    if user.role == "teacher":
        if lesson is None:
            return True  # creating — course check happens in form validation
        return lesson.course.teacher == user
    return False


def _student_can_view_lesson(user, lesson):
    """
    Student can see a lesson if:
    - it is a free preview (any student, enrolled or not), OR
    - they are enrolled in the lesson's course.
    """
    if lesson.is_preview:
        return True
    return Enrollment.objects.filter(student=user, course=lesson.course).exists()


# ── Views ───────────────────────────────────────────────────────────────────────

@login_required
def lesson_list(request):
    search     = request.GET.get("search", "").strip()
    course_id  = request.GET.get("course", "").strip()

    if request.user.role == "teacher":
        lessons = Lesson.objects.filter(
            course__teacher=request.user
        ).select_related("course", "course__teacher")

    elif request.user.role == "student":
        # Students see only published lessons for courses they are enrolled in,
        # plus any free-preview published lessons
        enrolled_course_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list("course_id", flat=True)
        lessons = Lesson.objects.filter(
            status="published",
        ).filter(
            course_id__in=enrolled_course_ids
        ).select_related("course")

    elif request.user.role == "admin" or request.user.is_superuser:
        lessons = Lesson.objects.select_related("course", "course__teacher")

    else:
        # Parent — only preview published lessons
        lessons = Lesson.objects.filter(
            status="published", is_preview=True
        ).select_related("course")

    if search:
        lessons = lessons.filter(title__icontains=search)

    if course_id:
        lessons = lessons.filter(course_id=course_id)

    # Build course filter options
    if request.user.role == "teacher":
        courses = Course.objects.filter(teacher=request.user).order_by("title")
    elif request.user.role == "student":
        enrolled_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list("course_id", flat=True)
        courses = Course.objects.filter(pk__in=enrolled_ids).order_by("title")
    else:
        courses = Course.objects.all().order_by("title")

    paginator = Paginator(lessons, 10)
    page_obj  = paginator.get_page(request.GET.get("page"))

    return render(request, "lessons/lesson_list.html", {
        "page_obj":  page_obj,
        "search":    search,
        "course_id": course_id,
        "courses":   courses,
        "can_create": _can_manage_lesson(request.user),
    })


@login_required
def lesson_detail(request, slug):
    lesson = get_object_or_404(
        Lesson.objects.select_related("course", "course__teacher"),
        slug=slug,
    )

    # Permission checks
    if request.user.role == "student":
        if not _student_can_view_lesson(request.user, lesson):
            messages.error(
                request,
                "You must be enrolled in this course to view this lesson."
            )
            return redirect("courses:course_detail", pk=lesson.course.pk)

    elif request.user.role == "teacher":
        if lesson.course.teacher != request.user:
            raise PermissionDenied

    # Documents attached to this lesson (for enrolled students and teachers)
    lesson_documents = []
    is_enrolled = False
    if request.user.role == "student":
        is_enrolled = Enrollment.objects.filter(
            student=request.user, course=lesson.course
        ).exists()
        if is_enrolled or lesson.is_preview:
            from apps.documents.models import Document
            lesson_documents = Document.objects.filter(
                lesson=lesson,
                visibility__in=["public", "students"],
            ).order_by("-created_at")

    elif _can_manage_lesson(request.user, lesson):
        from apps.documents.models import Document
        lesson_documents = Document.objects.filter(lesson=lesson).order_by("-created_at")

    # Other lessons in this course (for navigation sidebar)
    course_lessons = Lesson.objects.filter(
        course=lesson.course,
        status="published",
    ).order_by("lesson_order")

    if request.user.role == "student":
        # Only include lessons the student can see
        enrolled = Enrollment.objects.filter(
            student=request.user, course=lesson.course
        ).exists()
        if not enrolled:
            course_lessons = course_lessons.filter(is_preview=True)

    return render(request, "lessons/lesson_detail.html", {
        "lesson":           lesson,
        "lesson_documents": lesson_documents,
        "course_lessons":   course_lessons,
        "is_enrolled":      is_enrolled,
        "can_manage":       _can_manage_lesson(request.user, lesson),
    })


@login_required
def lesson_create(request):
    if not _can_manage_lesson(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            lesson = form.save()
            messages.success(request, f'Lesson "{lesson.title}" created successfully.')
            return redirect("lessons:lesson_detail", slug=lesson.slug)
    else:
        form = LessonForm(user=request.user)

    return render(request, "lessons/lesson_create.html", {"form": form})


@login_required
def lesson_update(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)

    if not _can_manage_lesson(request.user, lesson):
        messages.error(request, "You can only edit your own lessons.")
        return redirect("lessons:lesson_list")

    if request.method == "POST":
        form = LessonForm(request.POST, request.FILES, instance=lesson, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully.")
            return redirect("lessons:lesson_detail", slug=lesson.slug)
    else:
        form = LessonForm(instance=lesson, user=request.user)

    return render(request, "lessons/lesson_update.html", {
        "form":   form,
        "lesson": lesson,
    })


@login_required
def lesson_delete(request, slug):
    lesson = get_object_or_404(Lesson, slug=slug)

    if not _can_manage_lesson(request.user, lesson):
        messages.error(request, "You can only delete your own lessons.")
        return redirect("lessons:lesson_list")

    if request.method == "POST":
        course_pk = lesson.course.pk
        lesson.delete()
        messages.success(request, "Lesson deleted successfully.")
        return redirect("courses:course_detail", pk=course_pk)

    return render(request, "lessons/lesson_delete.html", {"lesson": lesson})


@login_required
def my_lessons(request):
    if request.user.role == "admin" or request.user.is_superuser:
        lessons = Lesson.objects.select_related("course").all()
    elif request.user.role == "teacher":
        lessons = Lesson.objects.filter(
            course__teacher=request.user
        ).select_related("course")
    else:
        raise PermissionDenied

    published_count = lessons.filter(status="published").count()
    draft_count     = lessons.filter(status="draft").count()
    preview_count   = lessons.filter(is_preview=True).count()

    return render(request, "lessons/my_lessons.html", {
        "lessons":         lessons,
        "published_count": published_count,
        "draft_count":     draft_count,
        "preview_count":   preview_count,
    })


@login_required
def lesson_preview(request, slug):
    """Preview a lesson — available to all logged-in users."""
    lesson = get_object_or_404(
        Lesson.objects.select_related("course"),
        slug=slug,
        is_preview=True,
        status="published",
    )
    return render(request, "lessons/lesson_detail.html", {
        "lesson":           lesson,
        "lesson_documents": [],
        "course_lessons":   [],
        "is_enrolled":      False,
        "can_manage":       _can_manage_lesson(request.user, lesson),
    })
