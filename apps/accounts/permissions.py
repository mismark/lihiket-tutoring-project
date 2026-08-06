from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import User


class IsAdminMixin:
    """Mixin to ensure only admin users can access the view."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class IsTeacherMixin:
    """Mixin to ensure only teacher users can access the view."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'teacher':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class IsStudentMixin:
    """Mixin to ensure only student users can access the view."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'student':
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class IsTeacherOrAdminMixin:
    """Mixin to ensure only teacher or admin users can access the view."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ['teacher', 'admin']:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class IsTeacherOrStudentMixin:
    """Mixin to ensure only teacher or student users can access the view."""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in ['teacher', 'student']:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def is_admin(user):
    """Check if user is admin."""
    return user.is_authenticated and user.role == 'admin'


def is_teacher(user):
    """Check if user is teacher."""
    return user.is_authenticated and user.role == 'teacher'


def is_student(user):
    """Check if user is student."""
    return user.is_authenticated and user.role == 'student'


def has_subject_access(user, subject):
    """
    Check if teacher has access to a subject.
    Admin has access to all subjects.
    """
    if is_admin(user):
        return True
    if is_teacher(user):
        return subject.teachers.filter(id=user.id).exists()
    return False


def has_course_access(user, course):
    """
    Check if teacher has access to a course.
    Admin has access to all courses.
    Teacher has access if they are assigned to the course's subject.
    """
    if is_admin(user):
        return True
    if is_teacher(user):
        return has_subject_access(user, course.subject)
    return False


def get_teacher_subjects(user):
    """Get all subjects assigned to a teacher."""
    if is_admin(user):
        from apps.subjects.models import Subject
        return Subject.objects.all()
    if is_teacher(user):
        return user.assigned_subjects.all()
    return []


def get_teacher_courses(user):
    """Get all courses a teacher can access (courses in their assigned subjects)."""
    if is_admin(user):
        from apps.courses.models import Course
        return Course.objects.all()
    if is_teacher(user):
        subjects = get_teacher_subjects(user)
        from apps.courses.models import Course
        return Course.objects.filter(subject__in=subjects)
    return []


def get_teacher_students(user):
    """Get all students enrolled in teacher's courses."""
    if is_admin(user):
        return User.objects.filter(role='student')
    if is_teacher(user):
        courses = get_teacher_courses(user)
        student_ids = set()
        for course in courses:
            for enrollment in course.enrollments.all():
                student_ids.add(enrollment.student.id)
        return User.objects.filter(id__in=student_ids, role='student')
    return []
