# Deployment Guide: Render

This guide explains how to deploy Activityhub on Render.

## Prerequisites

1. **GitHub Repository**: Push your code to GitHub (Render integrates with GitHub)
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **PostgreSQL Database**: Render will create this automatically

## Step 1: Update Django Settings for Production

Your `settings.py` is already partially configured to work with environment variables. Make sure to update it for production use:

### Key configurations needed:

```python
# These are already in your settings.py - verify they exist:
SECRET_KEY = os.getenv("SECRET_KEY", "your-production-secret-key")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1").split(",")]
```

## Step 2: Update requirements.txt

Add `whitenoise` for efficient static file serving:

```bash
pip freeze > requirements.txt
# Then manually add if not present:
# whitenoise>=6.6.0
# psycopg2-binary>=2.9.9
```

## Step 3: Update settings.py for Production

Add these settings for production:

### Add to the top (after imports):
```python
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"
```

### Modify MIDDLEWARE:
```python
MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add this first
    "django.middleware.security.SecurityMiddleware",
    # ... rest of middleware
]
```

### Update STATICFILES settings:
```python
if IS_PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Add Security Settings for Production:
```python
if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        "default-src": ("'self'",),
    }
```

### Database Configuration (for PostgreSQL):
```python
import dj_database_url

if IS_PRODUCTION and os.getenv("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

## Step 4: Create/Update requirements.txt

Update your requirements.txt to include production dependencies:

```bash
Django>=5.0
requests>=2.31
beautifulsoup4>=4.12
python-dotenv>=1.0
lxml>=5.1
Pillow>=10.0
django-allauth>=65.0
PyJWT>=2.8
cryptography>=43.0
firebase-admin>=6.5
openpyxl>=3.1
gunicorn>=22.0
whitenoise>=6.6.0
psycopg2-binary>=2.9.9
dj-database-url>=2.0
```

## Step 5: Deploy on Render

### Option A: Using render.yaml (Recommended)

1. Commit `render.yaml` and `build.sh` to your GitHub repository
2. Go to [render.com/dashboard](https://render.com/dashboard)
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Select the repository containing this project
6. Choose `render.yaml` as the blueprint file
7. Set your environment variables:
   - `SECRET_KEY`: Generate a strong random key
   - `ALLOWED_HOSTS`: Your Render domain (e.g., `activityhub.onrender.com`)
   - `FIREBASE_API_KEY`, `FIREBASE_AUTH_DOMAIN`, etc.: Copy from your .env
   - `EMAIL_BACKEND`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Your email config
8. Click "Deploy"

### Option B: Manual Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set these values:
   - **Name**: activityhub
   - **Environment**: Python 3.11
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```bash
     gunicorn social_hub.wsgi:application --bind 0.0.0.0:$PORT --workers 3
     ```

4. Add Environment Variables:
   ```
   PYTHON_VERSION=3.11
   DEBUG=false
   SECRET_KEY=<your-secret-key>
   ALLOWED_HOSTS=activityhub.onrender.com,www.activityhub.onrender.com
   DATABASE_URL=<Render will provide this if you add PostgreSQL>
   ENVIRONMENT=production
   FIREBASE_API_KEY=<from your Firebase project>
   FIREBASE_AUTH_DOMAIN=<from your Firebase project>
   FIREBASE_WEB_PROJECT_ID=<from your Firebase project>
   FIREBASE_APP_ID=<from your Firebase project>
   FIREBASE_SERVICE_ACCOUNT_PATH=<path or JSON>
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=true
   EMAIL_HOST_USER=<your-email>
   EMAIL_HOST_PASSWORD=<your-app-password>
   ```

5. Click "Create Web Service"

## Step 6: Add PostgreSQL Database (if using manual deployment)

1. In your Render dashboard, click "New +" → "PostgreSQL"
2. Create a new database instance
3. Copy the connection string
4. Add it to your web service as `DATABASE_URL`

## Step 7: Upload Firebase Service Account

The Firebase credentials need to be set as environment variables. In render.yaml or as env vars:

```
FIREBASE_PROJECT_ID=activityhub-792f7
FIREBASE_PRIVATE_KEY=<your-private-key>
FIREBASE_CLIENT_EMAIL=<your-service-account-email>
```

Or upload the JSON file directly in Render's file system if available.

## Step 8: Initial Setup on Production

After deployment, open the Render shell and run:

```bash
python manage.py createsuperuser
```

Then visit your app and test login/signup.

## Environmental Variables Summary

| Variable | Value | Example |
|----------|-------|---------|
| DEBUG | false | false |
| SECRET_KEY | Strong random key | (auto-generated) |
| ALLOWED_HOSTS | Your domain | activityhub.onrender.com |
| DATABASE_URL | PostgreSQL connection | postgresql://... |
| ENVIRONMENT | production | production |
| FIREBASE_* | From Firebase console | See Firebase section |
| EMAIL_* | SMTP config | See Email section |

## Troubleshooting

### Static Files Not Loading
- Run: `python manage.py collectstatic --noinput`
- Check `STATIC_ROOT` and `STATIC_URL` in settings
- Add whitenoise to MIDDLEWARE

### Database Connection Issues
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL credentials in Render dashboard
- Ensure `psycopg2-binary` is in requirements.txt

### Firebase Authentication Not Working
- Verify FIREBASE_* environment variables
- Check service account JSON is valid
- Update ALLOWED_HOSTS with your Render domain

### Static IP Whitelist
If Render runs in a private network:
1. Go to Database settings
2. Add Render's IP to whitelist
3. Or set `ipWhitelist: []` in render.yaml

## Production Checklist

- [ ] Update `settings.py` for production
- [ ] Add whitenoise to requirements.txt
- [ ] Update ALLOWED_HOSTS with your domain
- [ ] Set strong SECRET_KEY
- [ ] Configure PostgreSQL database
- [ ] Set all Firebase environment variables
- [ ] Configure email backend
- [ ] Test local deployment first: `gunicorn social_hub.wsgi:application`
- [ ] Create superuser on production
- [ ] Enable HTTPS (Render does this automatically)
- [ ] Monitor logs and performance

## Support

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/
- WhiteNoise: http://whitenoise.evans.io/

