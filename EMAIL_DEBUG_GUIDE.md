# 🔍 Email Debugging Guide

## 🚨 The Problem
Emails are being "sent" (showing in logs) but not actually delivered to the recipient's inbox, not even in spam folder.

## ✅ What I Added for Debugging

### 1. **Enhanced Logging**
- Added detailed logging to `send_verification_email()` method
- Shows all email configuration settings
- Logs success/failure of email sending

### 2. **Test Email Endpoint**
- New endpoint: `POST /api/users/test-email/`
- Tests email configuration without user registration
- Returns detailed email settings and error messages

### 3. **Improved Email Settings**
- Added `EMAIL_TIMEOUT = 30`
- Added `EMAIL_USE_SSL = False` (use TLS instead)
- Added `EMAIL_SUBJECT_PREFIX = '[ServiceMan] '`

## 🧪 How to Debug

### Step 1: Test Email Configuration
```bash
curl -X POST https://your-app.onrender.com/api/users/test-email/ \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@gmail.com"}'
```

### Step 2: Check Render Logs
1. Go to your Render dashboard
2. Click on your service
3. Go to "Logs" tab
4. Look for the detailed email configuration logs

### Step 3: Try Resend Verification
```bash
curl -X POST https://your-app.onrender.com/api/users/resend-verification-email/ \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@gmail.com"}'
```

## 🔧 Common Email Issues & Solutions

### Issue 1: Gmail App Passwords
**Problem**: Gmail requires app-specific passwords for SMTP
**Solution**: 
1. Enable 2FA on your Gmail account
2. Generate an "App Password" for "Mail"
3. Use the app password (not your regular password) in `EMAIL_HOST_PASSWORD`

### Issue 2: SMTP Authentication
**Problem**: SMTP server rejecting authentication
**Solution**: Check these settings:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # NOT your regular password
```

### Issue 3: Email Provider Restrictions
**Problem**: Some email providers block automated emails
**Solution**: Try different email providers:
- **Gmail**: Usually works well
- **Outlook/Hotmail**: May have restrictions
- **Yahoo**: Often blocks automated emails

### Issue 4: Render Environment Variables
**Problem**: Environment variables not set correctly
**Solution**: Double-check in Render dashboard:
1. Go to your service
2. Go to "Environment" tab
3. Verify all email variables are set

## 🎯 Expected Log Output

When working correctly, you should see:
```
=== EMAIL CONFIGURATION DEBUG ===
EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST: smtp.gmail.com
EMAIL_PORT: 587
EMAIL_HOST_USER: your-email@gmail.com
EMAIL_USE_TLS: True
DEFAULT_FROM_EMAIL: your-email@gmail.com
Test email sent successfully. Result: 1
```

## 🚀 Deploy and Test

```bash
git add .
git commit -m "Add email debugging and test endpoint"
git push origin main
```

## 📞 Next Steps

1. **Deploy the changes**
2. **Test the email endpoint** with your email
3. **Check Render logs** for detailed configuration
4. **Try resending verification** to your email
5. **Report back** what you see in the logs

The enhanced logging will help us identify exactly where the email delivery is failing! 🔍
