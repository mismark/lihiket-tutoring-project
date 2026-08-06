from django import forms
from django.forms import inlineformset_factory

from .models import QuestionBank, QuestionBankChoice


class QuestionBankForm(forms.ModelForm):

    class Meta:
        model = QuestionBank
        fields = [
            "subject",
            "question_text",
            "question_type",
            "difficulty",
            "marks",
            "tags",
            "explanation",
            "is_active",
        ]
        widgets = {
            "subject": forms.Select(attrs={
                "class": "form-select",
            }),
            "question_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter the question...",
            }),
            "question_type": forms.Select(attrs={
                "class": "form-select",
                "id": "id_question_type",
            }),
            "difficulty": forms.Select(attrs={
                "class": "form-select",
            }),
            "marks": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "tags": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. algebra, fractions, geometry",
            }),
            "explanation": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Explain the correct answer (optional)...",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Filter subject dropdown to only subjects assigned to this teacher
        if user and hasattr(user, "role") and user.role == "teacher":
            from apps.subjects.models import Subject
            self.fields["subject"].queryset = Subject.objects.filter(
                teachers=user, is_active=True
            ).order_by("grade_level", "name")
        else:
            from apps.subjects.models import Subject
            self.fields["subject"].queryset = Subject.objects.filter(
                is_active=True
            ).order_by("grade_level", "name")

        # Empty label for subject
        self.fields["subject"].empty_label = "— Select Subject (optional) —"
        self.fields["subject"].required = False


class QuestionBankChoiceForm(forms.ModelForm):

    class Meta:
        model = QuestionBankChoice
        fields = ["choice_text", "is_correct", "order"]
        widgets = {
            "choice_text": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter answer choice...",
            }),
            "is_correct": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
            "order": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "style": "width:70px;",
            }),
        }


# Inline formset — choices linked to a specific question instance
QuestionBankChoiceFormSet = inlineformset_factory(
    QuestionBank,
    QuestionBankChoice,
    form=QuestionBankChoiceForm,
    extra=4,
    max_num=10,
    can_delete=True,
    fields=["choice_text", "is_correct", "order"],
)
