# 🔥 Complete Guide: Fix 500 Errors on Production

## 🚨 Current Situation

**Problem**: Getting 500 errors on these endpoints in production:
- `GET /api/users/servicemen/`
- `GET /api/users/servicemen/1/`
- `GET /api/services/categories/1/servicemen/`

**Root Cause**: Database doesn't have new fields added to models

**Status**: ✅ Code is fixed locally, ⏳ Need to deploy to production

---

## ✅ Solution (2 Options)

### Option 1: Deploy Code Fix (Recommended - No Migrations Needed)

This makes endpoints work **immediately** without requiring migrations.

#### Step 1: Verify Changes Are Committed
```bash
cd /home/chegbe/Desktop/Projects/ServiceManBackend-main
git status
```

If you see modified files, commit them:
```bash
git add .
git commit -m "Fix: Make all serializers migration-safe for production"
```

#### Step 2: Push to GitHub
```bash
git push origin main
```

#### Step 3: Wait for Render to Deploy
- Render auto-detects the push (30 seconds)
- Builds and deploys (2-3 minutes)
- Watch at: https://dashboard.render.com

#### Step 4: Test
```bash
curl https://serviceman-backend.onrender.com/api/users/servicemen/
```

Should return 200 OK with data!

---

### Option 2: Run Migrations First (Full Features)

This gives you all features but requires database changes.

#### Step 1: Access Render Shell
1. Go to https://dashboard.render.com
2. Select your `serviceman-backend` service
3. Click **Shell** tab

#### Step 2: Run Migrations
```bash
# In Render Shell:
python manage.py makemigrations
python manage.py migrate
```

#### Step 3: Create Sample Data (If Needed)
```bash
# Check if servicemen exist
python manage.py shell
>>> from apps.users.models import User
>>> User.objects.filter(user_type='SERVICEMAN').count()

# If 0, create test servicemen
>>> exit()

# Use the test endpoint
curl -X POST https://serviceman-backend.onrender.com/api/users/create-test-servicemen/ \
  -H "Content-Type: application/json" \
  -d '{"category_id": 1}'
```

#### Step 4: Approve Servicemen
```bash
python manage.py shell
>>> from apps.users.models import ServicemanProfile
>>> from django.utils import timezone
>>> ServicemanProfile.objects.update(is_approved=True, approved_at=timezone.now())
>>> exit()
```

#### Step 5: Test
```bash
curl https://serviceman-backend.onrender.com/api/users/servicemen/
```

---

## 🎯 Recommended Approach

**Do Option 1 First** (Deploy code fix):
- ✅ Endpoints work immediately
- ✅ No database changes needed
- ✅ Zero downtime
- ✅ Can run migrations later

**Then Option 2 Later** (Run migrations):
- ✅ When you're ready
- ✅ Adds full features
- ✅ Skills, approval system, etc.

---

## 🧪 Detailed Testing Steps

### After Deploying Code Fix

#### Test 1: List All Servicemen
```bash
curl https://serviceman-backend.onrender.com/api/users/servicemen/
```

**Expected Response (200 OK):**
```json
{
  "statistics": {
    "total_servicemen": 0,  // Or actual count if servicemen exist
    "available": 0,
    "busy": 0
  },
  "results": []  // Or actual servicemen if they exist
}
```

#### Test 2: Get Specific Serviceman
```bash
curl https://serviceman-backend.onrender.com/api/users/servicemen/1/
```

**If serviceman exists - 200 OK:**
```json
{
  "user": 1,
  "skills": [],  // Empty until migrations
  "is_approved": true,  // Default
  ...
}
```

**If serviceman doesn't exist - 404 Not Found:**
```json
{
  "detail": "Not found."
}
```

#### Test 3: Category Servicemen
```bash
curl https://serviceman-backend.onrender.com/api/services/categories/1/servicemen/
```

**Expected (200 OK):**
```json
{
  "category_id": 1,
  "total_servicemen": 0,
  "available_servicemen": 0,
  "busy_servicemen": 0,
  "servicemen": []
}
```

---

## 🔍 If Still Getting 500 After Deploy

### Check Render Logs
```
1. Go to https://dashboard.render.com
2. Select serviceman-backend
3. Click "Logs"
4. Look for Python traceback
```

### Common Issues:

#### Issue 1: No Servicemen in Database
**Solution**: Create test servicemen
```bash
curl -X POST https://serviceman-backend.onrender.com/api/users/create-test-servicemen/ \
  -H "Content-Type: application/json" \
  -d '{"category_id": 1}'
```

#### Issue 2: Category Doesn't Exist
**Solution**: Create category first (as admin)
```bash
curl -X POST https://serviceman-backend.onrender.com/api/categories/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electrical",
    "description": "Electrical services"
  }'
```

#### Issue 3: Old Code Still Running
**Solution**: Trigger manual deploy
```
1. Go to Render dashboard
2. Select service
3. Click "Manual Deploy"
4. Select "Deploy latest commit"
```

#### Issue 4: Database Connection Error
**Solution**: Check Render logs for database URL issues

---

## 📋 Step-by-Step Deployment Checklist

### Pre-Deploy
- [ ] All changes saved in your editor
- [ ] Changes accepted (green checkmarks in Cursor)

### Deploy
- [ ] `git add .`
- [ ] `git commit -m "Fix: Migration-safe serializers"`
- [ ] `git push origin main`
- [ ] Wait 3-5 minutes

### Verify
- [ ] Check Render dashboard shows "Live"
- [ ] Check latest commit SHA matches
- [ ] No errors in Render logs

### Test
- [ ] `curl https://serviceman-backend.onrender.com/api/users/servicemen/`
- [ ] Should return 200 OK
- [ ] May return empty array if no servicemen exist

### Create Data (If Needed)
- [ ] Create category (admin endpoint)
- [ ] Create test servicemen
- [ ] Test again

---

## 🚀 Quick Deploy Commands

```bash
# Navigate to project
cd /home/chegbe/Desktop/Projects/ServiceManBackend-main

# Add all changes
git add .

# Commit
git commit -m "Fix: Make serializers migration-safe for production

- ServicemanProfile fields now use SerializerMethodField
- All new fields have safe default values
- Prevents 500 errors before migrations
- Endpoints work immediately after deploy
"

# Push to trigger Render deployment
git push origin main

# Watch deployment
echo "🔍 Check deployment at: https://dashboard.render.com"
echo "⏱️  Wait 3-5 minutes, then test:"
echo "curl https://serviceman-backend.onrender.com/api/users/servicemen/"
```

---

## ✅ Success Criteria

After deployment, you should see:

### Before (Current - Broken)
```bash
$ curl https://serviceman-backend.onrender.com/api/users/servicemen/
<!doctype html>
<html lang="en">
<head>
  <title>Server Error (500)</title>
...
```

### After (Fixed!)
```bash
$ curl https://serviceman-backend.onrender.com/api/users/servicemen/
{
  "statistics": {
    "total_servicemen": 3,
    "available": 3,
    "busy": 0
  },
  "results": [...]
}
```

---

## 📞 Need Help?

**Deployment Issues**: Check Render logs  
**500 Errors After Deploy**: Share the full error from Render logs  
**Empty Results**: Create test data (see above)

---

**Action Required**: Deploy to production NOW!  
**Command**: `git push origin main`  
**Wait Time**: 3-5 minutes  
**Result**: Endpoints will work!

