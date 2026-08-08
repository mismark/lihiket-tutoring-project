from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User
from .constants import GRADE_LEVEL_CHOICES



class RegisterForm(UserCreationForm):

    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "First Name"
        })
    )

    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Last Name"
        })
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username"
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email Address"
        })
    )

    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Phone Number"
        })
    )

    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "id_role"
        })
    )
    
    

    grade_level = forms.ChoiceField(
        required=False,
        choices=GRADE_LEVEL_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-select",
            "id": "id_grade_level"
        })
    )

    cv_document = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "id": "id_cv_document",
            "accept": ".pdf,.doc,.docx"
        }),
        help_text="Upload your CV (PDF, DOC or DOCX). Required for teachers."
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control"
        })
    )

    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Tell us about yourself"
        })
    )

    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date"
        })
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Address"
        })
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password"
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm Password"
        })
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "role",
            "grade_level",
            "cv_document",
            "profile_picture",
            "bio",
            "date_of_birth",
            "address",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get("role")

        # Only save grade_level for students
        if role != "student":
            user.grade_level = None

        # Only save cv_document for teachers
        if role != "teacher":
            user.cv_document = None

        if commit:
            user.save()
        return user


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter your registered email"
        })
    )


class OTPVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=4,
        min_length=4,
        widget=forms.TextInput(attrs={
            "class": "form-control text-center",
            "placeholder": "Enter 4-digit code",
            "maxlength": "4",
            "autocomplete": "off"
        })
    )


class SetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "New Password"
        })
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm New Password"
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password"
        })
    )
class UpdateProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "address",
            "bio",
            "grade_level",
            "profile_picture",
        ]

        widgets = {

            "first_name": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "last_name": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "email": forms.EmailInput(attrs={
                "class":"form-control"
            }),

            "phone": forms.TextInput(attrs={
                "class":"form-control"
            }),

            "date_of_birth": forms.DateInput(attrs={
                "class":"form-control",
                "type":"date"
            }),

            "address": forms.Textarea(attrs={
                "class":"form-control",
                "rows":3
            }),

            "bio": forms.Textarea(attrs={
                "class":"form-control",
                "rows":4
            }),

            "grade_level": forms.Select(attrs={
                "class":"form-select",
                "id":"id_grade_level"
            }),

            "profile_picture": forms.FileInput(attrs={
                "class":"form-control",
                "id":"imageInput"
            }),

        }    
        
        
        