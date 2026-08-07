from django import forms
from apps.accounts.models import User


class StudentForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "address",
            "grade_level",
            "profile_picture",
        ]

class TeacherForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "address",
            "profile_picture",
        ]