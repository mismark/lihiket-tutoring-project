from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import QuestionBankChoiceFormSet, QuestionBankForm
from .models import QuestionBank


# ── Permission helpers ─────────────────────────────────────────────────────────

def _is_teacher(user):
    return user.is_authenticated and user.role == "teacher"


def _is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == "admin")


def _teacher_subjects(user):
    """Return the subjects assigned to this teacher."""
    from apps.subjects.models import Subject
    return Subject.objects.filter(teachers=user, is_active=True)


def _can_access_question(user, question):
    """
    A teacher can access a question only if:
      - they created it, AND
      - the question's subject is one of their assigned subjects
        (or the question has no subject assigned).
    Admin can access everything.
    """
    if _is_admin(user):
        return True

    if _is_teacher(user):
        if question.created_by != user:
            return False
        # If question has no subject, teacher can still manage it
        if question.subject is None:
            return True
        # Otherwise the subject must be assigned to this teacher
        return _teacher_subjects(user).filter(pk=question.subject_id).exists()

    return False


# ── Views ──────────────────────────────────────────────────────────────────────

@login_required
def question_list(request):
    """
    Teacher — only questions they created, for their assigned subjects.
    Admin   — all questions.
    Others  — 403.
    """
    if not (_is_teacher(request.user) or _is_admin(request.user)):
        raise PermissionDenied

    search     = request.GET.get("search", "").strip()
    q_type     = request.GET.get("type", "").strip()
    difficulty = request.GET.get("difficulty", "").strip()
    subject_id = request.GET.get("subject", "").strip()

    if _is_admin(request.user):
        questions = QuestionBank.objects.select_related("subject", "created_by")
    else:
        # Only own questions whose subject is assigned to them (+ subjectless ones)
        from django.db.models import Q
        teacher_subject_ids = _teacher_subjects(request.user).values_list("pk", flat=True)
        questions = QuestionBank.objects.filter(
            created_by=request.user
        ).filter(
            Q(subject__isnull=True) | Q(subject_id__in=teacher_subject_ids)
        ).select_related("subject")

    if search:
        questions = questions.filter(question_text__icontains=search)
    if q_type:
        questions = questions.filter(question_type=q_type)
    if difficulty:
        questions = questions.filter(difficulty=difficulty)
    if subject_id:
        questions = questions.filter(subject_id=subject_id)

    paginator = Paginator(questions, 10)
    page_obj  = paginator.get_page(request.GET.get("page"))

    from apps.subjects.models import Subject
    subjects = (
        _teacher_subjects(request.user)
        if _is_teacher(request.user)
        else Subject.objects.filter(is_active=True).order_by("grade_level", "name")
    )

    return render(request, "question_bank/list.html", {
        "questions":         page_obj,
        "page_obj":          page_obj,
        "search":            search,
        "q_type":            q_type,
        "difficulty":        difficulty,
        "subject_id":        subject_id,
        "subjects":          subjects,
        "question_types":    QuestionBank.QUESTION_TYPES,
        "difficulty_levels": QuestionBank.DIFFICULTY_LEVELS,
        "total":             questions.count(),
    })


@login_required
def question_detail(request, pk):
    if not (_is_teacher(request.user) or _is_admin(request.user)):
        raise PermissionDenied

    question = get_object_or_404(
        QuestionBank.objects.prefetch_related("choices").select_related("subject", "created_by"),
        pk=pk,
    )

    if not _can_access_question(request.user, question):
        raise PermissionDenied

    return render(request, "question_bank/detail.html", {"question": question})


@login_required
def question_create(request):
    """
    Only teachers can create questions.
    The subject chosen must be one of the teacher's assigned subjects.
    """
    if not _is_teacher(request.user) and not _is_admin(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form    = QuestionBankForm(request.POST, user=request.user)
        formset = QuestionBankChoiceFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)

            # Extra server-side guard: teacher must own the chosen subject
            if _is_teacher(request.user) and question.subject:
                if not _teacher_subjects(request.user).filter(pk=question.subject_id).exists():
                    messages.error(
                        request,
                        "You can only create questions for your assigned subjects."
                    )
                    return render(request, "question_bank/form.html", {
                        "form": form, "formset": formset,
                        "action": "Create", "title": "Add New Question",
                    })

            question.created_by = request.user
            question.save()
            formset.instance = question
            formset.save()

            messages.success(request, "Question created successfully.")
            return redirect("question_bank:list")
    else:
        form    = QuestionBankForm(user=request.user)
        formset = QuestionBankChoiceFormSet()

    return render(request, "question_bank/form.html", {
        "form":    form,
        "formset": formset,
        "action":  "Create",
        "title":   "Add New Question",
    })


@login_required
def question_edit(request, pk):
    if not (_is_teacher(request.user) or _is_admin(request.user)):
        raise PermissionDenied

    question = get_object_or_404(QuestionBank, pk=pk)

    if not _can_access_question(request.user, question):
        messages.error(
            request,
            "You can only edit questions for your assigned subjects."
        )
        return redirect("question_bank:list")

    if request.method == "POST":
        form    = QuestionBankForm(request.POST, instance=question, user=request.user)
        formset = QuestionBankChoiceFormSet(request.POST, instance=question)

        if form.is_valid() and formset.is_valid():
            updated = form.save(commit=False)

            # Guard: teacher can't reassign question to a subject they don't own
            if _is_teacher(request.user) and updated.subject:
                if not _teacher_subjects(request.user).filter(pk=updated.subject_id).exists():
                    messages.error(
                        request,
                        "You can only assign questions to your own subjects."
                    )
                    return render(request, "question_bank/form.html", {
                        "form": form, "formset": formset,
                        "action": "Edit", "title": "Edit Question",
                        "question": question,
                    })

            updated.save()
            formset.save()
            messages.success(request, "Question updated successfully.")
            return redirect("question_bank:detail", pk=question.pk)
    else:
        form    = QuestionBankForm(instance=question, user=request.user)
        formset = QuestionBankChoiceFormSet(instance=question)

    return render(request, "question_bank/form.html", {
        "form":     form,
        "formset":  formset,
        "action":   "Edit",
        "title":    "Edit Question",
        "question": question,
    })


@login_required
def question_delete(request, pk):
    if not (_is_teacher(request.user) or _is_admin(request.user)):
        raise PermissionDenied

    question = get_object_or_404(QuestionBank, pk=pk)

    if not _can_access_question(request.user, question):
        messages.error(
            request,
            "You can only delete questions for your assigned subjects."
        )
        return redirect("question_bank:list")

    if request.method == "POST":
        question.delete()
        messages.success(request, "Question deleted successfully.")
        return redirect("question_bank:list")

    return render(request, "question_bank/delete.html", {"question": question})
