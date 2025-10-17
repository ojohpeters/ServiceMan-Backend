# Email Templates Visual Preview

## 📧 Overview

The ServiceMan Platform features professional, mobile-responsive HTML email templates with a consistent brand identity.

## 🎨 Design Features

### Universal Features (All Templates)
- **Responsive Design**: Adapts to mobile, tablet, and desktop
- **ServiceMan Branding**: Purple gradient header with platform logo
- **Professional Typography**: Clean, readable fonts
- **Call-to-Action Buttons**: Large, prominent action buttons
- **Security Warnings**: Highlighted security information
- **Footer**: Consistent footer with social links and contact info

### Color Scheme
- **Primary**: Purple gradient (#667eea to #764ba2)
- **Success**: Green (#28a745)
- **Warning**: Yellow (#ffc107)
- **Info**: Blue (#2196F3)
- **Background**: Light gray (#f4f7fa)
- **Text**: Dark gray (#333)

## 📨 Template Previews

### 1. Email Verification Template
**File**: `templates/emails/email_verification.html`

**Purpose**: Sent when user registers to verify their email address

**Key Elements**:
- Welcome message with user's username
- Large "Verify My Email Address" button
- Copy-pasteable verification link
- "Why verify your email?" info box (blue)
- "What's Next?" feature list
- Security warning if user didn't create account

**Sample Content**:
```
Subject: Verify Your Email - ServiceMan Platform

Hello testuser,

Thank you for registering with ServiceMan Platform! 

[Verify My Email Address Button]

ℹ️ Why verify your email?
Email verification helps us ensure the security of your account...

What's Next?
• Browse our wide range of service categories
• Book professional servicemen for your needs
• Track your service requests in real-time
```

---

### 2. Password Reset Request Template
**File**: `templates/emails/password_reset.html`

**Purpose**: Sent when user requests to reset their password

**Key Elements**:
- Clear reset request message
- 24-hour expiration notice
- Large "Reset My Password" button
- Copy-pasteable reset link
- Yellow security warning box
- Security tips list

**Sample Content**:
```
Subject: Password Reset Request - ServiceMan Platform

Hello john_doe,

We received a request to reset the password for your ServiceMan Platform account.

Click the button below to reset your password. This link will expire in 24 hours.

[Reset My Password Button]

⚠️ Security Notice:
If you didn't request a password reset, please ignore this email...

Security Tips:
• Never share your password with anyone
• Use a strong, unique password for your account
• Enable two-factor authentication when available
```

---

### 3. Password Reset Success Template
**File**: `templates/emails/password_reset_success.html`

**Purpose**: Confirmation email sent after successful password reset

**Key Elements**:
- Success confirmation message
- Green success notification box
- "Log In to Your Account" button
- Red security alert if change wasn't authorized
- Account security recommendations list

**Sample Content**:
```
Subject: Password Reset Successful - ServiceMan Platform

Hello john_doe,

This email confirms that your ServiceMan Platform account password has been successfully reset.

✓ Your password has been changed
You can now log in to your account using your new password.

[Log In to Your Account Button]

⚠️ Didn't make this change?
If you didn't reset your password, your account may be compromised...

Account Security Recommendations:
• Review your recent account activity
• Ensure you recognize all login locations and devices
```

---

### 4. Base Template
**File**: `templates/emails/base.html`

**Purpose**: Parent template extended by all other email templates

**Structure**:
```
┌─────────────────────────────────────┐
│   Header (Purple Gradient)          │
│   🔧 ServiceMan Platform            │
├─────────────────────────────────────┤
│                                      │
│   Body Content (White Background)   │
│   {% block content %}                │
│                                      │
├─────────────────────────────────────┤
│   Footer (Light Gray)                │
│   ServiceMan Platform                │
│   Social Links                       │
│   © 2025 ServiceMan Platform        │
└─────────────────────────────────────┘
```

## 📱 Responsive Behavior

### Desktop (> 600px)
- Email container: 600px width, centered
- Buttons: Inline with padding
- Two-column layouts where applicable

### Mobile (< 600px)
- Email container: Full width
- Buttons: Full width, stacked
- Single-column layout
- Larger touch targets
- Readable font sizes

## 🎨 CSS Styling

### Button Styles
```css
.btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 14px 32px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
}

.btn:hover {
    transform: translateY(-2px);
}
```

### Alert Boxes

**Security Warning (Yellow)**
```css
.security-warning {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 15px;
}
```

**Success (Green)**
```css
.success-box {
    background-color: #d4edda;
    border-left: 4px solid #28a745;
    color: #155724;
}
```

**Info (Blue)**
```css
.info-box {
    background-color: #e7f3ff;
    border-left: 4px solid #2196F3;
    color: #0c5460;
}
```

## ✉️ Plain Text Fallback

All templates include automatic plain text fallback for email clients that don't support HTML:

```
ServiceMan Platform

Hello testuser,

Thank you for registering with ServiceMan Platform!

Please verify your email: https://servicemanplatform.com/verify-email/?uid=5&token=abc123...

---

ServiceMan Platform
Your trusted service marketplace
© 2025 ServiceMan Platform. All rights reserved.
```

## 🔧 Customization Guide

### Changing Colors
Edit `templates/emails/base.html`:

```html
<style>
    .email-header {
        background: linear-gradient(135deg, #YOUR_COLOR_1, #YOUR_COLOR_2);
    }
    
    .btn {
        background: linear-gradient(135deg, #YOUR_COLOR_1, #YOUR_COLOR_2);
    }
</style>
```

### Adding Logo
Replace the emoji logo with an image:

```html
<div class="email-header">
    <img src="https://yourdomain.com/logo.png" alt="ServiceMan Platform" style="height: 40px;">
    <h1>ServiceMan Platform</h1>
</div>
```

### Customizing Footer
Edit social links and contact info in `base.html`:

```html
<div class="social-links">
    <a href="https://facebook.com/yourpage">Facebook</a> | 
    <a href="https://twitter.com/yourhandle">Twitter</a> | 
    <a href="https://linkedin.com/company/yourcompany">LinkedIn</a>
</div>
```

## 🧪 Testing Templates

### View in Browser
```python
# Create a test view (development only)
from django.template.loader import render_to_string
from django.http import HttpResponse

def preview_email(request, template_name):
    context = {
        'user': request.user,
        'verification_url': 'http://localhost:8000/verify?uid=1&token=abc123',
        'reset_url': 'http://localhost:8000/reset?uid=1&token=abc123',
        'login_url': 'http://localhost:8000/login',
    }
    html = render_to_string(f'emails/{template_name}.html', context)
    return HttpResponse(html)
```

### Send Test Email
```http
POST /api/users/test-email/
Content-Type: application/json

{
  "email": "your-email@example.com"
}
```

### Email Testing Services
- **Mailtrap**: https://mailtrap.io/
- **MailHog**: Local email testing
- **Ethereal**: https://ethereal.email/

## 📊 Email Client Compatibility

### Tested and Working
- ✅ Gmail (Web, iOS, Android)
- ✅ Outlook (Web, Desktop, Mobile)
- ✅ Apple Mail (macOS, iOS)
- ✅ Yahoo Mail
- ✅ ProtonMail
- ✅ Thunderbird

### Known Issues
- Some email clients strip CSS animations
- Outlook has limited gradient support (fallback color provided)
- Dark mode varies by client

## 🚀 Future Enhancements

### Planned Features
- [ ] Booking confirmation emails
- [ ] Service completion notifications
- [ ] Rating request emails
- [ ] Payment receipt emails
- [ ] Monthly summary emails
- [ ] Promotional email templates

### Possible Improvements
- [ ] Add email preferences/unsubscribe options
- [ ] Implement email templates in multiple languages
- [ ] Add dynamic content based on user preferences
- [ ] Include user profile pictures in emails
- [ ] Add service-specific branding for different categories

## 📞 Support

For template customization or issues:
- **Email**: support@servicemanplatform.com
- **Documentation**: See PASSWORD_RESET_DOCUMENTATION.md

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Maintained by**: ServiceMan Platform Team


