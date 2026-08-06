from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.accounts.permissions import has_course_access
from .forms import AssignmentForm, AssignmentSubmissionForm, GradeSubmissionForm
from .models import Assignment, AssignmentSubmission


# ── Mixins ─────────────────────────────────────────────────────────────────────

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_superuser or u.role in ("teacher", "admin"))

    def handle_no_permission(self):
        raise PermissionDenied


# ── Assignment CRUD (teacher / admin) ──────────────────────────────────────────

class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = "assignments/assignment_list.html"
    context_object_name = "assignments"
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.role == "teacher":
            return Assignment.objects.filter(
                created_by=self.request.user
            ).select_related("course")
        return Assignment.objects.filter(is_active=True).select_related("course")


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = "assignments/assignment_detail.html"
    context_object_name = "assignment"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        assignment = self.object
        user = self.request.user

        ctx["now"] = timezone.now()
        ctx["is_past_due"] = timezone.now() > assignment.due_date

        if user.role == "student":
            ctx["my_submission"] = AssignmentSubmission.objects.filter(
                assignment=assignment, student=user
            ).first()

        if user.role in ("teacher", "admin") or user.is_superuser:
            ctx["submissions"] = assignment.submissions.select_related(
                "student", "graded_by"
            ).order_by("-submitted_at")
            ctx["can_manage"] = (
                user.is_superuser
                or user.role == "admin"
                or assignment.created_by == user
            )

        return ctx


class AssignmentCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/assignment_form.html"
    success_url = reverse_lazy("assignments:assignment_list")

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw

    def get_initial(self):
        initial = super().get_initial()
        course_pk = self.request.GET.get("course")
        if course_pk:
            initial["course"] = course_pk
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Assignment created successfully.")
        return super().form_valid(form)


class AssignmentUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/assignment_form.html"
    success_url = reverse_lazy("assignments:assignment_list")

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.role == "admin":
            return Assignment.objects.all()
        return Assignment.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Assignment updated successfully.")
        return super().form_valid(form)


class AssignmentDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Assignment
    template_name = "assignments/assignment_confirm_delete.html"
    success_url = reverse_lazy("assignments:assignment_list")

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.role == "admin":
            return Assignment.objects.all()
        return Assignment.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Assignment deleted successfully.")
        return super().form_valid(form)


# ── Student: My Assignments ────────────────────────────────────────────────────

class MyAssignmentsView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = "assignments/my_assignments.html"
    context_object_name = "assignments"

    def get_queryset(self):
        from apps.courses.models import Enrollment
        enrolled_ids = Enrollment.objects.filter(
            student=self.request.user
        ).values_list("course_id", flat=True)
        return Assignment.objects.filter(
            is_active=True,
            course_id__in=enrolled_ids,
        ).select_related("course").order_by("due_date")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        # Pre-fetch each student's own submission
        submission_map = {
            s.assignment_id: s
            for s in AssignmentSubmission.objects.filter(student=user)
        }
        for a in ctx["assignments"]:
            a.my_submission = submission_map.get(a.pk)
        ctx["now"] = timezone.now()
        return ctx


# ── Student: Submit ────────────────────────────────────────────────────────────

@login_required
def submit_assignment(request, pk):
    if request.user.role != "student":
        messages.error(request, "Only students can submit assignments.")
        return redirect("assignments:assignment_list")

    assignment = get_object_or_404(Assignment, pk=pk, is_active=True)

    # Check enrollment
    from apps.courses.models import Enrollment
    if not Enrollment.objects.filter(student=request.user, course=assignment.course).exists():
        messages.error(request, "You are not enrolled in this course.")
        return redirect("courses:course_detail", pk=assignment.course.pk)

    # Due-date check
    is_past_due = timezone.now() > assignment.due_date

    existing = AssignmentSubmission.objects.filter(
        assignment=assignment, student=request.user
    ).first()

    # Block re-submission if already graded
    if existing and existing.status == "graded":
        messages.info(request, "This assignment has already been graded.")
        return redirect("assignments:submission_detail", pk=existing.pk)

    if request.method == "POST":
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=existing)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            # Mark as late if past due
            submission.status = "late" if is_past_due else "submitted"
            submission.save()

            if is_past_due:
                messages.warning(
                    request,
                    "Your assignment was submitted after the due date and is marked as Late."
                )
            else:
                messages.success(request, "Assignment submitted successfully!")

            return redirect("assignments:assignment_detail", pk=assignment.pk)
    else:
        form = AssignmentSubmissionForm(instance=existing)

    return render(request, "assignments/submission_form.html", {
        "form":        form,
        "assignment":  assignment,
        "existing":    existing,
        "is_past_due": is_past_due,
    })


# ── Teacher: Grade ─────────────────────────────────────────────────────────────

@login_required
def grade_submission(request, pk):
    if not (request.user.is_superuser or request.user.role in ("teacher", "admin")):
        raise PermissionDenied

    submission = get_object_or_404(
        AssignmentSubmission.objects.select_related(
            "assignment", "assignment__course", "student"
        ),
        pk=pk,
    )

    # Teacher can only grade their own assignments
    if request.user.role == "teacher":
        if submission.assignment.created_by != request.user:
            raise PermissionDenied

    if request.method == "POST":
        form = GradeSubmissionForm(
            request.POST,
            max_marks=submission.assignment.max_marks,
        )
        if form.is_valid():
            submission.marks    = form.cleaned_data["marks"]
            submission.grade    = form.cleaned_data["grade"]
            submission.feedback = form.cleaned_data["feedback"]
            submission.status   = "graded"
            submission.graded_by = request.user
            submission.graded_at = timezone.now()
            submission.save()

            messages.success(
                request,
                f"Graded {submission.student.get_full_name() or submission.student.username} "
                f"— {submission.marks}/{submission.assignment.max_marks}"
            )
            return redirect("assignments:assignment_detail", pk=submission.assignment.pk)
    else:
        form = GradeSubmissionForm(
            max_marks=submission.assignment.max_marks,
            initial={
                "marks":    submission.marks,
                "grade":    submission.grade,
                "feedback": submission.feedback,
            }
        )

    return render(request, "assignments/grade_submission.html", {
        "form":       form,
        "submission": submission,
    })


# ── Student: View own submission / result ──────────────────────────────────────

@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(
        AssignmentSubmission.objects.select_related(
            "assignment", "assignment__course", "graded_by"
        ),
        pk=pk,
        student=request.user,
    )
    return render(request, "assignments/submission_detail.html", {
        "submission": submission,
    })
