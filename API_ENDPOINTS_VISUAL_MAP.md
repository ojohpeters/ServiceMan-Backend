# 🗺️ ServiceMan Platform - API Endpoints Visual Map

## Complete visual reference of all API endpoints

---

## 🔐 AUTHENTICATION & USER MANAGEMENT

```
┌─────────────────────────────────────────────────────────┐
│                    AUTHENTICATION                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /api/users/register/                            │
│         └─ Register new user (Client/Serviceman)        │
│                                                          │
│  POST   /api/users/token/                               │
│         └─ Login & get JWT token                        │
│                                                          │
│  POST   /api/users/token/refresh/                       │
│         └─ Refresh JWT token                            │
│                                                          │
│  GET    /api/users/me/                                  │
│         └─ Get current user info                        │
│                                                          │
│  GET    /api/users/{id}/ ⭐ NEW                         │
│         └─ Get any user by ID                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📧 EMAIL & VERIFICATION

```
┌─────────────────────────────────────────────────────────┐
│               EMAIL VERIFICATION                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/users/verify-email/                        │
│         └─ Verify email with token                      │
│                                                          │
│  POST   /api/users/resend-verification-email/           │
│         └─ Resend verification email                    │
│                                                          │
├─────────────────────────────────────────────────────────┤
│               PASSWORD RESET                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /api/users/password-reset/                      │
│         └─ Request password reset link                  │
│                                                          │
│  POST   /api/users/password-reset-confirm/              │
│         └─ Confirm password reset                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 👷 SERVICEMEN ENDPOINTS

```
┌─────────────────────────────────────────────────────────┐
│                  SERVICEMEN                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/users/servicemen/ ⭐ NEW                   │
│         └─ List ALL servicemen                          │
│         └─ Filters: category, is_available, min_rating  │
│         └─ Search: by name                              │
│         └─ Sorting: rating, jobs, experience            │
│         └─ Shows: availability + active jobs            │
│                                                          │
│  GET    /api/users/servicemen/{id}/                     │
│         └─ Get serviceman profile                       │
│         └─ Shows: availability status + warnings        │
│                                                          │
│  GET    /api/users/serviceman-profile/                  │
│         └─ Get own profile (authenticated)              │
│                                                          │
│  PATCH  /api/users/serviceman-profile/                  │
│         └─ Update own profile                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 👥 CLIENT ENDPOINTS

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENTS                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/users/clients/{id}/ ⭐ NEW                 │
│         └─ Get client profile by ID                     │
│         └─ Admin only (or self)                         │
│         └─ Returns: phone, address, user info           │
│                                                          │
│  GET    /api/users/client-profile/                      │
│         └─ Get own profile (authenticated)              │
│                                                          │
│  PATCH  /api/users/client-profile/                      │
│         └─ Update own profile                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 💼 SKILLS MANAGEMENT

```
┌─────────────────────────────────────────────────────────┐
│                    SKILLS                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/users/skills/                              │
│         └─ List all active skills                       │
│         └─ Filter by category                           │
│                                                          │
│  GET    /api/users/skills/{id}/                         │
│         └─ Get skill details                            │
│                                                          │
│  POST   /api/users/skills/create/ [ADMIN]               │
│         └─ Create new skill                             │
│                                                          │
│  PUT    /api/users/skills/{id}/update/ [ADMIN]          │
│         └─ Update skill                                 │
│                                                          │
│  DELETE /api/users/skills/{id}/delete/ [ADMIN]          │
│         └─ Soft delete skill                            │
│                                                          │
│  GET    /api/users/servicemen/{id}/skills/              │
│         └─ Get serviceman's skills                      │
│                                                          │
│  POST   /api/users/servicemen/{id}/skills/              │
│         └─ Add skills to serviceman                     │
│                                                          │
│  DELETE /api/users/servicemen/{id}/skills/              │
│         └─ Remove skills from serviceman                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 👑 ADMIN ENDPOINTS

```
┌─────────────────────────────────────────────────────────┐
│                    ADMIN                                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /api/users/admin/create/ [ADMIN]                │
│         └─ Create new admin user                        │
│         └─ Requires: password confirmation              │
│         └─ Auto-sets: is_staff, is_email_verified       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔔 NOTIFICATIONS

```
┌─────────────────────────────────────────────────────────┐
│                 NOTIFICATIONS                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/notifications/                             │
│         └─ List user's notifications                    │
│                                                          │
│  POST   /api/notifications/send/ [ADMIN] ⭐ NEW         │
│         └─ Send notification to user                    │
│         └─ Body: user_id, title, message                │
│         └─ Creates dashboard + email notification       │
│                                                          │
│  GET    /api/notifications/unread-count/                │
│         └─ Get unread count                             │
│                                                          │
│  PATCH  /api/notifications/{id}/read/                   │
│         └─ Mark notification as read                    │
│                                                          │
│  PATCH  /api/notifications/mark-all-read/               │
│         └─ Mark all notifications as read               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📂 CATEGORIES

```
┌─────────────────────────────────────────────────────────┐
│                  CATEGORIES                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/categories/                                │
│         └─ List all categories                          │
│                                                          │
│  POST   /api/categories/ [ADMIN]                        │
│         └─ Create new category                          │
│                                                          │
│  GET    /api/categories/{id}/                           │
│         └─ Get category details                         │
│                                                          │
│  PATCH  /api/categories/{id}/ [ADMIN]                   │
│         └─ Update category                              │
│                                                          │
│  GET    /api/categories/{id}/servicemen/                │
│         └─ List servicemen in category                  │
│         └─ Shows: availability + warnings               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 SERVICE REQUESTS

```
┌─────────────────────────────────────────────────────────┐
│              SERVICE REQUESTS                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/service-requests/                          │
│         └─ List service requests (role-based)           │
│                                                          │
│  POST   /api/service-requests/ [CLIENT]                 │
│         └─ Create new service request                   │
│                                                          │
│  GET    /api/service-requests/{id}/                     │
│         └─ Get request details                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 INTERACTIVE DOCUMENTATION

```
┌─────────────────────────────────────────────────────────┐
│              API DOCUMENTATION                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/docs/                                      │
│         └─ Swagger UI (Interactive)                     │
│         └─ Try endpoints live                           │
│                                                          │
│  GET    /api/redoc/                                     │
│         └─ ReDoc (Clean documentation)                  │
│                                                          │
│  GET    /api/schema/                                    │
│         └─ OpenAPI schema (JSON)                        │
│         └─ Import to Postman                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Client Requested Features Status

| Feature | Status | Endpoint |
|---------|--------|----------|
| List all servicemen | ✅ DONE | `GET /api/users/servicemen/` |
| Get user by ID | ✅ DONE | `GET /api/users/{id}/` |
| Get client profile | ✅ DONE | `GET /api/users/clients/{id}/` |
| Send notifications | ✅ DONE | `POST /api/notifications/send/` |

## 🌟 Bonus Features

| Feature | Status | Description |
|---------|--------|-------------|
| Auto-availability | ✅ DONE | Serviceman auto-set to busy/available |
| Client warnings | ✅ DONE | Warn when booking busy serviceman |
| Skills system | ✅ DONE | 6 endpoints for skills management |
| Email templates | ✅ DONE | 4 beautiful HTML email templates |
| Admin creation | ✅ DONE | Secure admin user creation |
| API docs | ✅ DONE | Interactive Swagger UI |

---

## 📚 Documentation Quick Links

**For Developers:**
- START → `CLIENT_ENDPOINTS_QUICK_START.md`
- Examples → `FRONTEND_API_CONSUMPTION_GUIDE.md`
- Complete → `CLIENT_API_ENDPOINTS_GUIDE.md`

**For Features:**
- Availability → `SERVICEMAN_AVAILABILITY_SYSTEM.md`
- Skills → `SKILLS_MANAGEMENT_DOCUMENTATION.md`
- Emails → `PASSWORD_RESET_DOCUMENTATION.md`
- Admin → `ADMIN_CREATION_DOCUMENTATION.md`

---

## 🚀 Production URLs

### Development
```
http://localhost:8000/api/
```

### Production (Render)
```
https://serviceman-backend.onrender.com/api/
```

### API Docs
```
https://serviceman-backend.onrender.com/api/docs/
```

---

**Status**: ✅ ALL FEATURES IMPLEMENTED  
**Ready for**: Frontend integration  
**Documentation**: 16 comprehensive guides  
**Total Endpoints**: 35+

🎊 **Happy coding!**

