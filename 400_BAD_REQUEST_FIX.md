# 🚨 Django 400 Bad Request Fix

## The Problem
Django is returning 400 Bad Request for all endpoints, which suggests a configuration issue.

## ✅ What I Fixed

1. **Added fallback values** for SECRET_KEY and ALLOWED_HOSTS
2. **Added database fallback** to SQLite if DATABASE_URL is missing
3. **Added health check endpoint** for debugging
4. **Made DEBUG configurable** via environment variable

## 🚀 Deploy the Fix

```bash
git add .
git commit -m "Fix Django 400 Bad Request - add fallbacks and health check"
git push origin main
```

## 🧪 Test the Health Check

After deployment, test the health check endpoint:

```bash
curl https://serviceman-backend.onrender.com/api/users/health/
```

This should return:
```json
{
    "status": "healthy",
    "message": "API is working",
    "timestamp": "2025-10-07"
}
```

## 🔧 Environment Variables Check

Make sure these are set in Render:

```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=serviceman-backend.onrender.com
DATABASE_URL=postgresql://postgres:YbXqOgigypQCYVLHkHjqKltKUnXbfLwH@postgres.railway.internal:5432/railway
FRONTEND_URL=http://localhost:3000
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DJANGO_SETTINGS_MODULE=config.settings.production
```

## 🎯 Debugging Steps

1. **Test health check** first
2. **If health check works**, the issue is with database
3. **If health check fails**, the issue is with Django configuration

## 📞 Alternative: Use Render Shell

If the API endpoints still don't work:

1. **Go to Render dashboard**
2. **Click on your service**
3. **Go to "Shell" tab**
4. **Run these commands:**
   ```bash
   python manage.py migrate
   python manage.py runserver 0.0.0.0:10000
   ```

## 🧪 Test Sequence

```bash
# 1. Test health check
curl https://serviceman-backend.onrender.com/api/users/health/

# 2. If health check works, test categories
curl https://serviceman-backend.onrender.com/api/services/categories/

# 3. If categories work, run migrations
curl -X POST https://serviceman-backend.onrender.com/api/users/run-migrations/
```

The health check endpoint should work even without a database! 🎉
