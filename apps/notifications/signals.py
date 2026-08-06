"""
Notification signals — every teacher↔student interaction triggers a notification.

Events covered:
  Student receives:
    - Course created in their subject/grade
    - New lesson published in enrolled course
    - New document uploaded to enrolled course
    - Assignment created in enrolled course
    - Assignment graded
    - Assignment auto-rejected (past due)
    - Quiz created in enrolled course
    - Quiz result (after attempt)
    - Exam scheduled in enrolled course
    - Live class scheduled in enrolled course
    - Enrolled successfully
    - Certificate issued

  Teacher receives:
    - Student enrolled in their course
    - Student submitted assignment
    - Student completed a quiz
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import notify, notify_many


def _enrolled_students(course):
    """Return all students enrolled in a course."""
    from apps.courses.models import Enrollment
    return [
        e.student
        for e in Enrollment.objects.filter(course=course).select_related("student")
    ]


# ══ COURSE ════════════════════════════════════════════════════════

@receiver(post_save, sender="courses.Course")
def on_course_created(sender, instance, created, **kwargs):
    """Notify students in the same subject/grade that a new course is available."""
    if not created or instance.status != "published":
        return
    if not instance.subject:
        return

    from apps.accounts.models import User
    # Students whose grade matches the course subject's grade level
    students = User.objects.filter(
        role="student",
        grade_level=instance.subject.grade_level,
    )
    for student in students:
        notify(
            recipient=student,
            title="New Course Available",
            message=(
                f'A new course "{instance.title}" is now available '
                f'in {instance.subject.name} ({instance.subject.get_grade_level_display()}).'
            ),
            notification_type="course_enrollment",
            link=f"/courses/{instance.pk}/",
        )


@receiver(post_save, sender="courses.Enrollment")
def on_enrollment(sender, instance, created, **kwargs):
    """Student enrolled — notify student and teacher."""
    if not created:
        return
    student = instance.student
    course  = instance.course
    teacher = course.teacher

    notify(
        recipient=student,
        title="Enrolled Successfully",
        message=f'You are now enrolled in "{course.title}". Start learning!',
        notification_type="course_enrollment",
        link=f"/courses/{course.pk}/",
    )

    notify(
        recipient=teacher,
        title="New Student Enrolled",
        message=(
            f'{student.get_full_name() or student.username} enrolled in '
            f'"{course.title}".'
        ),
        notification_type="course_enrollment",
        link=f"/courses/{course.pk}/",
    )


# ══ LESSONS ═══════════════════════════════════════════════════════

@receiver(post_save, sender="lessons.Lesson")
def on_lesson(sender, instance, created, **kwargs):
    """Notify enrolled students when a new published lesson is added."""
    if not created or instance.status != "published":
        return

    students = _enrolled_students(instance.course)
    for student in students:
        notify(
            recipient=student,
            title="New Lesson Published",
            message=(
                f'A new lesson "{instance.title}" has been published '
                f'in "{instance.course.title}".'
            ),
            notification_type="course_enrollment",
            link=f"/lessons/{instance.slug}/",
        )


# ══ DOCUMENTS ═════════════════════════════════════════════════════

@receiver(post_save, sender="documents.Document")
def on_document(sender, instance, created, **kwargs):
    """Notify enrolled students when a document is uploaded to their course."""
    if not created:
        return
    if instance.visibility not in ("public", "students"):
        return

    students = _enrolled_students(instance.course)
    for student in students:
        notify(
            recipient=student,
            title="New Document Uploaded",
            message=(
                f'"{instance.title}" has been uploaded to '
                f'"{instance.course.title}". ({instance.file_extension.upper()})'
            ),
            notification_type="system",
            link=f"/documents/{instance.pk}/",
        )


# ══ ASSIGNMENTS ═══════════════════════════════════════════════════

@receiver(post_save, sender="assignments.Assignment")
def on_assignment_created(sender, instance, created, **kwargs):
    """Notify enrolled students when a new assignment is created."""
    if not created or not instance.is_active:
        return

    students = _enrolled_students(instance.course)
    for student in students:
        notify(
            recipient=student,
            title="New Assignment",
            message=(
                f'Assignment "{instance.title}" has been posted in '
                f'"{instance.course.title}". '
                f'Due: {instance.due_date.strftime("%B %d, %Y at %H:%M")}.'
            ),
            notification_type="assignment",
            link=f"/assignments/{instance.pk}/",
        )


@receiver(post_save, sender="assignments.AssignmentSubmission")
def on_submission_created(sender, instance, created, **kwargs):
    """Notify teacher when a student submits an assignment."""
    if not created:
        return

    teacher = instance.assignment.created_by
    student = instance.student
    notify(
        recipient=teacher,
        title="New Assignment Submission",
        message=(
            f'{student.get_full_name() or student.username} submitted '
            f'"{instance.assignment.title}".'
        ),
        notification_type="assignment",
        link=f"/assignments/{instance.assignment.pk}/",
    )


@receiver(post_save, sender="assignments.AssignmentSubmission")
def on_assignment_graded(sender, instance, created, **kwargs):
    """Notify student when their assignment is graded."""
    if created:
        return
    if instance.status == "graded" and instance.marks is not None:
        notify(
            recipient=instance.student,
            title="Assignment Graded ✅",
            message=(
                f'Your submission for "{instance.assignment.title}" has been graded. '
                f'Score: {instance.marks}/{instance.assignment.max_marks}'
                + (f' — Grade: {instance.grade}' if instance.grade else '')
                + ('.' if instance.feedback else '. No feedback provided.')
            ),
            notification_type="assignment",
            link=f"/assignments/submission/{instance.pk}/",
        )


@receiver(post_save, sender="assignments.AssignmentSubmission")
def on_assignment_rejected(sender, instance, created, **kwargs):
    """Notify student when their assignment is auto-rejected (past due)."""
    if created:
        return
    if instance.status == "rejected":
        notify(
            recipient=instance.student,
            title="Assignment Not Submitted — Rejected",
            message=(
                f'"{instance.assignment.title}" was not submitted before the deadline '
                f'and has been automatically rejected. Score: 0.'
            ),
            notification_type="assignment",
            link=f"/assignments/{instance.assignment.pk}/",
        )


# ══ QUIZZES ═══════════════════════════════════════════════════════

@receiver(post_save, sender="quizzes.Quiz")
def on_quiz_created(sender, instance, created, **kwargs):
    """Notify enrolled students when a new quiz is created."""
    if not created or not instance.is_active:
        return

    students = _enrolled_students(instance.course)
    for student in students:
        notify(
            recipient=student,
            title="New Quiz Available 📝",
            message=(
                f'A new quiz "{instance.title}" is available in '
                f'"{instance.course.title}". '
                f'Duration: {instance.duration} min.'
            ),
            notification_type="quiz",
            link=f"/quizzes/{instance.pk}/",
        )


@receiver(post_save, sender="quizzes.QuizAttempt")
def on_quiz_completed(sender, instance, created, **kwargs):
    """Notify student of their quiz result, notify teacher of completion."""
    if not instance.completed_at:
        return
    # Only fire once when completed_at is first set
    if created:
        return

    student = instance.student
    quiz    = instance.quiz

    notify(
        recipient=student,
        title=f"Quiz Result: {'Passed 🎉' if instance.passed else 'Failed'}",
        message=(
            f'You scored {instance.score}/{instance.total_marks} '
            f'({instance.percentage:.1f}%) on "{quiz.title}". '
            + ('Well done!' if instance.passed else f'You need {quiz.passing_score}% to pass.')
        ),
        notification_type="quiz",
        link=f"/quizzes/attempt/{instance.pk}/result/",
    )

    notify(
        recipient=quiz.created_by,
        title="Quiz Completed",
        message=(
            f'{student.get_full_name() or student.username} completed '
            f'"{quiz.title}" — score {instance.percentage:.1f}%.'
        ),
        notification_type="quiz",
        link=f"/quizzes/{quiz.pk}/results/",
    )


# ══ EXAMS ══════════════════════════════════════════════════════════

@receiver(post_save, sender="exams.Exam")
def on_exam_created(sender, instance, created, **kwargs):
    """Notify enrolled students when an exam is scheduled."""
    if not created or not instance.is_active:
        return

    students = _enrolled_students(instance.course)
    for student in students:
        notify(
            recipient=student,
            title="Exam Scheduled 📋",
            message=(
                f'Exam "{instance.title}" has been scheduled for '
                f'{instance.start_time.strftime("%B %d, %Y at %H:%M")} '
                f'in "{instance.course.title}". Duration: {instance.duration} min.'
            ),
            notification_type="exam",
            link=f"/exams/{instance.pk}/",
        )


@receiver(post_save, sender="exams.ExamAttempt")
def on_exam_completed(sender, instance, created, **kwargs):
    """Notify student of exam result, notify teacher."""
    if not instance.submitted_at:
        return
    if created:
        return

    student = instance.student
    exam    = instance.exam

    notify(
        recipient=student,
        title=f"Exam Result: {'Passed 🎉' if instance.passed else 'Failed'}",
        message=(
            f'You scored {instance.score}/{exam.total_marks} '
            f'({instance.percentage:.1f}%) on "{exam.title}". '
            + ('Congratulations!' if instance.passed else f'Pass mark: {exam.passing_score}%.')
        ),
        notification_type="exam",
        link=f"/exams/attempt/{instance.pk}/result/",
    )

    notify(
        recipient=exam.created_by,
        title="Exam Completed",
        message=(
            f'{student.get_full_name() or student.username} completed '
            f'"{exam.title}" — score {instance.percentage:.1f}%.'
        ),
        notification_type="exam",
        link=f"/exams/{exam.pk}/results/",
    )


# ══ LIVE CLASSES ══════════════════════════════════════════════════

@receiver(post_save, sender="live_classes.LiveClass")
def on_live_class_created(sender, instance, created, **kwargs):
    """Notify enrolled students when a live class is scheduled."""
    if not created:
        return

    students = _enrolled_students(instance.course)
    for student in students:
        notify(
            recipient=student,
            title="Live Class Scheduled 🎥",
            message=(
                f'"{instance.title}" live class is scheduled for '
                f'{instance.start_datetime.strftime("%B %d, %Y at %H:%M")} '
                f'in "{instance.course.title}". Platform: {instance.get_platform_display()}.'
            ),
            notification_type="live_class",
            link=f"/live-classes/{instance.pk}/",
        )


# ══ CERTIFICATES ══════════════════════════════════════════════════

@receiver(post_save, sender="certificates.Certificate")
def on_certificate_issued(sender, instance, created, **kwargs):
    """Notify student when a certificate is issued."""
    if not created:
        return
    notify(
        recipient=instance.student,
        title="Certificate Earned 🏆",
        message=(
            f'Congratulations! You have earned a certificate for completing '
            f'"{instance.course.title}".'
        ),
        notification_type="certificate",
        link=f"/courses/{instance.course.pk}/certificate/",
    )
