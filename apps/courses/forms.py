from django import forms
from .models import Course
from apps.accounts.models import User
from apps.subjects.models import Subject


class CourseForm(forms.ModelForm):

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and user.role == "teacher":
            # Teacher field — locked to themselves, rendered as hidden in template
            self.fields["teacher"].queryset = User.objects.filter(pk=user.pk)
            self.fields["teacher"].initial = user
            self.fields["teacher"].widget = forms.HiddenInput()

            # Subject dropdown — only this teacher's assigned subjects
            self.fields["subject"].queryset = Subject.objects.filter(
                teachers=user, is_active=True
            ).order_by("grade_level", "name")

        else:
            # Admin — sees all teachers and all subjects
            self.fields["teacher"].queryset = User.objects.filter(
                role="teacher"
            ).order_by("first_name", "last_name")

            self.fields["subject"].queryset = Subject.objects.filter(
                is_active=True
            ).order_by("grade_level", "name")

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    class Meta:
        model = Course
        fields = [
            "subject",
            "teacher",
            "title",
            "description",
            "thumbnail",
            "price",
            "level",
            "status",
        ]
        widgets = {
            "subject": forms.Select(attrs={
                "class": "form-select",
            }),
            "teacher": forms.Select(attrs={
                "class": "form-select",
            }),
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Course Title",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Course Description",
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "step": "0.01",
            }),
            "level": forms.Select(attrs={
                "class": "form-select",
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
            "thumbnail": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
        }
