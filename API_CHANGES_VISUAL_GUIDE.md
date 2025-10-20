# 🗺️ API Changes - Visual Guide for Frontend Devs

## Quick visual reference of what changed and what's new

---

## 🔴 BREAKING CHANGES: NONE ✅

All existing endpoints still work exactly the same way!

---

## 🆕 NEW ENDPOINTS (20+)

### Serviceman Approval System
```
┌─────────────────────────────────────────────────────────┐
│         SERVICEMAN APPROVAL (ADMIN ONLY)                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/users/admin/pending-servicemen/ ⭐         │
│         └─ List applications awaiting approval          │
│         └─ Response: { total_pending, applications }    │
│                                                          │
│  POST   /api/users/admin/approve-serviceman/ ⭐         │
│         └─ Body: { serviceman_id, category_id }         │
│         └─ Auto-notifies serviceman                     │
│                                                          │
│  POST   /api/users/admin/reject-serviceman/ ⭐          │
│         └─ Body: { serviceman_id, rejection_reason }    │
│         └─ Sends rejection notification                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Category Assignment System
```
┌─────────────────────────────────────────────────────────┐
│        CATEGORY ASSIGNMENT (ADMIN ONLY)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /api/users/admin/assign-category/ ⭐            │
│         └─ Assign one serviceman to category            │
│         └─ Body: { serviceman_id, category_id }         │
│                                                          │
│  POST   /api/users/admin/bulk-assign-category/ ⭐       │
│         └─ Assign multiple servicemen                   │
│         └─ Body: { serviceman_ids[], category_id }      │
│                                                          │
│  GET    /api/users/admin/servicemen-by-category/ ⭐     │
│         └─ View servicemen grouped by category          │
│         └─ Includes unassigned servicemen               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### User & Profile Endpoints
```
┌─────────────────────────────────────────────────────────┐
│            USER & PROFILE ENDPOINTS                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/users/servicemen/ ⭐                       │
│         └─ List ALL servicemen (with filters)           │
│         └─ Filters: category, availability, rating      │
│         └─ Shows: availability + active jobs            │
│         └─ Statistics: available/busy counts            │
│                                                          │
│  GET    /api/users/{id}/ ⭐                             │
│         └─ Get any user's basic info                    │
│         └─ Admin can view all, others limited           │
│                                                          │
│  GET    /api/users/clients/{id}/ ⭐                     │
│         └─ Get client profile (admin or self)           │
│         └─ Returns: phone, address, user info           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Skills Management System
```
┌─────────────────────────────────────────────────────────┐
│              SKILLS SYSTEM (NEW!)                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  GET    /api/users/skills/ ⭐                           │
│  GET    /api/users/skills/{id}/ ⭐                      │
│  POST   /api/users/skills/create/ ⭐ [Admin]            │
│  PUT    /api/users/skills/{id}/update/ ⭐ [Admin]       │
│  DELETE /api/users/skills/{id}/delete/ ⭐ [Admin]       │
│  GET/POST/DELETE /api/users/servicemen/{id}/skills/ ⭐  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Notifications Enhancement
```
┌─────────────────────────────────────────────────────────┐
│           NOTIFICATIONS (ENHANCED)                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  POST   /api/notifications/send/ ⭐ [Admin]             │
│         └─ Send custom notification to any user         │
│         └─ Body: { user_id, title, message }            │
│         └─ Creates dashboard + email notification       │
│                                                          │
│  [Existing notification endpoints still work]           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 ENHANCED RESPONSES

### Serviceman Profile - Now Includes:

```diff
{
  "user": 5,
  "category": {...},
+ "skills": [...],              // NEW - Array of skills
  "rating": "4.80",
  "is_available": false,
+ "active_jobs_count": 2,       // NEW - How many jobs currently
+ "availability_status": {      // NEW - Detailed status
+   "status": "busy",
+   "label": "Currently Busy",
+   "message": "...",
+   "warning": "...",
+   "can_book": true
+ },
+ "is_approved": true,           // NEW - Approval status
+ "approved_by": 1,              // NEW - Which admin
+ "approved_at": "...",          // NEW - When approved
+ "rejection_reason": ""         // NEW - If rejected
}
```

### Category Servicemen List - Now Includes:

```diff
{
  "category_id": 1,
+ "total_servicemen": 10,        // NEW
+ "available_servicemen": 7,     // NEW
+ "busy_servicemen": 3,          // NEW
+ "availability_message": {      // NEW
+   "type": "success",
+   "message": "7 servicemen available"
+ },
  "servicemen": [
    {
      "id": 1,
+     "is_available": true,      // Already existed
+     "active_jobs_count": 0,    // NEW
+     "availability_status": {   // NEW
+       "status": "available",
+       "label": "Available",
+       "badge_color": "green"
+     },
+     "booking_warning": null     // NEW - Shows if busy
    }
  ]
}
```

---

## 🎯 UI Components You MUST Build

### 1. Admin Approval Dashboard (NEW PAGE)
**Route**: `/admin/pending-approvals`

**Shows:**
- List of pending serviceman applications
- Approve/Reject buttons
- Category assignment dropdown

**API Calls:**
```javascript
GET /api/users/admin/pending-servicemen/
POST /api/users/admin/approve-serviceman/
POST /api/users/admin/reject-serviceman/
```

### 2. Pending Approval Screen (SERVICEMAN)
**Route**: `/serviceman/dashboard` (conditional)

**Shows When:**
- `serviceman.is_approved === false`

**Content:**
```
⏳ Application Under Review
Your application is being reviewed...
```

### 3. Availability Badges (UPDATE EXISTING)
**Where**: All serviceman cards/lists

**Add:**
```javascript
<span className={serviceman.is_available ? 'badge-green' : 'badge-orange'}>
  {serviceman.is_available ? 'Available' : 'Busy'}
</span>

{serviceman.active_jobs_count > 0 && (
  <p>🔧 {serviceman.active_jobs_count} active jobs</p>
)}
```

### 4. Booking Warnings (UPDATE EXISTING)
**Where**: Booking confirmation page

**Add:**
```javascript
{!serviceman.is_available && (
  <div className="alert alert-warning">
    ⚠️ {serviceman.availability_status.message}
    <p>{serviceman.availability_status.warning}</p>
  </div>
)}
```

---

## 📱 Mobile App Changes

Same changes apply! Just use React Native components:

```javascript
// Availability badge
<View style={serviceman.is_available ? styles.badgeGreen : styles.badgeOrange}>
  <Text>{serviceman.is_available ? 'Available' : 'Busy'}</Text>
</View>

// Approval status
{!serviceman.is_approved && (
  <View style={styles.pendingScreen}>
    <Text>⏳ Application Under Review</Text>
  </View>
)}
```

---

## 🧪 Quick Test

### Test New Endpoints
```javascript
// In browser console
const token = localStorage.getItem('access_token');

// 1. Test servicemen list
fetch('/api/users/servicemen/', {
  headers: { 'Authorization': `Bearer ${token}` }
})
  .then(r => r.json())
  .then(console.log);

// 2. Test pending list (admin only)
fetch('/api/users/admin/pending-servicemen/', {
  headers: { 'Authorization': `Bearer ${token}` }
})
  .then(r => r.json())
  .then(console.log);

// 3. Test skills
fetch('/api/users/skills/')
  .then(r => r.json())
  .then(console.log);
```

---

## ⚡ Priority Tasks

### THIS WEEK (Critical)
1. **[ ] Add approval status check to serviceman dashboard**
2. **[ ] Create admin approval page**
3. **[ ] Add availability badges everywhere**
4. **[ ] Add booking warnings**

### NEXT WEEK (Important)
5. **[ ] Skills display on profiles**
6. **[ ] Category assignment interface**
7. **[ ] Enhanced search/filters**
8. **[ ] Admin notification sender UI**

---

## 📚 Documentation

**Start Here**: `FRONTEND_DEVELOPER_UPDATES.md` (complete guide)  
**Quick Scan**: `WHATS_CHANGED_FOR_FRONTEND.md` (this doc)  
**API Reference**: `API_ENDPOINTS_VISUAL_MAP.md`  
**Examples**: `FRONTEND_API_CONSUMPTION_GUIDE.md`  
**Interactive**: http://localhost:8000/api/docs/

---

## 🆘 Need Help?

**Question**: "How do I...?"  
**Answer**: Check `FRONTEND_DEVELOPER_UPDATES.md` - it has complete React examples

**Question**: "What's the endpoint for...?"  
**Answer**: Check `API_ENDPOINTS_VISUAL_MAP.md` - visual map of all 35+ endpoints

**Question**: "How does ... work?"  
**Answer**: Visit http://localhost:8000/api/docs/ - try it live!

---

**Status**: ✅ All changes documented  
**Code Examples**: 50+ React components  
**Ready**: Production ready  
**Support**: Full documentation provided

