from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [

    # Homepage
    path("", views.home, name="home"),

    # Authentication
    path("register/", views.register_view, name="register"),
    
    path(
        "registration-pending/",
        views.registration_pending,
        name="registration_pending"
    ),
    
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Profile
    path("profile/", views.profile_view, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),

    # Forgot password — OTP flow
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    path("verify-otp/", views.verify_otp_view, name="verify_otp"),
    path("set-new-password/", views.set_new_password_view, name="set_new_password"),
]
