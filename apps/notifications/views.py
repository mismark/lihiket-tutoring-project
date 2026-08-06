from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


# ── Icon/color config for each notification type ──────────────────
TYPE_CONFIG = {
    "course_enrollment": {"icon": "fas fa-user-plus",      "bg": "#f0f2ff", "color": "#667eea"},
    "assignment":        {"icon": "fas fa-tasks",           "bg": "#fff8f0", "color": "#f7971e"},
    "quiz":              {"icon": "fas fa-question-circle", "bg": "#f0f2ff", "color": "#667eea"},
    "exam":              {"icon": "fas fa-file-alt",        "bg": "#fff1f2", "color": "#f5576c"},
    "live_class":        {"icon": "fas fa-video",           "bg": "#f0fff4", "color": "#43e97b"},
    "certificate":       {"icon": "fas fa-certificate",    "bg": "#fff8f0", "color": "#f7971e"},
    "message":           {"icon": "fas fa-comment",         "bg": "#f0f2ff", "color": "#667eea"},
    "system":            {"icon": "fas fa-bell",            "bg": "#f0f2ff", "color": "#667eea"},
    "payment":           {"icon": "fas fa-credit-card",    "bg": "#f0fff4", "color": "#43e97b"},
}


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")

    unread_count = notifications.filter(is_read=False).count()

    # Mark all as read when page is opened
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, "notifications/notification_list.html", {
        "notifications": notifications,
        "unread_count":  unread_count,
    })


@login_required
@require_POST
def mark_as_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.is_read = True
    notif.save()
    link = notif.link
    if link and link.startswith("/"):
        return redirect(link)
    return redirect("notifications:notification_list")


@login_required
@require_POST
def mark_all_as_read(request):
    Notification.objects.filter(
        recipient=request.user, is_read=False
    ).update(is_read=True)
    return redirect("notifications:notification_list")


@login_required
@require_POST
def delete_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.delete()
    return redirect("notifications:notification_list")


@login_required
@require_POST
def delete_all(request):
    Notification.objects.filter(recipient=request.user).delete()
    return redirect("notifications:notification_list")


@login_required
def unread_count(request):
    """AJAX — returns unread count for navbar badge. Auto-refreshed every 30s."""
    count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()
    return JsonResponse({"count": count})


@login_required
def recent_notifications(request):
    """AJAX — returns last 5 notifications for the navbar dropdown."""
    notifs = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")[:5]

    data = []
    for n in notifs:
        cfg = TYPE_CONFIG.get(n.notification_type, TYPE_CONFIG["system"])
        data.append({
            "pk":      n.pk,
            "title":   n.title,
            "message": n.message[:90] + ("…" if len(n.message) > 90 else ""),
            "type":    n.notification_type,
            "icon":    cfg["icon"],
            "bg":      cfg["bg"],
            "color":   cfg["color"],
            "is_read": n.is_read,
            "link":    n.link or "",
            "time":    n.created_at.strftime("%b %d, %H:%M"),
        })

    unread = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    return JsonResponse({"notifications": data, "unread": unread})
