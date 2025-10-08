# 📧 Email Configuration Fix

## The Problem
The email is being sent from `no-reply@yourdomain.com` instead of your configured email settings.

## ✅ What I Fixed
Added `DEFAULT_FROM_EMAIL` setting to production configuration.

## 🔧 Environment Variables for Render

Make sure these are set in your Render dashboard:

```
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

## 📋 Gmail Setup (if using Gmail)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password as `EMAIL_HOST_PASSWORD`

## 📋 Other Email Providers

### Outlook/Hotmail:
```
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### Yahoo:
```
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### Custom SMTP:
```
EMAIL_HOST=your-smtp-server.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

## 🚀 Deploy the Fix

```bash
git add .
git commit -m "Fix email configuration - add DEFAULT_FROM_EMAIL"
git push origin main
```

## 🧪 Test Email Configuration

After deployment, test registration again. The email should now come from your configured email address.

## 📞 Troubleshooting

### If emails still don't work:

1. **Check Render logs** for email errors
2. **Verify environment variables** are set correctly
3. **Test with console backend** first:
   ```
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```

### Common Issues:

- **Gmail**: Need app password, not regular password
- **Port**: Use 587 for TLS, 465 for SSL
- **TLS**: Must be True for most providers
- **Authentication**: Make sure credentials are correct

## 🎯 Expected Result

After the fix, emails should come from your configured email address instead of `no-reply@yourdomain.com`.
