from datetime import timedelta
import json
from pathlib import Path
import secrets

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials as firebase_credentials
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone

from .forms import ForgotPasswordRequestForm, ResetPasswordWithCodeForm, SignUpForm, VerifyResetCodeForm
from .models import PasswordResetCode

User = get_user_model()


def _ensure_firebase_app():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    service_account_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
    if service_account_path:
        file_path = Path(service_account_path)
        if not file_path.is_absolute():
            file_path = Path(settings.BASE_DIR) / service_account_path
        cred = firebase_credentials.Certificate(str(file_path))
        return firebase_admin.initialize_app(cred)

    if settings.FIREBASE_PROJECT_ID and settings.FIREBASE_CLIENT_EMAIL and settings.FIREBASE_PRIVATE_KEY:
        cred = firebase_credentials.Certificate(
            {
                "type": "service_account",
                "project_id": settings.FIREBASE_PROJECT_ID,
                "client_email": settings.FIREBASE_CLIENT_EMAIL,
                "private_key": settings.FIREBASE_PRIVATE_KEY,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
        return firebase_admin.initialize_app(cred)

    raise ValueError("Firebase admin credentials are not configured.")


def _build_unique_username(email: str, uid: str) -> str:
    if email:
        base = (email.split("@")[0] or "firebaseuser").strip().lower()
    else:
        base = f"firebase_{uid[:12]}"
    cleaned = "".join(ch for ch in base if ch.isalnum() or ch == "_")[:24] or "firebaseuser"
    candidate = cleaned
    suffix = 1
    while User.objects.filter(username=candidate).exclude(email__iexact=email or "").exists():
        candidate = f"{cleaned[:20]}{suffix}"
        suffix += 1
    return candidate


def _upsert_local_user_from_firebase(email: str, uid: str, display_name: str, password: str = ""):
    user = None
    if email:
        user = User.objects.filter(email__iexact=email).first()

    if not user:
        username = _build_unique_username(email, uid)
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=display_name[:30],
            last_name="",
        )

    if display_name and not user.first_name:
        user.first_name = display_name[:30]
        user.save(update_fields=["first_name"])

    # Keep local credentials synchronized in Django's SQLite user table.
    if password:
        user.set_password(password)
        user.save(update_fields=["password"])

    return user


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("searcher:posts")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Welcome aboard. Your account has been created.")
            return redirect("searcher:posts")
    else:
        form = SignUpForm()

    return render(
        request,
        "accounts/signup.html",
        {
            "form": form,
            "firebase_auth_enabled": settings.FIREBASE_AUTH_ENABLED,
            "firebase_web_config": settings.FIREBASE_WEB_CONFIG,
        },
    )


@require_POST
def firebase_session_signup_view(request):
    if not settings.FIREBASE_AUTH_ENABLED:
        return JsonResponse({"ok": False, "error": "Firebase auth is disabled."}, status=503)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid request payload."}, status=400)

    id_token = (payload.get("idToken") or "").strip()
    password = (payload.get("password") or "").strip()
    redirect_to = (payload.get("next") or "").strip() or "/search/posts/"

    if not id_token:
        return JsonResponse({"ok": False, "error": "idToken is required."}, status=400)
    if not password:
        return JsonResponse({"ok": False, "error": "Password is required."}, status=400)

    try:
        _ensure_firebase_app()
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception:
        return JsonResponse({"ok": False, "error": "Token verification failed."}, status=401)

    email = (decoded.get("email") or "").strip().lower()
    uid = (decoded.get("uid") or "").strip()
    display_name = (decoded.get("name") or "").strip()

    if not uid or not email:
        return JsonResponse({"ok": False, "error": "Firebase user email or UID missing."}, status=400)

    user = _upsert_local_user_from_firebase(email, uid, display_name, password=password)
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    messages.success(request, "Account created successfully! Welcome to ActivityHub.")
    return JsonResponse({"ok": True, "redirect": redirect_to})


def forgot_password_request_view(request):
    if request.method == "POST":
        form = ForgotPasswordRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            user = User.objects.filter(email__iexact=email).first()

            if user:
                code = f"{secrets.randbelow(1000000):06d}"
                PasswordResetCode.objects.filter(user=user, email__iexact=email, used_at__isnull=True).update(
                    used_at=timezone.now()
                )
                PasswordResetCode.objects.create(
                    user=user,
                    email=email,
                    code=code,
                    expires_at=timezone.now() + timedelta(minutes=15),
                )
                send_mail(
                    subject="Your ActivityHub password reset code",
                    message=(
                        f"Your verification code is: {code}\n\n"
                        "This code expires in 15 minutes."
                    ),
                    from_email=None,
                    recipient_list=[email],
                    fail_silently=False,
                )

            request.session["pwd_reset_email"] = email
            messages.success(request, "If the email exists, a reset code has been sent.")
            return redirect("accounts:forgot-password-verify")
    else:
        form = ForgotPasswordRequestForm(initial={"email": request.session.get("pwd_reset_email", "")})

    return render(request, "accounts/forgot_password_request.html", {"form": form})


def forgot_password_verify_view(request):
    if request.method == "POST":
        form = VerifyResetCodeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].strip().lower()
            code = form.cleaned_data["code"]
            reset_code = (
                PasswordResetCode.objects.select_related("user")
                .filter(email__iexact=email, code=code, used_at__isnull=True, expires_at__gt=timezone.now())
                .first()
            )
            if reset_code:
                request.session["pwd_reset_email"] = email
                request.session["pwd_reset_code_id"] = reset_code.id
                return redirect("accounts:forgot-password-reset")
            messages.error(request, "Invalid or expired code.")
    else:
        form = VerifyResetCodeForm(initial={"email": request.session.get("pwd_reset_email", "")})

    return render(request, "accounts/forgot_password_verify.html", {"form": form})


def forgot_password_reset_view(request):
    code_id = request.session.get("pwd_reset_code_id")
    email = request.session.get("pwd_reset_email")
    if not code_id or not email:
        messages.error(request, "Start with the email verification step.")
        return redirect("accounts:forgot-password-request")

    reset_code = (
        PasswordResetCode.objects.select_related("user")
        .filter(id=code_id, email__iexact=email, used_at__isnull=True, expires_at__gt=timezone.now())
        .first()
    )
    if not reset_code:
        messages.error(request, "Your code has expired. Request a new one.")
        return redirect("accounts:forgot-password-request")

    if request.method == "POST":
        form = ResetPasswordWithCodeForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["new_password1"]
            try:
                validate_password(password, user=reset_code.user)
            except ValidationError as exc:
                form.add_error("new_password1", " ".join(exc.messages))
            else:
                if settings.FIREBASE_AUTH_ENABLED and reset_code.user.email:
                    try:
                        _ensure_firebase_app()
                        fb_user = firebase_auth.get_user_by_email(reset_code.user.email)
                        firebase_auth.update_user(fb_user.uid, password=password)
                    except Exception:
                        messages.error(request, "Unable to update Firebase password. Please try again.")
                        return render(request, "accounts/forgot_password_reset.html", {"form": form})

                reset_code.user.set_password(password)
                reset_code.user.save(update_fields=["password"])
                reset_code.used_at = timezone.now()
                reset_code.save(update_fields=["used_at"])
                request.session.pop("pwd_reset_code_id", None)
                request.session.pop("pwd_reset_email", None)
                messages.success(request, "Password updated. You can now log in.")
                return redirect("accounts:login")
    else:
        form = ResetPasswordWithCodeForm()

    return render(request, "accounts/forgot_password_reset.html", {"form": form})


@require_POST
def firebase_session_login_view(request):
    if not settings.FIREBASE_AUTH_ENABLED:
        return JsonResponse({"ok": False, "error": "Firebase auth is disabled."}, status=503)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "Invalid request payload."}, status=400)

    id_token = (payload.get("idToken") or "").strip()
    password = (payload.get("password") or "").strip()
    redirect_to = (payload.get("next") or "").strip() or "/search/posts/"

    if not id_token:
        return JsonResponse({"ok": False, "error": "idToken is required."}, status=400)

    try:
        _ensure_firebase_app()
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception:
        return JsonResponse({"ok": False, "error": "Token verification failed."}, status=401)

    email = (decoded.get("email") or "").strip().lower()
    uid = (decoded.get("uid") or "").strip()
    display_name = (decoded.get("name") or "").strip()

    if not uid:
        return JsonResponse({"ok": False, "error": "Firebase UID missing."}, status=400)

    user = _upsert_local_user_from_firebase(email, uid, display_name, password=password)
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    messages.success(request, f"Welcome back, {user.first_name or user.username}!")
    return JsonResponse({"ok": True, "redirect": redirect_to})
