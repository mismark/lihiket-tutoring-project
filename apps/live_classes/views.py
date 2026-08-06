from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.lessons.models import Lesson
from .forms import LiveClassForm
from .models import LiveClass


@login_required
def ajax_load_lessons(request):
    """Return lessons for a given course_id as JSON — used by the create/update form."""
    course_id = request.GET.get("course_id", "")
    lessons   = Lesson.objects.filter(
        course_id=course_id,
        status="published",
    ).order_by("lesson_order", "title").values("id", "title")
    return JsonResponse(list(lessons), safe=False)


@login_required
def live_class_list(request):
    search = request.GET.get("search", "").strip()

    live_classes = LiveClass.objects.select_related(
        "course", "lesson", "teacher",
    )

    if request.user.role == "teacher":
        live_classes = live_classes.filter(teacher=request.user)
    elif request.user.role == "student":
        from apps.courses.models import Enrollment
        enrolled_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list("course_id", flat=True)
        live_classes = live_classes.filter(course_id__in=enrolled_ids)

    if search:
        live_classes = live_classes.filter(
            Q(title__icontains=search) |
            Q(course__title__icontains=search) |
            Q(teacher__username__icontains=search)
        )

    # Auto-sync status for all non-cancelled classes
    for lc in live_classes:
        lc.sync_status()

    # Re-fetch after sync so template gets fresh status
    live_classes = live_classes.all()

    return render(request, "live_classes/live_class_list.html", {
        "live_classes": live_classes,
        "search":       search,
    })


@login_required
def live_class_detail(request, pk):
    live_class = get_object_or_404(LiveClass, pk=pk)

    # Sync status before displaying
    live_class.sync_status()

    return render(request, "live_classes/live_class_detail.html", {
        "live_class": live_class,
    })


@login_required
def live_class_create(request):

    if request.user.role not in ["admin", "teacher"]:

        messages.error(
            request,
            "You are not allowed to create live classes.",
        )

        return redirect(
            "live_classes:live_class_list",
        )

    if request.method == "POST":

        form = LiveClassForm(
            request.POST,
            request.FILES,
            user=request.user,
        )

        if form.is_valid():

            live_class = form.save(
                commit=False,
            )

            if request.user.role == "teacher":

                live_class.teacher = request.user

            live_class.save()

            messages.success(
                request,
                "Live class created successfully.",
            )

            return redirect(
                "live_classes:live_class_detail",
                live_class.pk,
            )

    else:

        form = LiveClassForm(
            user=request.user,
        )

    return render(
        request,
        "live_classes/live_class_create.html",
        {
            "form": form,
        },
    )


@login_required
def live_class_update(request, pk):

    live_class = get_object_or_404(
        LiveClass,
        pk=pk,
    )

    if request.user.role == "teacher":

        if live_class.teacher != request.user:

            messages.error(
                request,
                "You cannot edit this live class.",
            )

            return redirect(
                "live_classes:my_live_classes",
            )

    elif request.user.role != "admin":

        return redirect(
            "live_classes:live_class_list",
        )

    if request.method == "POST":

        form = LiveClassForm(
            request.POST,
            request.FILES,
            instance=live_class,
            user=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Live class updated successfully.",
            )

            return redirect(
                "live_classes:live_class_detail",
                live_class.pk,
            )

    else:

        form = LiveClassForm(
            instance=live_class,
            user=request.user,
        )

    return render(
        request,
        "live_classes/live_class_update.html",
        {
            "form": form,
            "live_class": live_class,
        },
    )


@login_required
def live_class_delete(request, pk):

    live_class = get_object_or_404(
        LiveClass,
        pk=pk,
    )

    if request.user.role == "teacher":

        if live_class.teacher != request.user:

            messages.error(
                request,
                "You cannot delete this live class.",
            )

            return redirect(
                "live_classes:my_live_classes",
            )

    elif request.user.role != "admin":

        return redirect(
            "live_classes:live_class_list",
        )

    if request.method == "POST":

        live_class.delete()

        messages.success(
            request,
            "Live class deleted successfully.",
        )

        return redirect(
            "live_classes:live_class_list",
        )

    return render(
        request,
        "live_classes/live_class_delete.html",
        {
            "live_class": live_class,
        },
    )


@login_required
def my_live_classes(request):

    if request.user.role == "teacher":

        live_classes = LiveClass.objects.filter(
            teacher=request.user,
        )

    elif request.user.role == "admin":

        live_classes = LiveClass.objects.all()

    else:

        live_classes = LiveClass.objects.none()

    return render(
        request,
        "live_classes/my_live_classes.html",
        {
            "live_classes": live_classes,
        },
    )


@login_required
def upcoming_classes(request):

    live_classes = LiveClass.objects.filter(

        start_datetime__gte=timezone.now(),

        status="upcoming",

    ).order_by(
        "start_datetime",
    )

    return render(
        request,
        "live_classes/upcoming_classes.html",
        {
            "live_classes": live_classes,
        },
    )


@login_required
def join_live_class(request, pk):

    live_class = get_object_or_404(
        LiveClass,
        pk=pk,
    )

    if live_class.status == "cancelled":

        messages.error(
            request,
            "This live class has been cancelled.",
        )

        return redirect(
            "live_classes:live_class_detail",
            live_class.pk,
        )

    return redirect(
        live_class.meeting_link,
    )