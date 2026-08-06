from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.constants import GRADE_LEVEL_CHOICES
from .forms import SubjectForm
from .models import Subject


def _is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.role == "admin"
    )


def _get_subjects_for_user(user):
    """
    Return the correct queryset based on who is logged in:
    - Admin / Superuser  → all subjects
    - Teacher            → only subjects assigned to them
    - Student            → only subjects matching their grade_level
    - Parent / other     → all subjects (read-only view)
    """
    if user.is_superuser or user.role == "admin":
        return Subject.objects.all()

    if user.role == "teacher":
        return Subject.objects.filter(teachers=user)

    if user.role == "student":
        if user.grade_level:
            return Subject.objects.filter(grade_level=user.grade_level)
        return Subject.objects.none()

    # parent or any other role — show all as read-only
    return Subject.objects.all()


@login_required
def subject_list(request):
    search = request.GET.get("search", "").strip()
    grade_filter = request.GET.get("grade", "").strip()

    subjects = _get_subjects_for_user(request.user)

    if search:
        subjects = subjects.filter(name__icontains=search)

    # Grade filter only available to admin (students are already filtered by grade)
    if grade_filter and _is_admin(request.user):
        subjects = subjects.filter(grade_level=grade_filter)

    paginator = Paginator(subjects, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "subjects/subject_list.html", {
        "subjects": page_obj,
        "page_obj": page_obj,
        "search": search,
        "grade_filter": grade_filter,
        "grade_level_choices": GRADE_LEVEL_CHOICES[1:],
        "total_subjects": subjects.count(),
        "user_is_admin": _is_admin(request.user),
    })


@login_required
def subject_detail(request, slug):
    subject = get_object_or_404(Subject, slug=slug)

    # Teachers can only view their assigned subjects
    if request.user.role == "teacher":
        if not subject.teachers.filter(pk=request.user.pk).exists():
            raise PermissionDenied

    # Students can only view subjects matching their grade
    if request.user.role == "student":
        if not request.user.grade_level or subject.grade_level != request.user.grade_level:
            raise PermissionDenied

    # Courses under this subject
    from apps.courses.models import Course, Enrollment
    courses = Course.objects.filter(subject=subject).select_related("teacher").order_by("-created_at")

    # For students — only published, and mark enrolled ones
    enrolled_course_ids = set()
    if request.user.role == "student":
        courses = courses.filter(status="published")
        enrolled_course_ids = set(
            Enrollment.objects.filter(student=request.user)
            .values_list("course_id", flat=True)
        )

    return render(request, "subjects/subject_detail.html", {
        "subject": subject,
        "user_is_admin": _is_admin(request.user),
        "courses": courses,
        "enrolled_course_ids": enrolled_course_ids,
        "is_teacher": request.user.role == "teacher",
    })


@login_required
def subject_create(request):
    """Only admins can create subjects."""
    if not _is_admin(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = SubjectForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.save()
            form.save_m2m()
            messages.success(request, f'Subject "{subject}" created successfully.')
            return redirect("subjects:subject_list")
    else:
        form = SubjectForm()

    return render(request, "subjects/subject_create.html", {
        "form": form,
        "title": "Create Subject",
        "user_is_admin": True,
    })


@login_required
def subject_update(request, slug):
    """Only admins can update subjects."""
    subject = get_object_or_404(Subject, slug=slug)

    if not _is_admin(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = SubjectForm(request.POST, request.FILES, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subject "{subject}" updated successfully.')
            return redirect("subjects:subject_detail", slug=subject.slug)
    else:
        form = SubjectForm(instance=subject)

    return render(request, "subjects/subject_update.html", {
        "form": form,
        "subject": subject,
        "title": "Update Subject",
        "user_is_admin": True,
    })


@login_required
def subject_delete(request, slug):
    """Only admins can delete subjects."""
    subject = get_object_or_404(Subject, slug=slug)

    if not _is_admin(request.user):
        raise PermissionDenied

    if request.method == "POST":
        name = str(subject)
        subject.delete()
        messages.success(request, f'Subject "{name}" deleted successfully.')
        return redirect("subjects:subject_list")

    return render(request, "subjects/subject_delete.html", {
        "subject": subject,
        "user_is_admin": True,
    })
