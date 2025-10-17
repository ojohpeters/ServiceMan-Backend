# Admin Creation - Quick Reference Guide

## 🚀 Quick Start

### Create Admin User (Admin Only)
```bash
curl -X POST http://localhost:8000/api/users/admin/create/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_admin",
    "email": "admin@servicemanplatform.com",
    "password": "SecureAdminPass123!",
    "password_confirm": "SecureAdminPass123!",
    "first_name": "John",
    "last_name": "Admin"
  }'
```

### Response
```json
{
  "id": 15,
  "username": "new_admin",
  "email": "admin@servicemanplatform.com",
  "user_type": "ADMIN",
  "is_email_verified": true
}
```

## ❌ Public Registration Blocks ADMIN

Attempting to create admin via public registration will fail:

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "hacker",
    "email": "hacker@example.com",
    "password": "password123",
    "user_type": "ADMIN"
  }'
```

**Error Response:**
```json
{
  "user_type": [
    "Cannot create admin users through public registration. Please contact an administrator."
  ]
}
```

## 🔐 Requirements

1. **Authentication**: Must be logged in as admin
2. **Password Match**: password and password_confirm must match
3. **Unique Username**: Username must not exist
4. **Unique Email**: Email must not exist
5. **Password Strength**: Minimum 8 characters

## ✅ Auto-Configuration

When admin is created, these are automatically set:
- `user_type` = `ADMIN`
- `is_staff` = `True`
- `is_email_verified` = `True`
- `is_active` = `True`

## 📚 Full Documentation

See `ADMIN_CREATION_DOCUMENTATION.md` for complete documentation.

