from django import forms
from django.utils import timezone

from .models import LiveClass
from apps.courses.models import Course


class LiveClassForm(forms.ModelForm):

    class Meta:

        model = LiveClass

        fields = [
            "course",
            "lesson",
            "title",
            "description",
            "platform",
            "meeting_link",
            "meeting_id",
            "passcode",
            "thumbnail",
            "start_datetime",
            "end_datetime",
            "duration",
            "maximum_students",
            "status",
            "is_recorded",
            "recording_url",
        ]

        widgets = {

            "course": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "lesson": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Live Class Title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Live class description",
                }
            ),

            "platform": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "meeting_link": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://meet.google.com/...",
                }
            ),

            "meeting_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Meeting ID",
                }
            ),

            "passcode": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Passcode",
                }
            ),

            "thumbnail": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "start_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),

            "end_datetime": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),

            "duration": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Duration in minutes",
                }
            ),

            "maximum_students": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Maximum students",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "is_recorded": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),

            "recording_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Recording URL (optional)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        if self.user:

            if self.user.role == "teacher":

                self.fields["course"].queryset = Course.objects.filter(
                    teacher=self.user
                )

            elif self.user.role == "admin":

                self.fields["course"].queryset = Course.objects.all()

    def clean_start_datetime(self):

        start = self.cleaned_data["start_datetime"]

        if start < timezone.now():

            raise forms.ValidationError(
                "Start time cannot be in the past."
            )

        return start

    def clean(self):

        cleaned_data = super().clean()

        start = cleaned_data.get("start_datetime")
        end = cleaned_data.get("end_datetime")
        duration = cleaned_data.get("duration")
        maximum_students = cleaned_data.get("maximum_students")

        if start and end:

            if end <= start:

                raise forms.ValidationError(
                    "End time must be after the start time."
                )

        if duration is not None:

            if duration <= 0:

                raise forms.ValidationError(
                    "Duration must be greater than zero."
                )

        if maximum_students is not None:

            if maximum_students <= 0:

                raise forms.ValidationError(
                    "Maximum students must be greater than zero."
                )

        return cleaned_data