from django import forms
from apps.courses.models import Course
from .models import Quiz, Question, Choice, QuizAttempt


class QuizForm(forms.ModelForm):

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and user.role == "teacher":
            self.fields["course"].queryset = Course.objects.filter(
                teacher=user
            ).order_by("title")
        else:
            self.fields["course"].queryset = Course.objects.all().order_by("title")

    class Meta:
        model = Quiz
        fields = ["course", "title", "description", "duration", "passing_score", "max_attempts", "is_active"]
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Quiz Title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Quiz Description",
            }),
            "duration": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "passing_score": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "max": 100,
            }),
            "max_attempts": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ["question_text", "question_type", "marks", "explanation"]
        widgets = {
            "question_text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter the question...",
            }),
            "question_type": forms.Select(attrs={"class": "form-select"}),
            "marks": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "explanation": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Explain the correct answer (shown after quiz)...",
            }),
        }


class ChoiceForm(forms.ModelForm):

    class Meta:
        model = Choice
        fields = ["choice_text", "is_correct"]
        widgets = {
            "choice_text": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter choice text...",
            }),
            "is_correct": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class QuizAttemptForm(forms.ModelForm):
    class Meta:
        model = QuizAttempt
        fields = []
