from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("",                            views.notification_list,   name="notification_list"),
    path("mark-all-read/",              views.mark_all_as_read,    name="mark_all_as_read"),
    path("delete-all/",                 views.delete_all,          name="delete_all"),
    path("<int:pk>/mark-read/",         views.mark_as_read,        name="mark_as_read"),
    path("<int:pk>/delete/",            views.delete_notification, name="delete_notification"),
    path("ajax/unread-count/",          views.unread_count,        name="unread_count"),
    path("ajax/recent/",                views.recent_notifications,name="recent"),
]
