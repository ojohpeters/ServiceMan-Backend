# ⚡ Serviceman Approval System - Quick Start

## ✅ 3 NEW Admin Endpoints for Application Approval!

---

## 1️⃣ List Pending Applications

```bash
GET /api/users/admin/pending-servicemen/
```

**Response:**
```json
{
  "total_pending": 5,
  "pending_applications": [...]
}
```

---

## 2️⃣ Approve Serviceman

```bash
POST /api/users/admin/approve-serviceman/

{
  "serviceman_id": 15,
  "category_id": 2
}
```

**What Happens:**
- ✅ Serviceman marked as approved
- ✅ Category assigned (optional)
- ✅ Serviceman notified via dashboard + email
- ✅ Can now be assigned to jobs
- ✅ Appears in public listings

---

## 3️⃣ Reject Serviceman

```bash
POST /api/users/admin/reject-serviceman/

{
  "serviceman_id": 15,
  "rejection_reason": "Insufficient documentation"
}
```

**What Happens:**
- ❌ Application rejected
- ❌ Reason recorded
- 📧 Serviceman notified with reason
- ❌ Cannot be assigned to jobs
- ❌ Not in public listings

---

## 🔄 Complete Workflow

### When Serviceman Registers:
1. Account created with `is_approved = false`
2. Can login but sees "Pending Approval" message
3. NOT shown in public servicemen listings
4. Admin sees them in pending list

### Admin Reviews:
```javascript
// 1. Get pending applications
const pending = await fetch('/api/users/admin/pending-servicemen/', {
  headers: { 'Authorization': `Bearer ${adminToken}` }
}).then(r => r.json());

// 2. Review application
console.log(pending.pending_applications);

// 3. Approve or Reject
await fetch('/api/users/admin/approve-serviceman/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    serviceman_id: 15,
    category_id: 2
  })
});
```

### After Approval:
- ✅ Serviceman receives notification
- ✅ Appears in `/api/users/servicemen/`
- ✅ Can be assigned to jobs
- ✅ Fully functional account

---

## 🎯 Quick Test

```bash
# 1. Register serviceman
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_serviceman",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "user_type": "SERVICEMAN"
  }'

# 2. Check pending (should show 1)
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/users/admin/pending-servicemen/

# 3. Approve
curl -X POST http://localhost:8000/api/users/admin/approve-serviceman/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceman_id": 15, "category_id": 1}'

# 4. Verify in public list
curl http://localhost:8000/api/users/servicemen/
```

---

## 🎨 UI Component Example

```javascript
function ApprovalButton({ servicemanId, onApproved }) {
  const [category, setCategory] = useState('');
  
  const handleApprove = async () => {
    await fetch('/api/users/admin/approve-serviceman/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${adminToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        serviceman_id: servicemanId,
        category_id: category || null
      })
    });
    
    onApproved();
  };
  
  return (
    <div>
      <select value={category} onChange={(e) => setCategory(e.target.value)}>
        <option value="">Select Category</option>
        <option value="1">Plumbing</option>
        <option value="2">Electrical</option>
      </select>
      <button onClick={handleApprove}>✅ Approve</button>
    </div>
  );
}
```

---

## 📊 All Admin Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /admin/pending-servicemen/` | List pending applications |
| `POST /admin/approve-serviceman/` | Approve application |
| `POST /admin/reject-serviceman/` | Reject application |
| `POST /admin/assign-category/` | Assign category |
| `POST /admin/bulk-assign-category/` | Bulk assign |
| `GET /admin/servicemen-by-category/` | View by category |

---

## ⚠️ Migration Required

```bash
python manage.py makemigrations
python manage.py migrate
```

**Approve existing servicemen:**
```python
from apps.users.models import ServicemanProfile
from django.utils import timezone

ServicemanProfile.objects.update(
    is_approved=True,
    approved_at=timezone.now()
)
```

---

## 📚 Full Documentation

See **SERVICEMAN_APPROVAL_SYSTEM.md** for:
- Complete React components
- Admin dashboard examples
- Analytics queries
- Django admin interface details

---

**Status**: ✅ Ready to deploy  
**Requires**: Database migration  
**Auth**: Admin token required

