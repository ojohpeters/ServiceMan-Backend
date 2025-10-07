# 🚀 Free Hosting Guide for Serviceman Platform API

## Option 1: Railway (Recommended) - Easiest Setup

### Step 1: Prepare Your Code
1. **Push to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

### Step 2: Deploy on Railway
1. **Go to [Railway.app](https://railway.app)**
2. **Sign up with GitHub**
3. **Click "New Project" → "Deploy from GitHub repo"**
4. **Select your repository**
5. **Railway will automatically detect Django and deploy**

### Step 3: Configure Environment Variables
In Railway dashboard, go to your project → Variables tab and add:

```bash
# Required Variables
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
DEBUG=False
ALLOWED_HOSTS=your-app-name.railway.app
DATABASE_URL=postgresql://postgres:password@host:port/database

# Optional but Recommended
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS (allow your frontend)
FRONTEND_URL=https://your-frontend-domain.com,http://localhost:3000

# Redis (for caching)
REDIS_URL=redis://localhost:6379/1
```

### Step 4: Get Your API URL
Railway will give you a URL like: `https://your-app-name.railway.app`

**Your API base URL will be:** `https://your-app-name.railway.app/api`

---

## Option 2: Render (Alternative)

### Step 1: Connect GitHub
1. **Go to [Render.com](https://render.com)**
2. **Sign up with GitHub**
3. **Click "New" → "Web Service"**
4. **Connect your repository**

### Step 2: Configure Service
- **Name**: `serviceman-api`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

### Step 3: Add Environment Variables
Same as Railway above.

---

## Option 3: Heroku (Classic)

### Step 1: Install Heroku CLI
```bash
# Install Heroku CLI from https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Deploy
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate
```

---

## 🔧 Quick Setup Commands

### For Railway/Render:
```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to production"
git push origin main

# 2. Connect to hosting platform
# 3. Set environment variables
# 4. Deploy automatically
```

### Test Your Deployment:
```bash
# Test the API
curl https://your-app-name.railway.app/api/services/categories/

# Should return your categories
```

---

## 📱 Frontend Integration

Once deployed, your friend can use:

```javascript
// Update the base URL
const API_BASE_URL = 'https://your-app-name.railway.app/api';

// Example API calls
const getCategories = async () => {
    const response = await fetch(`${API_BASE_URL}/services/categories/`);
    return response.json();
};

const getServicemenByCategory = async (categoryId) => {
    const response = await fetch(`${API_BASE_URL}/services/categories/${categoryId}/servicemen/`);
    return response.json();
};

const registerUser = async (userData) => {
    const response = await fetch(`${API_BASE_URL}/users/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
    });
    return response.json();
};
```

---

## 🛠️ Troubleshooting

### Common Issues:

1. **CORS Errors**: Add your frontend domain to `FRONTEND_URL`
2. **Database Errors**: Ensure `DATABASE_URL` is set correctly
3. **Static Files**: Railway/Render handle this automatically
4. **Email Issues**: Use console backend for testing: `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`

### Debug Commands:
```bash
# Check logs (Railway)
railway logs

# Check logs (Render)
# Go to dashboard → Logs tab

# Check logs (Heroku)
heroku logs --tail
```

---

## 🎯 Recommended Setup

**For your friend's access, I recommend Railway because:**
- ✅ **Free tier** with generous limits
- ✅ **Automatic deployments** from GitHub
- ✅ **Built-in PostgreSQL** database
- ✅ **Easy environment variable** management
- ✅ **Custom domains** available
- ✅ **No credit card** required for free tier

**Your friend will get:**
- 🌐 **Public API URL**: `https://your-app-name.railway.app/api`
- 📚 **API Documentation**: `https://your-app-name.railway.app/api/docs/`
- 🔧 **Admin Panel**: `https://your-app-name.railway.app/admin/`

---

## 🚀 Next Steps

1. **Choose Railway** (easiest option)
2. **Push code to GitHub**
3. **Connect to Railway**
4. **Set environment variables**
5. **Share the API URL** with your friend
6. **Test the endpoints**

Your friend will have full access to the API for frontend development! 🎉
