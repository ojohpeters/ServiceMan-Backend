# Skills API - Quick Reference Guide

## 🚀 Quick Start

### List All Skills
```bash
curl http://localhost:8000/api/users/skills/
```

### Filter by Category
```bash
curl http://localhost:8000/api/users/skills/?category=TECHNICAL
```

### Create Skill (Admin Only)
```bash
curl -X POST http://localhost:8000/api/users/skills/create/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electrical Wiring",
    "category": "TECHNICAL",
    "description": "Installation and repair of electrical systems"
  }'
```

### Register Serviceman with Skills
```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_electrician",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "user_type": "SERVICEMAN",
    "skill_ids": [1, 2, 3]
  }'
```

### Add Skills to Serviceman
```bash
curl -X POST http://localhost:8000/api/users/servicemen/5/skills/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill_ids": [4, 5, 6]}'
```

### Remove Skills from Serviceman
```bash
curl -X DELETE http://localhost:8000/api/users/servicemen/5/skills/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill_ids": [2]}'
```

### Update Serviceman Profile with Skills
```bash
curl -X PATCH http://localhost:8000/api/users/serviceman-profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": "Experienced electrician",
    "years_of_experience": 10,
    "skill_ids": [1, 3, 5, 7]
  }'
```

## 📋 Skill Categories

- `TECHNICAL` - Technical skills (Electrical, Plumbing, etc.)
- `MANUAL` - Manual labor (Carpentry, Masonry, etc.)
- `CREATIVE` - Creative skills (Design, Landscaping, etc.)
- `PROFESSIONAL` - Professional services (Consulting, etc.)
- `OTHER` - Other skills

## 🔑 Authentication

Most endpoints require JWT authentication:

```bash
# Get token
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📚 Full Documentation

See `SKILLS_MANAGEMENT_DOCUMENTATION.md` for complete documentation.

