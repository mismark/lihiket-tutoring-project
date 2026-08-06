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

from apps.quizzes.models import Question, Choice
from .forms import ExamForm
from .models import Exam, ExamQuestion, ExamAttempt, ExamAnswer


# ── Permission helpers ─────────────────────────────────────────────────────────

class TeacherRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_superuser or u.role in ("teacher", "admin"))
    def handle_no_permission(self):
        raise PermissionDenied


def _can_manage_exam(user, exam=None):
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.role == "admin":
        return True
    if user.role == "teacher":
        if exam is None:
            return True
        return exam.created_by == user
    return False


# ── Exam CRUD ──────────────────────────────────────────────────────────────────

class ExamListView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = "exams/exam_list.html"
    context_object_name = "exams"
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.role == "teacher":
            return Exam.objects.filter(
                created_by=self.request.user
            ).select_related("course", "created_by")
        elif self.request.user.role == "student":
            from apps.courses.models import Enrollment
            enrolled_ids = Enrollment.objects.filter(
                student=self.request.user
            ).values_list("course_id", flat=True)
            return Exam.objects.filter(
                is_active=True,
                course_id__in=enrolled_ids,
            ).select_related("course", "created_by")
        return Exam.objects.filter(is_active=True).select_related("course", "created_by")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.role == "student":
            attempt_map = {
                a.exam_id: a
                for a in ExamAttempt.objects.filter(student=self.request.user)
            }
            now = timezone.now()
            for exam in ctx["exams"]:
                exam.my_attempt    = attempt_map.get(exam.pk)
                exam.is_open       = exam.start_time <= now <= exam.end_time
                exam.is_upcoming   = now < exam.start_time
        return ctx


class ExamDetailView(LoginRequiredMixin, DetailView):
    model = Exam
    template_name = "exams/exam_detail.html"
    context_object_name = "exam"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        ctx["can_manage"]  = _can_manage_exam(self.request.user, self.object)
        ctx["my_attempt"]  = ExamAttempt.objects.filter(
            exam=self.object, student=self.request.user
        ).first()
        ctx["total_marks"] = self.object.total_marks
        ctx["is_open"]     = self.object.is_currently_open
        ctx["is_upcoming"] = now < self.object.start_time
        ctx["is_expired"]  = now > self.object.end_time
        return ctx


class ExamCreateView(LoginRequiredMixin, TeacherRequiredMixin, CreateView):
    model = Exam
    form_class = ExamForm
    template_name = "exams/exam_form.html"

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
        messages.success(self.request, "Exam created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("exams:exam_question_list", kwargs={"exam_pk": self.object.pk})


class ExamUpdateView(LoginRequiredMixin, TeacherRequiredMixin, UpdateView):
    model = Exam
    form_class = ExamForm
    template_name = "exams/exam_form.html"

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["user"] = self.request.user
        return kw

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.role == "admin":
            return Exam.objects.all()
        return Exam.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Exam updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("exams:exam_detail", kwargs={"pk": self.object.pk})


class ExamDeleteView(LoginRequiredMixin, TeacherRequiredMixin, DeleteView):
    model = Exam
    template_name = "exams/exam_confirm_delete.html"
    success_url = reverse_lazy("exams:exam_list")

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.role == "admin":
            return Exam.objects.all()
        return Exam.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Exam deleted successfully.")
        return super().form_valid(form)


# ── Question management ────────────────────────────────────────────────────────

class ExamQuestionListView(LoginRequiredMixin, TeacherRequiredMixin, ListView):
    model = ExamQuestion
    template_name = "exams/exam_question_list.html"
    context_object_name = "questions"

    def get_queryset(self):
        self.exam = get_object_or_404(Exam, pk=self.kwargs["exam_pk"])
        return self.exam.questions.select_related(
            "question"
        ).prefetch_related("question__choices").all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["exam"]        = self.exam
        ctx["total_marks"] = self.exam.total_marks
        return ctx


@login_required
def view_exam_question(request, pk):
    """View a single question and its choices."""
    eq = get_object_or_404(
        ExamQuestion.objects.select_related("question", "exam")
        .prefetch_related("question__choices"),
        pk=pk,
    )
    if not _can_manage_exam(request.user, eq.exam):
        raise PermissionDenied
    return render(request, "exams/exam_question_view.html", {
        "eq":   eq,
        "exam": eq.exam,
    })


@login_required
def edit_exam_question(request, pk):
    """Edit a question that belongs to this exam."""
    eq = get_object_or_404(
        ExamQuestion.objects.select_related("question", "exam")
        .prefetch_related("question__choices"),
        pk=pk,
    )
    if not _can_manage_exam(request.user, eq.exam):
        raise PermissionDenied

    question = eq.question
    choices  = list(question.choices.all())

    if request.method == "POST":
        question.question_text = request.POST.get("question_text", "").strip()
        question.question_type = request.POST.get("question_type", "mcq")
        question.marks         = int(request.POST.get("marks", 1))
        question.explanation   = request.POST.get("explanation", "").strip()
        question.save()

        # Delete old choices and recreate
        question.choices.all().delete()
        for i in range(1, 7):
            choice_text = request.POST.get(f"choice_{i}", "").strip()
            if choice_text:
                is_correct = request.POST.get(f"correct_{i}") == "on"
                Choice.objects.create(
                    question    = question,
                    choice_text = choice_text,
                    is_correct  = is_correct,
                )

        messages.success(request, "Question updated successfully.")
        return redirect("exams:exam_question_list", exam_pk=eq.exam.pk)

    # Pad choices list to 6 for template
    choices_padded = list(choices) + [None] * (6 - len(choices))

    return render(request, "exams/exam_question_edit.html", {
        "eq":             eq,
        "exam":           eq.exam,
        "question":       question,
        "choices_padded": choices_padded,
    })


@login_required
def exam_question_delete(request, pk):
    eq = get_object_or_404(ExamQuestion, pk=pk)
    if not _can_manage_exam(request.user, eq.exam):
        raise PermissionDenied
    if request.method == "POST":
        exam_pk = eq.exam.pk
        eq.delete()
        messages.success(request, "Question removed from exam.")
        return redirect("exams:exam_question_list", exam_pk=exam_pk)
    # GET — just redirect back, do nothing
    return redirect("exams:exam_question_list", exam_pk=eq.exam.pk)


@login_required
def add_exam_question(request, exam_pk):
    """
    Teacher manually adds a question (with choices) directly to an exam.
    Uses the pool-quiz pattern so ExamQuestion can link to quizzes.Question.
    """
    if not (request.user.is_superuser or request.user.role in ("teacher", "admin")):
        raise PermissionDenied

    exam = get_object_or_404(Exam, pk=exam_pk)
    if not _can_manage_exam(request.user, exam):
        raise PermissionDenied

    if request.method == "POST":
        question_text = request.POST.get("question_text", "").strip()
        question_type = request.POST.get("question_type", "mcq")
        marks         = int(request.POST.get("marks", 1))
        explanation   = request.POST.get("explanation", "").strip()

        if not question_text:
            messages.error(request, "Question text is required.")
            return redirect("exams:exam_question_list", exam_pk=exam_pk)

        # Get or create a pool quiz for this teacher
        from apps.quizzes.models import Quiz as QuizModel
        pool_quiz, _ = QuizModel.objects.get_or_create(
            title=f"__exam_pool_{request.user.pk}__",
            created_by=request.user,
            defaults={
                "course":        exam.course,
                "duration":      60,
                "passing_score": 50,
                "is_active":     False,
            }
        )

        # Create the question in the pool quiz
        quiz_q = Question.objects.create(
            quiz          = pool_quiz,
            question_text = question_text,
            question_type = question_type,
            marks         = marks,
            explanation   = explanation,
        )

        # Save choices (up to 6 from POST)
        for i in range(1, 7):
            choice_text = request.POST.get(f"choice_{i}", "").strip()
            if choice_text:
                is_correct = request.POST.get(f"correct_{i}") == "on"
                Choice.objects.create(
                    question    = quiz_q,
                    choice_text = choice_text,
                    is_correct  = is_correct,
                )

        # Link to exam
        ExamQuestion.objects.create(exam=exam, question=quiz_q)
        messages.success(request, f'Question "{question_text[:50]}" added to exam.')

    return redirect("exams:exam_question_list", exam_pk=exam_pk)


# ── Import questions from Question Bank ────────────────────────────────────────

@login_required
def import_exam_questions(request, exam_pk):
    if not (request.user.is_superuser or request.user.role in ("teacher", "admin")):
        raise PermissionDenied

    exam = get_object_or_404(
        Exam.objects.select_related("course", "course__subject"),
        pk=exam_pk,
    )
    if request.user.role == "teacher" and exam.created_by != request.user:
        raise PermissionDenied

    from apps.question_bank.models import QuestionBank

    if request.user.role == "teacher":
        qb_qs = QuestionBank.objects.filter(
            created_by=request.user,
            question_type__in=["mcq", "tf"],
            is_active=True,
        )
    else:
        qb_qs = QuestionBank.objects.filter(
            question_type__in=["mcq", "tf"],
            is_active=True,
        )

    quiz_subject = exam.course.subject if exam.course else None

    search     = request.GET.get("search", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    subject_id = request.GET.get("subject", "").strip()

    if not subject_id and quiz_subject:
        subject_id = str(quiz_subject.pk)

    if search:
        qb_qs = qb_qs.filter(question_text__icontains=search)
    if difficulty:
        qb_qs = qb_qs.filter(difficulty=difficulty)
    if subject_id:
        qb_qs = qb_qs.filter(subject_id=subject_id)

    qb_questions = qb_qs.prefetch_related("choices").select_related("subject").order_by("-created_at")

    # Already-linked quiz Question PKs in this exam
    existing_q_ids = set(exam.questions.values_list("question_id", flat=True))

    if request.method == "POST":
        selected_ids = request.POST.getlist("question_ids")
        if not selected_ids:
            messages.warning(request, "No questions selected.")
            return redirect(request.get_full_path())

        imported = 0
        skipped  = 0

        for qb_id in selected_ids:
            try:
                qb_q = QuestionBank.objects.prefetch_related("choices").get(pk=qb_id)
            except QuestionBank.DoesNotExist:
                continue

            # Each QB question needs a matching quizzes.Question
            # Find or create it so ExamQuestion can link to it
            quiz_q, created = Question.objects.get_or_create(
                question_text=qb_q.question_text,
                defaults={
                    "question_type": qb_q.question_type,
                    "marks":         qb_q.marks,
                    "explanation":   qb_q.explanation,
                    # quiz FK is required — use a dummy internal quiz
                    # We create a hidden "exam_pool" quiz owned by this teacher
                }
            )

            # If it's a brand new question, we need to assign a quiz
            # Use a special "Question Pool" quiz per teacher
            if created:
                from apps.quizzes.models import Quiz as QuizModel
                pool_quiz, _ = QuizModel.objects.get_or_create(
                    title=f"__exam_pool_{request.user.pk}__",
                    created_by=request.user,
                    defaults={
                        "course":        exam.course,
                        "duration":      60,
                        "passing_score": 50,
                        "is_active":     False,
                    }
                )
                quiz_q.quiz = pool_quiz
                quiz_q.save()

                # Copy choices
                for ch in qb_q.choices.all():
                    Choice.objects.get_or_create(
                        question=quiz_q,
                        choice_text=ch.choice_text,
                        defaults={"is_correct": ch.is_correct}
                    )

            if quiz_q.pk in existing_q_ids:
                skipped += 1
                continue

            ExamQuestion.objects.create(exam=exam, question=quiz_q)
            existing_q_ids.add(quiz_q.pk)
            imported += 1

        if imported:
            msg = f"{imported} question{'s' if imported != 1 else ''} imported."
            if skipped:
                msg += f" {skipped} skipped (already in exam)."
            messages.success(request, msg)
        else:
            messages.warning(request, "No new questions were imported.")

        return redirect("exams:exam_question_list", exam_pk=exam_pk)

    from apps.subjects.models import Subject
    subjects = (
        Subject.objects.filter(teachers=request.user, is_active=True)
        if request.user.role == "teacher"
        else Subject.objects.filter(is_active=True)
    )

    return render(request, "exams/import_questions.html", {
        "exam":              exam,
        "quiz_subject":      quiz_subject,
        "qb_questions":      qb_questions,
        "search":            search,
        "difficulty":        difficulty,
        "subject_id":        subject_id,
        "subjects":          subjects,
        "existing_q_ids":    existing_q_ids,
        "difficulty_levels": QuestionBank.DIFFICULTY_LEVELS,
    })


# ── Student: My Exams ──────────────────────────────────────────────────────────

class MyExamsView(LoginRequiredMixin, ListView):
    model = Exam
    template_name = "exams/my_exams.html"
    context_object_name = "exams"

    def get_queryset(self):
        from apps.courses.models import Enrollment
        enrolled_ids = Enrollment.objects.filter(
            student=self.request.user
        ).values_list("course_id", flat=True)
        return Exam.objects.filter(
            is_active=True,
            course_id__in=enrolled_ids,
        ).select_related("course").order_by("start_time")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        attempt_map = {
            a.exam_id: a
            for a in ExamAttempt.objects.filter(student=self.request.user)
        }
        now = timezone.now()
        for exam in ctx["exams"]:
            exam.my_attempt  = attempt_map.get(exam.pk)
            exam.is_open     = exam.is_currently_open
            exam.is_upcoming = now < exam.start_time
            exam.is_expired  = now > exam.end_time
        return ctx


# ── Student: Take exam ─────────────────────────────────────────────────────────

@login_required
def take_exam(request, pk):
    if request.user.role != "student":
        messages.error(request, "Only students can take exams.")
        return redirect("exams:exam_list")

    exam = get_object_or_404(Exam, pk=pk, is_active=True)
    now  = timezone.now()

    # Enrollment check
    from apps.courses.models import Enrollment
    if not Enrollment.objects.filter(student=request.user, course=exam.course).exists():
        messages.error(request, "You must be enrolled in this course to take this exam.")
        return redirect("courses:course_detail", pk=exam.course.pk)

    if now < exam.start_time:
        messages.warning(
            request,
            f"This exam hasn't started yet. It opens on "
            f"{exam.start_time.strftime('%B %d, %Y at %H:%M')}."
        )
        return redirect("exams:exam_detail", pk=exam.pk)

    if now > exam.end_time:
        messages.error(request, "This exam has already ended.")
        return redirect("exams:exam_detail", pk=exam.pk)

    # Already attempted?
    attempt = ExamAttempt.objects.filter(exam=exam, student=request.user).first()
    if attempt and attempt.submitted_at:
        messages.info(request, "You have already completed this exam.")
        return redirect("exams:exam_result", pk=attempt.pk)

    # Create attempt
    if not attempt:
        attempt = ExamAttempt.objects.create(exam=exam, student=request.user)

    questions = (
        exam.questions
        .select_related("question")
        .prefetch_related("question__choices")
    )

    # Seconds remaining from when the attempt started
    elapsed   = (now - attempt.started_at).total_seconds()
    remaining = max(0, exam.duration * 60 - int(elapsed))

    return render(request, "exams/take_exam.html", {
        "exam":             exam,
        "attempt":          attempt,
        "questions":        questions,
        "remaining_seconds": remaining,
    })


@login_required
def submit_exam(request, pk):
    attempt = get_object_or_404(ExamAttempt, pk=pk, student=request.user)

    if attempt.submitted_at:
        return redirect("exams:exam_result", pk=attempt.pk)

    if request.method != "POST":
        return redirect("exams:take_exam", pk=attempt.exam.pk)

    # Server-side time enforcement
    elapsed_seconds = (timezone.now() - attempt.started_at).total_seconds()
    allowed_seconds = attempt.exam.duration * 60
    time_expired    = elapsed_seconds > (allowed_seconds + 30)  # 30s grace

    score       = 0
    total_marks = attempt.exam.total_marks

    for item in attempt.exam.questions.select_related("question").prefetch_related("question__choices"):
        question = item.question

        selected_choice_id = None if time_expired else request.POST.get(f"question_{question.id}")
        selected_choice    = None
        is_correct         = False

        if selected_choice_id:
            selected_choice = Choice.objects.filter(
                pk=selected_choice_id, question=question
            ).first()
            if selected_choice and selected_choice.is_correct:
                is_correct = True
                score     += question.marks

        ExamAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_choice=selected_choice,
            is_correct=is_correct,
        )

    percentage         = round((score / total_marks) * 100, 1) if total_marks > 0 else 0
    attempt.score      = score
    attempt.percentage = percentage
    attempt.passed     = percentage >= attempt.exam.passing_score
    attempt.submitted_at = timezone.now()
    attempt.save()

    if time_expired:
        messages.warning(request, "Time was up — your exam was automatically submitted.")
    else:
        messages.success(request, "Exam submitted successfully!")

    return redirect("exams:exam_result", pk=attempt.pk)


# ── Student: Result ────────────────────────────────────────────────────────────

@login_required
def exam_result(request, pk):
    attempt = get_object_or_404(
        ExamAttempt.objects.select_related("exam", "exam__course"),
        pk=pk, student=request.user,
    )

    answers = attempt.answers.select_related(
        "question", "selected_choice"
    ).prefetch_related("question__choices").order_by("question__id")

    for ans in answers:
        ans.correct_choice = ans.question.choices.filter(is_correct=True).first()

    return render(request, "exams/exam_result.html", {
        "attempt": attempt,
        "answers": answers,
    })


# ── Teacher: All results ───────────────────────────────────────────────────────

@login_required
def exam_results(request, exam_id):
    exam = get_object_or_404(Exam, pk=exam_id)

    if not _can_manage_exam(request.user, exam):
        raise PermissionDenied

    attempts = ExamAttempt.objects.filter(
        exam=exam
    ).select_related("student").order_by("-score")

    passed_count = attempts.filter(passed=True).count()
    failed_count = attempts.filter(passed=False).count()
    avg_score    = (
        sum(a.percentage for a in attempts) / attempts.count()
        if attempts.count() > 0 else 0
    )

    return render(request, "exams/exam_results.html", {
        "exam":         exam,
        "attempts":     attempts,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "avg_score":    round(avg_score, 1),
    })
