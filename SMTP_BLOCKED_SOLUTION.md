# 🚨 Network Unreachable - SMTP Blocked

## The Problem
Render is blocking outbound SMTP connections, causing `[Errno 101] Network is unreachable` when trying to connect to Gmail's SMTP server.

## 🔧 Solutions

### Option 1: Use SendGrid (Recommended)
SendGrid is a reliable email service that works well with Render.

#### Setup SendGrid:
1. **Sign up** at [SendGrid](https://sendgrid.com/)
2. **Create an API key** with "Mail Send" permissions
3. **Update your environment variables**:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=blogscribeai@gmail.com
```

### Option 2: Use Mailgun
Another reliable email service.

#### Setup Mailgun:
1. **Sign up** at [Mailgun](https://www.mailgun.com/)
2. **Get your SMTP credentials**
3. **Update your environment variables**:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-mailgun-username
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=blogscribeai@gmail.com
```

### Option 3: Use AWS SES
Amazon's email service.

#### Setup AWS SES:
1. **Sign up** for AWS SES
2. **Verify your email address**
3. **Get SMTP credentials**
4. **Update your environment variables**:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-ses-username
EMAIL_HOST_PASSWORD=your-ses-password
DEFAULT_FROM_EMAIL=blogscribeai@gmail.com
```

### Option 4: Use Resend (Modern Alternative)
A developer-friendly email service.

#### Setup Resend:
1. **Sign up** at [Resend](https://resend.com/)
2. **Get your API key**
3. **Install the package**:
   ```bash
   pip install resend
   ```
4. **Update your environment variables**:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=your-resend-api-key
DEFAULT_FROM_EMAIL=blogscribeai@gmail.com
```

## 🚀 Quick Fix with SendGrid

1. **Go to [SendGrid](https://sendgrid.com/)**
2. **Sign up for free account**
3. **Create API key**:
   - Go to Settings → API Keys
   - Click "Create API Key"
   - Choose "Restricted Access"
   - Give it "Mail Send" permissions
   - Copy the API key
4. **Update Render environment variables**:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=your-sendgrid-api-key-here
   DEFAULT_FROM_EMAIL=blogscribeai@gmail.com
   ```
5. **Redeploy your app**

## 🧪 Test After Setup

```bash
curl -X POST https://serviceman-backend.onrender.com/api/users/test-email/ \
  -H "Content-Type: application/json" \
  -d '{"email": "petersojochegbe@gmail.com"}'
```

## 💡 Why This Happens

Some hosting providers (including Render) block outbound SMTP connections to prevent spam. This is a security measure, but it prevents using Gmail's SMTP directly.

## 🎯 Recommendation

**Use SendGrid** - it's free for up to 100 emails/day, reliable, and works perfectly with Render.

Would you like me to help you set up SendGrid or another email service?

