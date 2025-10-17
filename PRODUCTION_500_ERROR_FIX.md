# 🔥 Production 500 Error Fix - Serviceman Profile Endpoint

## ❌ Problem
Getting 500 Server Error at:
```
https://serviceman-backend.onrender.com/api/users/servicemen/1/
```

## 🔍 Root Cause
The `ServicemanProfileSerializer` is trying to access the `skills` field (many-to-many relationship) that **doesn't exist in the production database yet** because migrations haven't been run after adding the Skill model.

```python
# This line causes the error in production:
class ServicemanProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)  # ← Skills table doesn't exist!
```

## ✅ Immediate Solution

### Option 1: Run Migrations on Render (Recommended)

1. **Access Render Dashboard**:
   - Go to https://dashboard.render.com
   - Select your ServiceMan Backend service

2. **Run Migrations**:
   - Go to "Shell" tab
   - Run these commands:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

   OR use the Manual Deploy with command:
   - Go to "Settings" → "Build & Deploy"
   - Add Build Command:
   ```bash
   pip install -r requirements.txt && python manage.py migrate
   ```

3. **Redeploy**:
   - Click "Manual Deploy" → "Deploy latest commit"

### Option 2: Make Serializer Migration-Safe (Quick Fix)

Update the serializer to handle missing skills gracefully:

```python
# apps/users/serializers.py

class ServicemanProfileSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of skill IDs to assign to serviceman"
    )
    
    def get_skills(self, obj):
        """Safely get skills, return empty list if field doesn't exist"""
        try:
            if hasattr(obj, 'skills'):
                return SkillSerializer(obj.skills.filter(is_active=True), many=True).data
            return []
        except Exception:
            return []
    
    class Meta:
        model = ServicemanProfile
        fields = [
            'user', 'category', 'skills', 'skill_ids', 'rating', 
            'total_jobs_completed', 'bio', 'years_of_experience', 
            'phone_number', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'rating', 'total_jobs_completed', 'created_at', 'updated_at']
```

## 🚀 Complete Deployment Steps

### Step 1: Create and Apply Migrations Locally

```bash
# In your local environment
cd /home/chegbe/Desktop/Projects/ServiceManBackend-main

# Create migrations
python manage.py makemigrations

# You should see something like:
# Migrations for 'users':
#   apps/users/migrations/0003_skill_servicemanprofile_skills.py
#     - Create model Skill
#     - Add field skills to servicemanprofile
```

### Step 2: Commit Migrations to Git

```bash
git add apps/users/migrations/
git add apps/users/models.py
git add apps/users/serializers.py
git add apps/users/views.py
git add apps/users/admin.py
git add apps/users/utils.py
git add templates/
git commit -m "Add Skill model and skills management system"
git push origin main
```

### Step 3: Deploy to Render

Render will automatically:
1. Detect the push to main branch
2. Pull latest code
3. Run migrations (if configured in build command)
4. Restart the service

**Ensure your Build Command includes migrations:**
```bash
pip install -r requirements.txt && python manage.py migrate
```

### Step 4: Verify Deployment

Test the endpoint:
```bash
curl https://serviceman-backend.onrender.com/api/users/servicemen/1/
```

Should return serviceman profile data!

## 🔧 Render Configuration

### Environment Variables
Ensure these are set in Render dashboard:

```bash
DATABASE_URL=<automatically-set-by-render>
SECRET_KEY=<your-secret-key>
DEBUG=False
ALLOWED_HOSTS=serviceman-backend.onrender.com
FRONTEND_URL=<your-frontend-url>

# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>

# Redis (if using)
REDIS_URL=<your-redis-url>
```

### Build Command
```bash
pip install -r requirements.txt && python manage.py migrate
```

### Start Command
```bash
gunicorn config.wsgi:application
```

## 🐛 Debugging on Render

### View Logs
1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. Look for migration errors or database errors

### Common Errors

**"relation does not exist"**
- Migrations haven't run
- Run: `python manage.py migrate` in Shell

**"no such table"**
- Database not created properly
- Check DATABASE_URL is set correctly

**"column does not exist"**
- Old migration issue
- Run migrations again

### Access Render Shell

1. Go to your service in Render
2. Click "Shell" tab
3. Run commands:
   ```bash
   python manage.py showmigrations
   python manage.py migrate
   python manage.py check
   ```

## 📋 Migration Files to Commit

Make sure these migration files exist and are committed:

```
apps/users/migrations/
├── __init__.py
├── 0001_initial.py
├── 0002_make_profile_fields_optional.py
└── 0003_skill_servicemanprofile_skills.py  ← NEW!
```

If `0003_skill_servicemanprofile_skills.py` doesn't exist, create it:

```bash
python manage.py makemigrations users
```

## ✅ Verification Checklist

After deployment, verify:

- [ ] Migrations ran successfully (check logs)
- [ ] No database errors in logs
- [ ] `/api/users/servicemen/1/` returns 200 (or 404 if user doesn't exist)
- [ ] Skills endpoints work: `/api/users/skills/`
- [ ] Can create skills as admin
- [ ] Can register serviceman with skills
- [ ] API docs accessible: `/api/docs/`

## 🎯 Quick Fix Script

Create a file `deploy_to_render.sh`:

```bash
#!/bin/bash

echo "🚀 Deploying ServiceMan Backend to Render..."

# Create migrations
echo "📦 Creating migrations..."
python manage.py makemigrations

# Add all changes
echo "📝 Adding changes to git..."
git add .

# Commit
echo "💾 Committing changes..."
git commit -m "Deploy: Add skills system and fix serializers"

# Push to trigger Render deploy
echo "🌐 Pushing to GitHub..."
git push origin main

echo "✅ Done! Check Render dashboard for deployment progress."
echo "🔗 https://dashboard.render.com"
```

Run it:
```bash
chmod +x deploy_to_render.sh
./deploy_to_render.sh
```

## 🆘 If Still Getting 500 Error

1. **Check serviceman exists**:
   ```bash
   # In Render shell
   python manage.py shell
   >>> from apps.users.models import User, ServicemanProfile
   >>> User.objects.filter(id=1).exists()
   >>> ServicemanProfile.objects.filter(user_id=1).exists()
   ```

2. **Create test serviceman**:
   ```bash
   curl -X POST https://serviceman-backend.onrender.com/api/users/create-test-servicemen/ \
     -H "Content-Type: application/json" \
     -d '{"category_id": 1}'
   ```

3. **Check different user**:
   ```bash
   curl https://serviceman-backend.onrender.com/api/users/servicemen/2/
   ```

## 📞 Additional Resources

- **Render Docs**: https://render.com/docs/databases
- **Django Migrations**: https://docs.djangoproject.com/en/4.2/topics/migrations/
- **Your API Docs**: https://serviceman-backend.onrender.com/api/docs/

---

**Status**: Ready to deploy  
**Action Required**: Run migrations on Render  
**ETA**: 2-5 minutes after deployment

