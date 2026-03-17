from django.contrib.auth import views as auth_views
from django.conf import settings
from django.urls import path

from .forms import LoginForm
from .views import (
    firebase_session_login_view,
    firebase_session_signup_view,
    forgot_password_request_view,
    forgot_password_reset_view,
    forgot_password_verify_view,
    signup_view,
)

app_name = "accounts"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
            extra_context={
                "firebase_auth_enabled": settings.FIREBASE_AUTH_ENABLED,
                "firebase_web_config": settings.FIREBASE_WEB_CONFIG,
            },
        ),
        name="login",
    ),
    path("forgot-password/", forgot_password_request_view, name="forgot-password-request"),
    path("forgot-password/verify/", forgot_password_verify_view, name="forgot-password-verify"),
    path("forgot-password/reset/", forgot_password_reset_view, name="forgot-password-reset"),
    path("firebase-signup/", firebase_session_signup_view, name="firebase-signup"),
    path("firebase-login/", firebase_session_login_view, name="firebase-login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
