# Deployment Checklist for Render

## Before Deployment

- [ ] Push all changes to GitHub
  ```bash
  git add .
  git commit -m "Prepare for Render deployment"
  git push origin main
  ```

- [ ] Test locally with production settings
  ```bash
  ENVIRONMENT=production DEBUG=false python manage.py runserver
  ```

- [ ] Verify `render.yaml` exists in root directory
- [ ] Verify `build.sh` exists in root directory
- [ ] Verify requirements.txt has whitenoise and psycopg2-binary

## Render Deployment Steps

### 1. Create Render Account
- Go to https://render.com
- Sign up and verify email
- Connect GitHub account

### 2. Deploy Using Blueprint (RECOMMENDED)
- Click "New" → "Blueprint"
- Select your repository
- Choose `render.yaml` as blueprint
- Set environment variables (see below)
- Click "Deploy"

### 3. Set Environment Variables
Copy these into Render's environment settings:

```
DEBUG=false
ENVIRONMENT=production
ALLOWED_HOSTS=your-app.onrender.com,www.your-app.onrender.com
SECRET_KEY=<generate a strong random key, or let Render auto-generate>
DATABASE_URL=<will be auto-set by PostgreSQL service>
SITE_ID=1

# Firebase Config (from your Firebase project)
FIREBASE_AUTH_ENABLED=true
FIREBASE_API_KEY=AIzaSyAFMNQOq-EH16VN-XZWTViiRg4tx0xIzcE
FIREBASE_AUTH_DOMAIN=activityhub-792f7.firebaseapp.com
FIREBASE_WEB_PROJECT_ID=activityhub-792f7
FIREBASE_APP_ID=1:184476752065:web:92b18cae8c5823b7051c40
FIREBASE_PROJECT_ID=activityhub-792f7
FIREBASE_CLIENT_EMAIL=<from service account JSON>
FIREBASE_PRIVATE_KEY=<from service account JSON, with \n preserved>

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Google OAuth (optional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### 4. Firebase Service Account Setup

If using Firebase authentication:
1. Go to Firebase Console
2. Project Settings → Service Accounts
3. Download JSON file
4. Extract these values to environment variables:
   - `FIREBASE_PROJECT_ID`: from JSON `project_id`
   - `FIREBASE_CLIENT_EMAIL`: from JSON `client_email`
   - `FIREBASE_PRIVATE_KEY`: from JSON `private_key` (keep `\n`)

### 5. Monitor Deployment

- [ ] Check Render dashboard for build status
- [ ] View logs for any errors
- [ ] Wait for "Live" status
- [ ] Test the app URL

### 6. Post-Deployment Setup

Once deployed, access Render shell:

```bash
# Create superuser
python manage.py createsuperuser

# Run migrations manually if needed
python manage.py migrate

# Check static files
python manage.py collectstatic --noinput
```

## Common Issues & Solutions

### Issue: Database migration fails
**Solution**: Ensure DATABASE_URL is set and PostgreSQL is running
```bash
# Check migration status
python manage.py showmigrations
python manage.py migrate
```

### Issue: Static files not loading (404 on CSS/JS)
**Solution**: 
```bash
# Rebuild static files
python manage.py collectstatic --noinput
# Ensure STATICFILES_STORAGE is set to whitenoise
```

### Issue: Firebase authentication not working
**Solution**: 
- Verify all FIREBASE_* variables are set correctly
- Check ALLOWED_HOSTS includes your Render domain
- Ensure FIREBASE_PRIVATE_KEY has newlines preserved

### Issue: Email not sending
**Solution**:
- If using Gmail, use App Password (not your Gmail password)
- Generate app password: https://myaccount.google.com/apppasswords
- Set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

### Issue: CSRF token errors
**Solution**: Update ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS
```python
CSRF_TRUSTED_ORIGINS = [
    "https://your-app.onrender.com",
    "https://*.onrender.com"
]
```

## Monitoring & Maintenance

After deployment:

- [ ] Monitor error logs regularly
- [ ] Set up error tracking (Sentry recommended)
- [ ] Check database usage
- [ ] Monitor worker memory
- [ ] Set up uptime monitoring

### Useful Commands

```bash
# View logs
# Available in Render dashboard → Logs

# Connect to production shell
# Available in Render dashboard → Shell

# Restart the app
# Available in Render dashboard → Manual Deploy
```

## Database Backups

Render PostgreSQL backup options:
1. Automatic backups (free tier: 7 days)
2. Manual backups via dashboard
3. Export PostgreSQL data:
   ```bash
   pg_dump $DATABASE_URL > backup.sql
   ```

## Performance Tips

1. Enable caching headers
2. Use CDN for static files
3. Optimize database queries
4. Monitor build logs for warnings
5. Use production-grade WSGI settings (gunicorn workers, threads)

## Next Steps

- [ ] Set custom domain (if applicable)
- [ ] Enable SSL/TLS (automatic on Render)
- [ ] Set up monitoring & alerts
- [ ] Create deployment documentation for team
- [ ] Schedule regular backups
- [ ] Plan scaling strategy

## Support Resources

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/5.0/howto/deployment/
- Firebase Docs: https://firebase.google.com/docs
- WhiteNoise: http://whitenoise.evans.io/

