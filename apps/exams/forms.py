from django import forms
from apps.courses.models import Course
from .models import Exam


class ExamForm(forms.ModelForm):

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.role == "teacher":
            self.fields["course"].queryset = Course.objects.filter(
                teacher=user
            ).order_by("title")
        else:
            self.fields["course"].queryset = Course.objects.all().order_by("title")

    class Meta:
        model = Exam
        fields = [
            "course", "title", "description",
            "duration", "passing_score",
            "start_time", "is_active",
        ]
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Exam Title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Exam instructions...",
            }),
            "duration": forms.NumberInput(attrs={
                "class": "form-control", "min": 1,
                "placeholder": "Minutes",
            }),
            "passing_score": forms.NumberInput(attrs={
                "class": "form-control", "min": 0, "max": 100,
            }),
            "start_time": forms.DateTimeInput(attrs={
                "class": "form-control", "type": "datetime-local",
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
