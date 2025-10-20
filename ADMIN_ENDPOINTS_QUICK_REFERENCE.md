# ⚡ Admin Endpoints - Quick Reference

## 🎯 Category Assignment (NEW!)

### 1. Assign Serviceman to Category
```bash
POST /api/users/admin/assign-category/

{
  "serviceman_id": 5,
  "category_id": 2
}
```

### 2. Bulk Assign Category
```bash
POST /api/users/admin/bulk-assign-category/

{
  "serviceman_ids": [5, 6, 7, 8],
  "category_id": 2
}
```

### 3. View Servicemen by Category
```bash
GET /api/users/admin/servicemen-by-category/
```

---

## 👑 Admin Management

### Create Admin User
```bash
POST /api/users/admin/create/

{
  "username": "new_admin",
  "email": "admin@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

---

## 📊 User & Profile Management

### List All Servicemen
```bash
GET /api/users/servicemen/
GET /api/users/servicemen/?is_available=true
GET /api/users/servicemen/?category=1
```

### Get User by ID
```bash
GET /api/users/{user_id}/
```

### Get Client Profile
```bash
GET /api/users/clients/{client_id}/
```

---

## 🔔 Notifications

### Send Notification
```bash
POST /api/notifications/send/

{
  "user_id": 5,
  "title": "Service Assigned",
  "message": "You have been assigned to SR #123",
  "service_request_id": 123
}
```

---

## 📂 Categories

### Create Category
```bash
POST /api/categories/

{
  "name": "Electrical",
  "description": "Electrical services"
}
```

### Update Category
```bash
PATCH /api/categories/{id}/

{
  "description": "Updated description"
}
```

---

## 💼 Skills Management

### Create Skill
```bash
POST /api/users/skills/create/

{
  "name": "Smart Home Installation",
  "category": "TECHNICAL",
  "description": "Installation of smart home devices"
}
```

### Update Skill
```bash
PUT /api/users/skills/{id}/update/

{
  "description": "Updated description"
}
```

### Delete Skill (Soft)
```bash
DELETE /api/users/skills/{id}/delete/
```

---

## 🎯 Complete Admin Workflow

### Assign Service Request
```javascript
// 1. Get available servicemen
GET /api/users/servicemen/?category=1&is_available=true

// 2. Assign to request
PATCH /api/service-requests/{id}/
{
  "serviceman_id": 5,
  "status": "ASSIGNED_TO_SERVICEMAN"
}

// 3. Notify serviceman
POST /api/notifications/send/
{
  "user_id": 5,
  "title": "Service Assigned",
  "message": "You have been assigned..."
}
```

---

**Auth Required**: Admin JWT token  
**Format**: `Authorization: Bearer YOUR_ADMIN_TOKEN`

📚 **Full Guide**: ADMIN_CATEGORY_ASSIGNMENT.md

