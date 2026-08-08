from django.contrib import messages
from django.contrib.auth import  authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import (
    RegisterForm, UpdateProfileForm,
    ForgotPasswordForm, OTPVerifyForm, SetNewPasswordForm
)
from .models import User, PasswordResetOTP
from .email_utils import send_otp_email

def home(request):
    # Redirect logged-in users straight to their dashboard
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    # Pass registered teachers to show on landing page
    teachers = User.objects.filter(
        role="teacher",
        is_active=True,
    ).order_by("first_name", "last_name")[:20]

    return render(request, "home.html", {"teachers": teachers})

from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import RegisterForm


def register_view(request):

    if request.method == "POST":

        form = RegisterForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            user = form.save(commit=False)

            # New registration must wait for admin approval
            user.approval_status = "pending"

            user.save()

            messages.success(
                request,
                "Registration submitted successfully. "
                "Please wait for administrator approval "
                "before logging in."
            )

            return redirect(
                "accounts:registration_pending"
            )

    else:

        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )
    

def registration_pending(request):

    return render(
        request,
        "accounts/pending.html"
    )
    

    

def login_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # -------------------------------
            # CHECK REGISTRATION APPROVAL
            # -------------------------------

            if user.approval_status == "pending":

                messages.warning(
                    request,
                    "Your registration is waiting "
                    "for administrator approval."
                )

                return redirect("accounts:login")

            if user.approval_status == "rejected":

                messages.error(
                    request,
                    "Your registration request has "
                    "been rejected by the administrator."
                )

                return redirect("accounts:login")

            # -------------------------------
            # USER IS APPROVED
            # -------------------------------

            if user.approval_status == "approved":

                login(request, user)

                messages.success(
                    request,
                    f"Welcome back {user.first_name}!"
                )

                return redirect("dashboard:home")

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(
        request,
        "accounts/login.html"
    )
    

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect("accounts:login")

@login_required
def profile_view(request):
    return render(
        request,
        "accounts/profile.html",
        {
            "user": request.user
        }
    )
    
    
@login_required
def edit_profile(request):

    if request.method == "POST":

        form = UpdateProfileForm(
            request.POST,
            request.FILES,
            instance=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("accounts:profile")

    else:

        form = UpdateProfileForm(instance=request.user)

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "form":form
        }
    )


# ─── Forgot Password (OTP flow) ───────────────────────────────────────────────

def forgot_password_view(request):
    """Step 1 — User enters their email, system sends a 4-digit OTP."""
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Don't reveal whether the email exists — just show success and stop
                messages.success(
                    request,
                    f"If {email} is registered, a reset code has been sent."
                )
                return render(request, "accounts/forgot_password.html", {"form": ForgotPasswordForm()})

            otp = PasswordResetOTP.generate_for(user)

            try:
                send_otp_email(
                    recipient_email=email,
                    recipient_name=user.first_name or user.username,
                    otp_code=otp.code,
                )
                messages.success(
                    request,
                    f"A 4-digit reset code has been sent to {email}. "
                    f"Please check your inbox (and spam folder)."
                )
            except Exception as e:
                messages.error(
                    request,
                    "Failed to send the reset email. Please try again later."
                )
                return render(request, "accounts/forgot_password.html", {"form": form})

            request.session["otp_user_id"] = user.pk
            return redirect("accounts:verify_otp")
    else:
        form = ForgotPasswordForm()

    return render(request, "accounts/forgot_password.html", {"form": form})


def verify_otp_view(request):
    """Step 2 — User enters the 4-digit OTP."""
    user_id = request.session.get("otp_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please start again.")
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"]
            try:
                otp = PasswordResetOTP.objects.filter(
                    user_id=user_id,
                    code=code,
                    is_used=False
                ).latest("created_at")
            except PasswordResetOTP.DoesNotExist:
                messages.error(request, "Invalid code. Please try again.")
                return render(request, "accounts/verify_otp.html", {"form": form})

            if otp.is_expired():
                messages.error(request, "This code has expired. Please request a new one.")
                return redirect("accounts:forgot_password")

            # Mark OTP verified in session, invalidate the code
            otp.is_used = True
            otp.save()
            request.session["otp_verified"] = True

            return redirect("accounts:set_new_password")
    else:
        form = OTPVerifyForm()

    return render(request, "accounts/verify_otp.html", {"form": form})


def set_new_password_view(request):
    """Step 3 — User sets a new password after OTP is verified."""
    user_id = request.session.get("otp_user_id")
    otp_verified = request.session.get("otp_verified")

    if not user_id or not otp_verified:
        messages.error(request, "Session expired. Please start again.")
        return redirect("accounts:forgot_password")

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                messages.error(request, "User not found.")
                return redirect("accounts:forgot_password")

            user.password = make_password(form.cleaned_data["new_password1"])
            user.save()

            # Clear session keys
            del request.session["otp_user_id"]
            del request.session["otp_verified"]

            messages.success(
                request,
                "Password reset successful. You can now log in with your new password."
            )
            return redirect("accounts:login")
    else:
        form = SetNewPasswordForm()

    return render(request, "accounts/set_new_password.html", {"form": form})