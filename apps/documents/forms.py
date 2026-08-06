import os
from django import forms

from apps.courses.models import Course
from apps.subjects.models import Subject
from .models import Document


class DocumentForm(forms.ModelForm):

    ALLOWED_EXTENSIONS = (
        ".pdf", ".doc", ".docx",
        ".ppt", ".pptx",
        ".xls", ".xlsx",
        ".txt", ".zip", ".rar",
    )

    class Meta:
        model = Document
        fields = [
            "subject",
            "course",
            "lesson",
            "title",
            "description",
            "file",
            "visibility",
        ]
        widgets = {
            "subject": forms.Select(attrs={
                "class": "form-select",
                "id": "id_subject",
            }),
            "course": forms.Select(attrs={
                "class": "form-select",
                "id": "id_course",
            }),
            "lesson": forms.Select(attrs={
                "class": "form-select",
                "id": "id_lesson",
            }),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Document Title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Brief description (optional)",
            }),
            "file": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "visibility": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user and user.role == "teacher":
            # Subject: only subjects assigned to this teacher
            self.fields["subject"].queryset = Subject.objects.filter(
                teachers=user, is_active=True
            ).order_by("grade_level", "name")

            # Course: only courses this teacher teaches
            self.fields["course"].queryset = Course.objects.filter(
                teacher=user
            ).order_by("title")

        elif user and (user.role == "admin" or user.is_superuser):
            self.fields["subject"].queryset = Subject.objects.filter(
                is_active=True
            ).order_by("grade_level", "name")
            self.fields["course"].queryset = Course.objects.all().order_by("title")

        # lesson is optional — keep full queryset, AJAX will narrow it
        self.fields["lesson"].required = False

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters.")
        return title

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file:
            return file

        _, ext = os.path.splitext(file.name.lower())
        if ext not in self.ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f"Unsupported file type '{ext}'. "
                f"Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        max_size = 50 * 1024 * 1024  # 50 MB
        if file.size > max_size:
            raise forms.ValidationError("File size cannot exceed 50 MB.")

        return file

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get("subject")
        course  = cleaned_data.get("course")
        lesson  = cleaned_data.get("lesson")

        # Course must belong to the chosen subject
        if course and subject and course.subject != subject:
            raise forms.ValidationError(
                "The selected course does not belong to the selected subject."
            )

        # Teacher must be assigned to the subject
        if self.user and self.user.role == "teacher" and subject:
            if not subject.teachers.filter(pk=self.user.pk).exists():
                raise forms.ValidationError(
                    "You are not assigned to the selected subject."
                )

        # Teacher must own the course
        if self.user and self.user.role == "teacher" and course:
            if course.teacher != self.user:
                raise forms.ValidationError(
                    "You can only upload documents for your own courses."
                )

        # Lesson must belong to the course
        if lesson and course and lesson.course != course:
            raise forms.ValidationError(
                "The selected lesson does not belong to the selected course."
            )

        return cleaned_data
