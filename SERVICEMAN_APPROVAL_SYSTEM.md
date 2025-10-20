# ✅ Serviceman Application Approval System

## 📋 Overview

A complete admin approval workflow for serviceman applications. Servicemen who register must be reviewed and approved by an admin before they can be assigned to jobs or appear in public listings.

---

## ✨ Features

### Approval Workflow
```
Serviceman Registers
       ↓
Email Verification
       ↓
⏳ PENDING (is_approved = False)
       ↓
Admin Reviews Application
       ↓
   ┌───────────┐
   │  Approve  │ OR │  Reject  │
   └───────────┘
       ↓               ↓
✅ APPROVED      ❌ REJECTED
Can work          Cannot work
Public listing    Not in listings
```

### New Database Fields
```python
class ServicemanProfile:
    is_approved = BooleanField(default=False)
    approved_by = ForeignKey(User)  # Which admin approved
    approved_at = DateTimeField()   # When approved
    rejection_reason = TextField()  # Why rejected
```

---

## 🚀 API Endpoints

### 1. List Pending Applications

**Endpoint**: `GET /api/users/admin/pending-servicemen/`

**Auth**: Admin only

**Purpose**: View all serviceman applications awaiting approval

**Response:**
```json
{
  "total_pending": 5,
  "pending_applications": [
    {
      "user": 15,
      "category": null,
      "skills": [],
      "rating": "0.00",
      "total_jobs_completed": 0,
      "bio": "Experienced electrician with 10 years",
      "years_of_experience": 10,
      "phone_number": "+2348012345678",
      "is_available": true,
      "is_approved": false,
      "approved_by": null,
      "approved_at": null,
      "rejection_reason": "",
      "created_at": "2025-10-18T10:00:00Z"
    }
  ]
}
```

**Example:**
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/users/admin/pending-servicemen/
```

---

### 2. Approve Serviceman Application

**Endpoint**: `POST /api/users/admin/approve-serviceman/`

**Auth**: Admin only

**Purpose**: Approve a serviceman application

**Request Body:**
```json
{
  "serviceman_id": 15,
  "category_id": 2,
  "notes": "Verified credentials, approved for electrical work"
}
```

**Required**: `serviceman_id`  
**Optional**: `category_id` (assign category during approval), `notes`

**Response:**
```json
{
  "detail": "Serviceman application approved successfully",
  "serviceman": {
    "id": 15,
    "username": "john_electrician",
    "full_name": "John Smith",
    "email": "john@example.com"
  },
  "approved_by": "admin",
  "approved_at": "2025-10-18T14:30:00Z",
  "category": {
    "id": 2,
    "name": "Electrical"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/users/admin/approve-serviceman/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceman_id": 15,
    "category_id": 2,
    "notes": "Approved for electrical work"
  }'
```

---

### 3. Reject Serviceman Application

**Endpoint**: `POST /api/users/admin/reject-serviceman/`

**Auth**: Admin only

**Purpose**: Reject a serviceman application with reason

**Request Body:**
```json
{
  "serviceman_id": 15,
  "rejection_reason": "Insufficient experience or qualifications not verified"
}
```

**Required**: `serviceman_id`, `rejection_reason`

**Response:**
```json
{
  "detail": "Serviceman application rejected",
  "serviceman": {
    "id": 15,
    "username": "john_electrician",
    "email": "john@example.com"
  },
  "rejected_by": "admin",
  "rejection_reason": "Insufficient experience or qualifications not verified"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/users/admin/reject-serviceman/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceman_id": 15,
    "rejection_reason": "Insufficient documentation provided"
  }'
```

---

## 🎯 Complete Admin Workflow

### Serviceman Application Review Flow

```javascript
// React Component - Admin Approval Dashboard
import React, { useState, useEffect } from 'react';

function ServicemanApprovalDashboard() {
  const [pendingApplications, setPendingApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  
  useEffect(() => {
    loadPendingApplications();
    loadCategories();
  }, []);
  
  const loadPendingApplications = async () => {
    const response = await fetch('/api/users/admin/pending-servicemen/', {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    });
    const data = await response.json();
    setPendingApplications(data.pending_applications);
    setLoading(false);
  };
  
  const loadCategories = async () => {
    const response = await fetch('/api/categories/');
    const data = await response.json();
    setCategories(data);
  };
  
  const approveServiceman = async (servicemanId, categoryId) => {
    try {
      const response = await fetch('/api/users/admin/approve-serviceman/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          serviceman_id: servicemanId,
          category_id: categoryId
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert(data.detail);
        loadPendingApplications(); // Reload list
      } else {
        alert('Error: ' + data.detail);
      }
    } catch (error) {
      alert('Failed to approve: ' + error.message);
    }
  };
  
  const rejectServiceman = async (servicemanId, reason) => {
    if (!reason) {
      alert('Please provide a rejection reason');
      return;
    }
    
    try {
      const response = await fetch('/api/users/admin/reject-serviceman/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          serviceman_id: servicemanId,
          rejection_reason: reason
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert(data.detail);
        loadPendingApplications(); // Reload list
      } else {
        alert('Error: ' + data.detail);
      }
    } catch (error) {
      alert('Failed to reject: ' + error.message);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="admin-approval-dashboard">
      <h1>Pending Serviceman Applications</h1>
      <p className="text-gray-600">
        {pendingApplications.length} application(s) awaiting review
      </p>
      
      {pendingApplications.length === 0 ? (
        <div className="empty-state">
          <p>✅ No pending applications</p>
        </div>
      ) : (
        <div className="applications-grid">
          {pendingApplications.map(app => (
            <ApplicationCard
              key={app.user}
              application={app}
              categories={categories}
              onApprove={approveServiceman}
              onReject={rejectServiceman}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Application Card Component
function ApplicationCard({ application, categories, onApprove, onReject }) {
  const [selectedCategory, setSelectedCategory] = useState(application.category?.id || '');
  const [rejectionReason, setRejectionReason] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(false);
  
  const handleApprove = () => {
    if (!selectedCategory) {
      if (!confirm('No category selected. Approve without category?')) {
        return;
      }
    }
    onApprove(application.user, selectedCategory || null);
  };
  
  const handleReject = () => {
    onReject(application.user, rejectionReason);
    setShowRejectForm(false);
  };
  
  return (
    <div className="application-card">
      {/* Application Header */}
      <div className="card-header">
        <h3>{application.user.full_name || application.user.username}</h3>
        <span className="badge badge-yellow">⏳ Pending</span>
      </div>
      
      {/* Application Details */}
      <div className="card-body">
        <div className="detail-row">
          <strong>Email:</strong> {application.user.email}
        </div>
        <div className="detail-row">
          <strong>Phone:</strong> {application.phone_number || 'Not provided'}
        </div>
        <div className="detail-row">
          <strong>Experience:</strong> {application.years_of_experience || 'Not specified'} years
        </div>
        <div className="detail-row">
          <strong>Bio:</strong> {application.bio || 'No bio provided'}
        </div>
        <div className="detail-row">
          <strong>Skills:</strong>
          {application.skills.length > 0 ? (
            <div className="skills-list">
              {application.skills.map(skill => (
                <span key={skill.id} className="skill-badge">
                  {skill.name}
                </span>
              ))}
            </div>
          ) : (
            <span className="text-gray-500">No skills added</span>
          )}
        </div>
        <div className="detail-row">
          <strong>Applied:</strong> {new Date(application.created_at).toLocaleString()}
        </div>
      </div>
      
      {/* Approval Actions */}
      <div className="card-footer">
        {!showRejectForm ? (
          <>
            {/* Category Selection */}
            <div className="form-group">
              <label>Assign Category:</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="form-control"
              >
                <option value="">-- Select Category --</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>
                    {cat.name}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Action Buttons */}
            <div className="button-group">
              <button 
                onClick={handleApprove}
                className="btn btn-success"
              >
                ✅ Approve
              </button>
              <button 
                onClick={() => setShowRejectForm(true)}
                className="btn btn-danger"
              >
                ❌ Reject
              </button>
            </div>
          </>
        ) : (
          <>
            {/* Rejection Form */}
            <div className="reject-form">
              <label>Rejection Reason:</label>
              <textarea
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Provide a clear reason for rejection..."
                className="form-control"
                rows={3}
              />
              <div className="button-group mt-2">
                <button 
                  onClick={handleReject}
                  className="btn btn-danger"
                  disabled={!rejectionReason}
                >
                  Confirm Rejection
                </button>
                <button 
                  onClick={() => setShowRejectForm(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default ServicemanApprovalDashboard;
```

---

## 🔒 Access Control

### Public Listings
- **Show only approved servicemen** by default
- Unapproved servicemen don't appear in:
  - `/api/users/servicemen/`
  - `/api/categories/{id}/servicemen/`
  - Public searches

### Admin Access
- **Admins can see all servicemen** using `?show_all=true`:
  ```bash
  GET /api/users/servicemen/?show_all=true
  ```

### Serviceman Access
- **Unapproved servicemen can**:
  - Login to their account
  - View their own profile
  - See "Pending Approval" status
  
- **Unapproved servicemen cannot**:
  - Be assigned to service requests
  - Appear in public listings
  - Accept jobs

---

## 📧 Auto-Notifications

### On Approval
Serviceman receives notification:
```
Title: Serviceman Application Approved
Message: Congratulations! Your serviceman application has been approved.
You can now be assigned to service requests and start accepting jobs.
```

### On Rejection
Serviceman receives notification:
```
Title: Serviceman Application Update
Message: We regret to inform you that your serviceman application has not
been approved at this time. Reason: [rejection_reason]. If you have
questions, please contact support.
```

---

## 🧪 Testing

### Test Complete Workflow

```bash
# 1. Register as serviceman
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_serviceman",
    "email": "serviceman@example.com",
    "password": "SecurePass123!",
    "user_type": "SERVICEMAN"
  }'

# 2. Get admin token
ADMIN_TOKEN=$(curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' \
  | jq -r '.access')

# 3. List pending applications
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/users/admin/pending-servicemen/

# 4. Approve serviceman
curl -X POST http://localhost:8000/api/users/admin/approve-serviceman/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceman_id": 15,
    "category_id": 2
  }'

# 5. Verify serviceman is now in public listings
curl http://localhost:8000/api/users/servicemen/
```

---

## 📊 Admin Dashboard Examples

### Pending Applications Counter
```javascript
function PendingApprovalsBadge() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const fetchCount = async () => {
      const response = await fetch('/api/users/admin/pending-servicemen/', {
        headers: { 'Authorization': `Bearer ${adminToken}` }
      });
      const data = await response.json();
      setCount(data.total_pending);
    };
    
    fetchCount();
    
    // Poll every minute
    const interval = setInterval(fetchCount, 60000);
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="nav-item">
      <a href="/admin/pending-approvals">
        Pending Approvals
        {count > 0 && <span className="badge badge-red">{count}</span>}
      </a>
    </div>
  );
}
```

### Quick Approval Interface
```javascript
function QuickApprovalInterface() {
  const [pending, setPending] = useState([]);
  
  const quickApprove = async (servicemanId, categoryId) => {
    await fetch('/api/users/admin/approve-serviceman/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${adminToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        serviceman_id: servicemanId,
        category_id: categoryId
      })
    });
    
    // Reload list
    loadPending();
  };
  
  return (
    <div className="quick-approval">
      <h2>Quick Approvals ({pending.length})</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Experience</th>
            <th>Applied</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {pending.map(app => (
            <tr key={app.user}>
              <td>{app.user.username}</td>
              <td>{app.years_of_experience} years</td>
              <td>{new Date(app.created_at).toLocaleDateString()}</td>
              <td>
                <button onClick={() => quickApprove(app.user, app.category?.id)}>
                  ✅ Approve
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 🔍 Filtering

### View Only Approved Servicemen (Default)
```bash
GET /api/users/servicemen/
```

### View All Including Pending (Admin Only)
```bash
GET /api/users/servicemen/?show_all=true
```

### View Only Unapproved (Admin Only)
```bash
GET /api/users/admin/pending-servicemen/
```

---

## 🎨 UI/UX Recommendations

### Serviceman Dashboard (If Pending)
```javascript
function ServicemanDashboard({ user }) {
  if (!user.serviceman_profile.is_approved) {
    return (
      <div className="pending-approval-screen">
        <div className="alert alert-info">
          <h2>⏳ Application Under Review</h2>
          <p>Your serviceman application is currently being reviewed by our team.</p>
          <p>You will be notified via email once your application is approved.</p>
          <p>Applied: {new Date(user.serviceman_profile.created_at).toLocaleDateString()}</p>
        </div>
        
        <div className="what-next">
          <h3>While You Wait:</h3>
          <ul>
            <li>✅ Email verification completed</li>
            <li>⏳ Admin approval pending</li>
            <li>📧 Check your email for updates</li>
          </ul>
        </div>
      </div>
    );
  }
  
  // Normal dashboard for approved servicemen
  return <ApprovedServicemanDashboard user={user} />;
}
```

### Admin Notification of New Applications
```javascript
// Send notification when new serviceman registers
// In your registration success handler:

// After serviceman registers, notify admins
const admins = await fetch('/api/users/servicemen/?user_type=ADMIN');

for (const admin of admins) {
  await fetch('/api/notifications/send/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${systemToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      user_id: admin.id,
      title: 'New Serviceman Application',
      message: `${newServiceman.username} has applied to join as a serviceman. Please review.`
    })
  });
}
```

---

## 📋 Admin Interface (Django Admin)

### Features Added
- ✅ **List Display**: Shows approval status badge
- ✅ **Filters**: Filter by approved/pending/rejected
- ✅ **Bulk Actions**: Approve or reject multiple at once
- ✅ **Approval Section**: Dedicated fieldset for approval data
- ✅ **Audit Trail**: Shows who approved and when

### Access Django Admin
```
http://localhost:8000/admin/users/servicemanprofile/
```

Filter by:
- Is approved: Yes/No
- Approved at: Date range

Bulk actions:
- Approve selected servicemen
- Reject selected servicemen

---

## 🔧 Migration Required

After adding approval fields, run:

```bash
python manage.py makemigrations users
python manage.py migrate
```

### Approve Existing Servicemen

If you have existing servicemen, approve them:

```python
python manage.py shell

from apps.users.models import ServicemanProfile
from django.utils import timezone

# Approve all existing servicemen
ServicemanProfile.objects.filter(is_approved=False).update(
    is_approved=True,
    approved_at=timezone.now()
)

print("All existing servicemen approved!")
```

---

## 📈 Analytics Queries

### Approval Statistics
```python
from apps.users.models import ServicemanProfile
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

# Get counts
stats = ServicemanProfile.objects.aggregate(
    total=Count('id'),
    approved=Count('id', filter=Q(is_approved=True)),
    pending=Count('id', filter=Q(is_approved=False, rejection_reason='')),
    rejected=Count('id', filter=Q(rejection_reason__isnull=False))
)

# Applications in last 7 days
recent = ServicemanProfile.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=7),
    is_approved=False
).count()

print(f"Total: {stats['total']}")
print(f"Approved: {stats['approved']}")
print(f"Pending: {stats['pending']}")
print(f"Rejected: {stats['rejected']}")
print(f"New in last 7 days: {recent}")
```

### Approval Time Analysis
```python
from django.db.models import Avg, F

avg_approval_time = ServicemanProfile.objects.filter(
    is_approved=True,
    approved_at__isnull=False
).annotate(
    approval_duration=F('approved_at') - F('created_at')
).aggregate(
    avg_time=Avg('approval_duration')
)

print(f"Average approval time: {avg_approval_time['avg_time']}")
```

---

## ✅ Benefits

### For Platform
✅ **Quality Control** - Review servicemen before activation  
✅ **Fraud Prevention** - Verify credentials  
✅ **Professional Standards** - Ensure quality  
✅ **Brand Protection** - Only qualified servicemen  

### For Clients
✅ **Trust** - All servicemen are vetted  
✅ **Quality** - Only approved professionals  
✅ **Safety** - Background checked  

### For Servicemen
✅ **Clear Process** - Know application status  
✅ **Transparency** - Notified of decision  
✅ **Professionalism** - Part of vetted platform  

---

## 🚨 Important Notes

### Migration Impact
- **Existing servicemen**: Will be `is_approved=False` by default
- **Action required**: Run migration then approve existing servicemen
- **Or**: Change default to `True` during migration

### Backwards Compatibility
```python
# Option 1: Approve all existing during migration
def forwards(apps, schema_editor):
    ServicemanProfile = apps.get_model('users', 'ServicemanProfile')
    from django.utils import timezone
    ServicemanProfile.objects.update(
        is_approved=True,
        approved_at=timezone.now()
    )

# Option 2: Set default=True in model (not recommended)
is_approved = models.BooleanField(default=True)
```

---

## 📞 Support

**Complete Guide**: This document  
**Quick Reference**: ADMIN_ENDPOINTS_QUICK_REFERENCE.md  
**API Docs**: http://localhost:8000/api/docs/

---

**Status**: ✅ IMPLEMENTED  
**Endpoints**: 3 new admin approval endpoints  
**Migration**: Required  
**Notifications**: Automatic

