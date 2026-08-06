from django import forms
from django.utils import timezone

from apps.courses.models import Course
from .models import Assignment, AssignmentSubmission


class AssignmentForm(forms.ModelForm):

    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            "type": "datetime-local",
            "class": "form-control",
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user and user.role == "teacher":
            self.fields["course"].queryset = Course.objects.filter(
                teacher=user
            ).order_by("title")
        else:
            self.fields["course"].queryset = Course.objects.all().order_by("title")

    class Meta:
        model = Assignment
        fields = ["course", "title", "description", "file", "due_date", "max_marks", "is_active"]
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Assignment Title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Assignment instructions and details...",
            }),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "max_marks": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
            }),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class AssignmentSubmissionForm(forms.ModelForm):

    class Meta:
        model = AssignmentSubmission
        fields = ["file", "remarks"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "remarks": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Any notes for your teacher (optional)...",
            }),
        }


class GradeSubmissionForm(forms.Form):

    GRADE_CHOICES = (
        ("", "— Select Grade —"),
        ("A+", "A+"),
        ("A",  "A"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B",  "B"),
        ("B-", "B-"),
        ("C+", "C+"),
        ("C",  "C"),
        ("C-", "C-"),
        ("D",  "D"),
        ("F",  "F"),
    )

    marks = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Enter marks",
        })
    )

    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Write feedback for the student...",
        })
    )

    def __init__(self, *args, max_marks=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["marks"].max_value = max_marks
        self.fields["marks"].widget.attrs["max"] = max_marks
        self.fields["marks"].help_text = f"Maximum: {max_marks}"

    def clean_marks(self):
        marks = self.cleaned_data["marks"]
        max_marks = self.fields["marks"].max_value
        if max_marks and marks > max_marks:
            raise forms.ValidationError(
                f"Marks cannot exceed {max_marks}."
            )
        return marks
