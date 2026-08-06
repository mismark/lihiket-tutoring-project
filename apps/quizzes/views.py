from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
)

from .forms import QuizForm, QuestionForm, ChoiceForm
from .models import Quiz, Question, Choice, QuizAttempt, StudentAnswer


# ── Permission mixin ───────────────────────────────────────────────────────────

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_superuser or u.role in ("teacher", "admin"))

    def handle_no_permission(self):
        raise PermissionDenied


# ── Quiz CRUD ──────────────────────────────────────────────────────────────────

class QuizListView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "quizzes/quiz_list.html"
    context_object_name = "quizzes"
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.role == "teacher":
            return Quiz.objects.filter(
                created_by=self.request.user
            ).select_related("course", "created_by")
        elif self.request.user.role == "student":
            from apps.courses.models import Enrollment
            enrolled_ids = Enrollment.objects.filter(
                student=self.request.user
            ).values_list("course_id", flat=True)
            return Quiz.objects.filter(
                is_active=True, course_id__in=enrolled_ids
            ).select_related("course", "created_by")
        return Quiz.objects.filter(is_active=True).select_related("course", "created_by")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.role == "student":
            attempt_map = {
                a.quiz_id: a
                for a in QuizAttempt.objects.filter(student=self.request.user)
            }
            for quiz in ctx["quizzes"]:
                quiz.my_attempt = attempt_map.get(quiz.pk)
        return ctx


class QuizDetailView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = "quizzes/quiz_detail.html"
    context_object_name = "quiz"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["my_attempt"] = QuizAttempt.objects.filter(
            quiz=self.object, student=self.request.user
        ).first()
        ctx["can_manage"] = (
            self.request.user.is_superuser
            or self.request.user.role == "admin"
            or self.object.created_by == self.request.user
        )
        ctx["total_marks"] = sum(
            q.marks for q in self.object.questions.all()
        )
        return ctx


class QuizCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quizzes/quiz_form.html"
    success_url = reverse_lazy("quizzes:quiz_list")

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
        messages.success(self.request, "Quiz created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quizzes:question_list", kwargs={"quiz_pk": self.object.pk})


class QuizUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = "quizzes/quiz_form.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.role == "admin":
            return Quiz.objects.all()
        return Quiz.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Quiz updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quizzes:quiz_detail", kwargs={"pk": self.object.pk})


class QuizDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Quiz
    template_name = "quizzes/quiz_confirm_delete.html"
    success_url = reverse_lazy("quizzes:quiz_list")

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.role == "admin":
            return Quiz.objects.all()
        return Quiz.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Quiz deleted successfully.")
        return super().form_valid(form)


# ── Question CRUD ──────────────────────────────────────────────────────────────

class QuestionListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Question
    template_name = "quizzes/question_list.html"
    context_object_name = "questions"

    def get_queryset(self):
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs["quiz_pk"])
        return self.quiz.questions.prefetch_related("choices").all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["quiz"] = self.quiz
        ctx["total_marks"] = sum(q.marks for q in ctx["questions"])
        return ctx


@login_required
def import_from_question_bank(request, quiz_pk):
    """
    Teacher selects questions from their own question bank
    (filtered to MCQ and True/False, matched to the quiz's course subject)
    and imports them with all choices into the quiz.
    """
    if not (request.user.is_superuser or request.user.role in ("teacher", "admin")):
        raise PermissionDenied

    quiz = get_object_or_404(
        Quiz.objects.select_related("course", "course__subject"),
        pk=quiz_pk,
    )

    # Teacher can only import into their own quiz
    if request.user.role == "teacher" and quiz.created_by != request.user:
        raise PermissionDenied

    from apps.question_bank.models import QuestionBank

    # Base queryset — only MCQ and TF (quiz engine supports these only)
    if request.user.role == "teacher":
        qb_qs = QuestionBank.objects.filter(
            created_by=request.user,
            question_type__in=["mcq", "tf"],
            is_active=True,
        )
    else:
        # Admin sees all
        qb_qs = QuestionBank.objects.filter(
            question_type__in=["mcq", "tf"],
            is_active=True,
        )

    # ── Auto-filter by quiz's subject if the course has one ───────────────────
    quiz_subject = quiz.course.subject if quiz.course else None

    # Filters from GET
    search     = request.GET.get("search", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    subject_id = request.GET.get("subject", "").strip()

    # Default to the quiz's subject if no subject filter is set
    if not subject_id and quiz_subject:
        subject_id = str(quiz_subject.pk)

    if search:
        qb_qs = qb_qs.filter(question_text__icontains=search)
    if difficulty:
        qb_qs = qb_qs.filter(difficulty=difficulty)
    if subject_id:
        qb_qs = qb_qs.filter(subject_id=subject_id)

    qb_questions = qb_qs.prefetch_related("choices").select_related("subject").order_by("-created_at")

    # Track question texts already in this quiz to flag duplicates
    existing_texts = set(quiz.questions.values_list("question_text", flat=True))

    # ── POST — perform the import ─────────────────────────────────────────────
    if request.method == "POST":
        selected_ids = request.POST.getlist("question_ids")

        if not selected_ids:
            messages.warning(request, "No questions selected. Please tick at least one question.")
            return redirect(request.get_full_path())

        imported = 0
        skipped  = 0

        for qb_id in selected_ids:
            try:
                qb_q = QuestionBank.objects.prefetch_related("choices").get(pk=qb_id)
            except QuestionBank.DoesNotExist:
                continue

            # Skip duplicates
            if qb_q.question_text in existing_texts:
                skipped += 1
                continue

            # Copy question
            new_q = Question.objects.create(
                quiz          = quiz,
                question_text = qb_q.question_text,
                question_type = qb_q.question_type,
                marks         = qb_q.marks,
                explanation   = qb_q.explanation,
            )

            # Copy choices
            for ch in qb_q.choices.all():
                Choice.objects.create(
                    question    = new_q,
                    choice_text = ch.choice_text,
                    is_correct  = ch.is_correct,
                )

            existing_texts.add(qb_q.question_text)
            imported += 1

        if imported:
            msg = f"{imported} question{'s' if imported != 1 else ''} imported successfully."
            if skipped:
                msg += f" {skipped} skipped (already exist in this quiz)."
            messages.success(request, msg)
        else:
            messages.warning(request, "No new questions were imported (all were already in this quiz).")

        return redirect("quizzes:question_list", quiz_pk=quiz_pk)

    # ── GET — show the import page ────────────────────────────────────────────
    from apps.subjects.models import Subject
    if request.user.role == "teacher":
        subjects = Subject.objects.filter(teachers=request.user, is_active=True)
    else:
        subjects = Subject.objects.filter(is_active=True)

    return render(request, "quizzes/import_questions.html", {
        "quiz":              quiz,
        "quiz_subject":      quiz_subject,
        "qb_questions":      qb_questions,
        "search":            search,
        "difficulty":        difficulty,
        "subject_id":        subject_id,
        "subjects":          subjects,
        "existing_texts":    existing_texts,
        "difficulty_levels": QuestionBank.DIFFICULTY_LEVELS,
        "total_available":   qb_qs.count(),
    })


class QuestionCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Question
    form_class = QuestionForm
    template_name = "quizzes/question_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.quiz = get_object_or_404(Quiz, pk=self.kwargs["quiz_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["quiz"] = self.quiz
        return ctx

    def form_valid(self, form):
        form.instance.quiz = self.quiz
        messages.success(self.request, "Question added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quizzes:question_list", kwargs={"quiz_pk": self.quiz.pk})


class QuestionUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Question
    form_class = QuestionForm
    template_name = "quizzes/question_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["quiz"] = self.object.quiz
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Question updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quizzes:question_list", kwargs={"quiz_pk": self.object.quiz.pk})


class QuestionDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Question
    template_name = "quizzes/question_confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "Question deleted successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quizzes:question_list", kwargs={"quiz_pk": self.object.quiz.pk})


# ── Choice CRUD ────────────────────────────────────────────────────────────────

class ChoiceListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = Choice
    template_name = "quizzes/choice_list.html"
    context_object_name = "choices"

    def get_queryset(self):
        self.question = get_object_or_404(Question, pk=self.kwargs["question_pk"])
        return self.question.choices.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["question"] = self.question
        ctx["quiz"] = self.question.quiz
        return ctx


class ChoiceCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Choice
    form_class = ChoiceForm
    template_name = "quizzes/choice_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.question = get_object_or_404(Question, pk=self.kwargs["question_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["question"] = self.question
        ctx["quiz"] = self.question.quiz
        return ctx

    def form_valid(self, form):
        form.instance.question = self.question
        messages.success(self.request, "Choice added successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quizzes:choice_list", kwargs={"question_pk": self.question.pk})


class ChoiceUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Choice
    form_class = ChoiceForm
    template_name = "quizzes/choice_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["question"] = self.object.question
        ctx["quiz"] = self.object.question.quiz
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Choice updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quizzes:choice_list", kwargs={"question_pk": self.object.question.pk})


class ChoiceDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Choice
    template_name = "quizzes/choice_confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, "Choice deleted successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("quizzes:choice_list", kwargs={"question_pk": self.object.question.pk})


# ── My Quizzes (student) ───────────────────────────────────────────────────────

class MyQuizzesView(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = "quizzes/my_quizzes.html"
    context_object_name = "quizzes"

    def get_queryset(self):
        from apps.courses.models import Enrollment
        enrolled_ids = Enrollment.objects.filter(
            student=self.request.user
        ).values_list("course_id", flat=True)
        return Quiz.objects.filter(
            is_active=True, course_id__in=enrolled_ids
        ).select_related("course")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt_map = {
            a.quiz_id: a
            for a in QuizAttempt.objects.filter(student=self.request.user)
        }
        for quiz in ctx["quizzes"]:
            quiz.my_attempt = attempt_map.get(quiz.pk)
        return ctx


# ── Student: Take quiz ─────────────────────────────────────────────────────────

@login_required
def start_quiz(request, pk):
    if request.user.role != "student":
        messages.error(request, "Only students can take quizzes.")
        return redirect("quizzes:quiz_list")

    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)

    # Must be enrolled in the course
    from apps.courses.models import Enrollment
    if not Enrollment.objects.filter(student=request.user, course=quiz.course).exists():
        messages.error(request, "You must be enrolled in this course to take the quiz.")
        return redirect("courses:course_detail", pk=quiz.course.pk)

    # Check if already attempted
    attempt = QuizAttempt.objects.filter(quiz=quiz, student=request.user).first()
    if attempt and attempt.completed_at:
        messages.info(request, "You have already completed this quiz.")
        return redirect("quizzes:quiz_result", pk=attempt.pk)

    # Create or reuse in-progress attempt
    if not attempt:
        attempt = QuizAttempt.objects.create(quiz=quiz, student=request.user)

    return render(request, "quizzes/quiz_attempt.html", {
        "quiz":    quiz,
        "attempt": attempt,
    })


@login_required
def submit_quiz(request, pk):
    attempt = get_object_or_404(QuizAttempt, pk=pk, student=request.user)

    if attempt.completed_at:
        return redirect("quizzes:quiz_result", pk=attempt.pk)

    if request.method != "POST":
        return redirect("quizzes:start_quiz", pk=attempt.quiz.pk)

    # ── Server-side time enforcement ──────────────────────────────
    # Calculate how many seconds have passed since the attempt started
    elapsed_seconds   = (timezone.now() - attempt.started_at).total_seconds()
    allowed_seconds   = attempt.quiz.duration * 60
    time_expired      = elapsed_seconds > (allowed_seconds + 30)  # 30s grace period

    score       = 0
    total_marks = 0

    for question in attempt.quiz.questions.prefetch_related("choices").all():
        total_marks += question.marks

        # If time expired, don't accept any answers — count all as wrong
        selected_choice_id = None if time_expired else request.POST.get(f"question_{question.id}")
        selected_choice    = None
        correct            = False

        if selected_choice_id:
            selected_choice = Choice.objects.filter(
                id=selected_choice_id, question=question
            ).first()
            if selected_choice and selected_choice.is_correct:
                correct = True
                score  += question.marks

        StudentAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_choice=selected_choice,
            is_correct=correct,
        )

    percentage           = round((score / total_marks) * 100, 1) if total_marks > 0 else 0
    attempt.score        = score
    attempt.total_marks  = total_marks
    attempt.percentage   = percentage
    attempt.passed       = percentage >= attempt.quiz.passing_score
    attempt.completed_at = timezone.now()
    attempt.save()

    if time_expired:
        messages.warning(request, "Time was up — your quiz was automatically submitted.")
    else:
        messages.success(request, "Quiz submitted successfully!")

    return redirect("quizzes:quiz_result", pk=attempt.pk)


@login_required
def quiz_result(request, pk):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related("quiz", "quiz__course"),
        pk=pk,
        student=request.user,
    )

    # Attach correct choice to each answer for the review section
    answers = attempt.answers.select_related(
        "question", "selected_choice"
    ).prefetch_related("question__choices").order_by("question__id")

    for ans in answers:
        ans.correct_choice = ans.question.choices.filter(is_correct=True).first()

    return render(request, "quizzes/quiz_result.html", {
        "attempt": attempt,
        "answers": answers,
    })


# ── Teacher: All results for a quiz ───────────────────────────────────────────

@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    if not (request.user.is_superuser or request.user.role in ("teacher", "admin")):
        raise PermissionDenied

    if request.user.role == "teacher" and quiz.created_by != request.user:
        raise PermissionDenied

    attempts = QuizAttempt.objects.filter(
        quiz=quiz
    ).select_related("student").order_by("-score")

    passed_count  = attempts.filter(passed=True).count()
    failed_count  = attempts.filter(passed=False).count()
    avg_score     = (
        sum(a.percentage for a in attempts) / attempts.count()
        if attempts.count() > 0 else 0
    )

    return render(request, "quizzes/quiz_results.html", {
        "quiz":         quiz,
        "attempts":     attempts,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "avg_score":    round(avg_score, 1),
    })
