"""
Management command: auto_reject_overdue

Finds all active assignments whose due date has passed and auto-creates
a rejected submission (marks=0, grade=F) for every enrolled student
who has not submitted.

Usage:
    python manage.py auto_reject_overdue

Schedule via Windows Task Scheduler or cron to run every hour:
    # Windows Task Scheduler: run every hour
    # Action: python manage.py auto_reject_overdue
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.assignments.models import Assignment


class Command(BaseCommand):
    help = "Auto-reject overdue assignments for students who did not submit."

    def handle(self, *args, **options):
        now = timezone.now()

        overdue = Assignment.objects.filter(
            is_active=True,
            due_date__lt=now,
        )

        total_rejected = 0
        for assignment in overdue:
            count = assignment.auto_reject_missing_submissions()
            if count:
                self.stdout.write(
                    f"  Rejected {count} submission(s) for: {assignment.title}"
                )
                total_rejected += count

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {total_rejected} submission(s) auto-rejected across "
                f"{overdue.count()} overdue assignments."
            )
        )
