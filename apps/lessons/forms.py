from django import forms
from apps.courses.models import Course
from .models import Lesson


class LessonForm(forms.ModelForm):

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and user.role == "teacher":
            # Teacher can only create lessons for their own courses
            self.fields["course"].queryset = Course.objects.filter(
                teacher=user
            ).order_by("title")
        elif user and (user.role == "admin" or user.is_superuser):
            self.fields["course"].queryset = Course.objects.all().order_by("title")

    def clean_lesson_order(self):
        lesson_order = self.cleaned_data["lesson_order"]
        if lesson_order <= 0:
            raise forms.ValidationError("Lesson order must be greater than zero.")
        return lesson_order

    def clean_duration(self):
        duration = self.cleaned_data["duration"]
        if not duration:
            raise forms.ValidationError("Please enter the lesson duration.")
        return duration

    class Meta:
        model = Lesson
        fields = [
            "course",
            "title",
            "description",
            "thumbnail",
            "video",
            "video_url",
            "duration",
            "lesson_order",
            "is_preview",
            "status",
        ]
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Lesson Title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Lesson Description",
            }),
            "thumbnail": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/*",
            }),
            "video": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "video/*",
            }),
            "video_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://youtube.com/...",
            }),
            "duration": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 15 Minutes",
            }),
            "lesson_order": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
            }),
            "status": forms.Select(attrs={"class": "form-select"}),
            "is_preview": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
