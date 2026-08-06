from .models import Notification


def notify(recipient, title, message, notification_type="system", link=""):
    """Create a single notification for a user."""
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link,
    )


def notify_many(recipients, title, message, notification_type="system", link=""):
    """Create the same notification for multiple users."""
    objs = [
        Notification(
            recipient=r,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
        )
        for r in recipients
    ]
    Notification.objects.bulk_create(objs)
