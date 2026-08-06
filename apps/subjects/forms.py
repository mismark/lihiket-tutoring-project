from django import forms
from django.conf import settings

from apps.accounts.constants import GRADE_LEVEL_CHOICES
from .models import Subject


class SubjectForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Explicitly limit teachers queryset to role == teacher
        User = settings.AUTH_USER_MODEL
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        self.fields["teachers"].queryset = UserModel.objects.filter(
            role="teacher"
        ).order_by("first_name", "last_name", "username")

    class Meta:
        model = Subject
        fields = [
            "name",
            "grade_level",
            "code",
            "description",
            "image",
            "icon",
            "color",
            "teachers",
            "is_active",
        ]

        widgets = {

            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Mathematics, English",
            }),

            "grade_level": forms.Select(attrs={
                "class": "form-select",
            }),

            "code": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. MATH-G1, ENG-G10",
            }),

            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Enter subject description",
            }),

            "image": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),

            "icon": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. fas fa-book",
            }),

            "color": forms.TextInput(attrs={
                "class": "form-control",
                "type": "color",
            }),

            # Rendered as checkboxes in the template — widget kept minimal
            "teachers": forms.CheckboxSelectMultiple(),

            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name", "").strip()
        grade_level = cleaned_data.get("grade_level", "")

        if name and grade_level:
            qs = Subject.objects.filter(
                name__iexact=name,
                grade_level=grade_level,
            )
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(
                    f'A subject named "{name}" already exists for '
                    f'{dict(GRADE_LEVEL_CHOICES[1:]).get(grade_level, grade_level)}.'
                )

        return cleaned_data

    def clean_code(self):
        code = self.cleaned_data["code"].strip().upper()
        qs = Subject.objects.filter(code__iexact=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "A subject with this code already exists."
            )
        return code
