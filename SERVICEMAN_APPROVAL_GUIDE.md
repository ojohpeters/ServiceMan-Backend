# 👨‍🔧 Serviceman Approval System - Complete Guide

## 📋 Overview

When a user registers as a **SERVICEMAN**, they are **NOT immediately active**. Their profile is created with `is_approved = False`, and they must wait for admin approval before they can:
- Be assigned to service requests
- Appear in public serviceman listings
- Be visible to clients

**Admin has two options:**
1. ✅ **Approve** - Activate the serviceman
2. ❌ **Reject** - Decline with a reason

---

## 🔄 Serviceman Registration Flow

### 1. User Registers as Serviceman

**Endpoint**: `POST /api/users/register/`

```javascript
const response = await fetch('https://serviceman-backend.onrender.com/api/users/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'john_plumber',
    email: 'john@example.com',
    password: 'SecurePass123!',
    password2: 'SecurePass123!',
    first_name: 'John',
    last_name: 'Smith',
    phone_number: '+2348012345678',
    user_type: 'SERVICEMAN',
    category_id: 2, // Plumbing
    skill_ids: [1, 3, 5], // Optional: Pipe repair, Installation, etc.
    bio: 'Experienced plumber with 10 years experience',
    years_of_experience: 10
  })
});

const data = await response.json();
// User created with is_approved = false
```

**What Happens:**
- ✅ User account created
- ✅ ServicemanProfile created with `is_approved = false`
- ✅ Email verification sent
- ❌ **NOT visible** in public listings
- ❌ **CANNOT be assigned** to jobs

---

### 2. Admin Views Pending Servicemen

**Endpoint**: `GET /api/users/admin/pending-servicemen/`

**Who Can Access**: Admins only

```javascript
const response = await fetch(
  'https://serviceman-backend.onrender.com/api/users/admin/pending-servicemen/',
  {
    headers: {
      'Authorization': `Bearer ${adminAccessToken}`
    }
  }
);

const pendingServicemen = await response.json();
```

**Response Example**:
```json
[
  {
    "user": {
      "id": 25,
      "username": "john_plumber",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Smith",
      "user_type": "SERVICEMAN",
      "phone_number": "+2348012345678",
      "is_email_verified": true
    },
    "category": {
      "id": 2,
      "name": "Plumbing",
      "description": "Water and drainage systems"
    },
    "skills": [
      {
        "id": 1,
        "name": "Pipe Repair",
        "category": "TECHNICAL"
      },
      {
        "id": 3,
        "name": "Installation",
        "category": "TECHNICAL"
      }
    ],
    "bio": "Experienced plumber with 10 years experience",
    "years_of_experience": 10,
    "rating": "0.00",
    "total_jobs_completed": 0,
    "is_available": true,
    "is_approved": false,
    "approved_by": null,
    "approved_at": null,
    "rejection_reason": null,
    "created_at": "2025-11-03T10:30:00Z"
  }
]
```

**Admin Dashboard UI:**
```tsx
// Example Admin Dashboard Component
const PendingServicemenList = () => {
  const [pending, setPending] = useState([]);
  
  useEffect(() => {
    fetchPendingServicemen();
  }, []);
  
  const fetchPendingServicemen = async () => {
    const response = await fetch(
      'https://serviceman-backend.onrender.com/api/users/admin/pending-servicemen/',
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    const data = await response.json();
    setPending(data);
  };
  
  return (
    <div className="pending-list">
      <h2>Pending Serviceman Applications</h2>
      {pending.map(serviceman => (
        <ServicemanCard key={serviceman.user.id} data={serviceman} />
      ))}
    </div>
  );
};
```

---

### 3A. Admin APPROVES Serviceman ✅

**Endpoint**: `POST /api/users/admin/approve-serviceman/`

**Who Can Access**: Admins only

**Request**:
```javascript
const response = await fetch(
  'https://serviceman-backend.onrender.com/api/users/admin/approve-serviceman/',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminAccessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      serviceman_id: 25
    })
  }
);

const result = await response.json();
```

**Success Response** (200):
```json
{
  "detail": "Serviceman application approved successfully",
  "serviceman": {
    "id": 25,
    "username": "john_plumber",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Smith"
  },
  "approved_by": "admin_user",
  "approved_at": "2025-11-03T14:20:00Z",
  "message": "Serviceman can now be assigned to service requests and is visible in listings."
}
```

**What Happens:**
- ✅ `is_approved = True`
- ✅ `approved_by = admin_user_id`
- ✅ `approved_at = current_timestamp`
- ✅ **Notification sent to serviceman**: "Your application has been approved!"
- ✅ **Now visible** in public listings
- ✅ **Can be assigned** to service requests
- ✅ **Can receive jobs**

**Errors**:
```json
// 403 - Not admin
{
  "detail": "Only administrators can approve servicemen"
}

// 404 - Serviceman not found
{
  "detail": "Serviceman with ID 25 not found"
}

// 400 - Already approved
{
  "detail": "This serviceman is already approved"
}

// 503 - Migrations not run
{
  "detail": "Approval system not available. Database migrations needed.",
  "migration_needed": "0003_servicemanprofile_approval_fields"
}
```

---

### 3B. Admin REJECTS Serviceman ❌

**Endpoint**: `POST /api/users/admin/reject-serviceman/`

**Who Can Access**: Admins only

**Request**:
```javascript
const response = await fetch(
  'https://serviceman-backend.onrender.com/api/users/admin/reject-serviceman/',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminAccessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      serviceman_id: 25,
      rejection_reason: "Insufficient experience. Minimum 5 years required for this category."
    })
  }
);

const result = await response.json();
```

**Success Response** (200):
```json
{
  "detail": "Serviceman application rejected",
  "serviceman": {
    "id": 25,
    "username": "john_plumber",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Smith"
  },
  "rejected_by": "admin_user",
  "rejection_reason": "Insufficient experience. Minimum 5 years required for this category."
}
```

**What Happens:**
- ✅ `rejection_reason` saved to database
- ✅ `is_approved` remains `False`
- ✅ **Notification sent to serviceman**: "Your application was not approved. Reason: ..."
- ❌ **NOT visible** in listings
- ❌ **CANNOT be assigned** to jobs
- ℹ️ User can still login but cannot work as serviceman

**Errors**:
```json
// 403 - Not admin
{
  "detail": "Only administrators can reject servicemen"
}

// 404 - Serviceman not found
{
  "detail": "Serviceman with ID 25 not found"
}

// 400 - No reason provided
{
  "detail": "rejection_reason is required"
}

// 400 - Already approved
{
  "detail": "Cannot reject an already approved serviceman. Consider deactivating their account instead."
}
```

---

## 🎨 Frontend Implementation Examples

### Admin Dashboard - Pending Applications

```tsx
import React, { useState } from 'react';

const ServicemanApplicationCard = ({ application, onApprove, onReject }) => {
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [loading, setLoading] = useState(false);
  
  const handleApprove = async () => {
    if (!confirm(`Approve ${application.user.first_name} ${application.user.last_name}?`)) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(
        'https://serviceman-backend.onrender.com/api/users/admin/approve-serviceman/',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            serviceman_id: application.user.id
          })
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        showSuccess('Serviceman approved successfully!');
        onApprove(application.user.id);
      } else {
        const error = await response.json();
        showError(error.detail || 'Failed to approve');
      }
    } catch (error) {
      showError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleReject = async () => {
    if (!rejectReason.trim()) {
      showError('Please provide a reason for rejection');
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(
        'https://serviceman-backend.onrender.com/api/users/admin/reject-serviceman/',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            serviceman_id: application.user.id,
            rejection_reason: rejectReason
          })
        }
      );
      
      if (response.ok) {
        showSuccess('Application rejected');
        setShowRejectModal(false);
        onReject(application.user.id);
      } else {
        const error = await response.json();
        showError(error.detail || 'Failed to reject');
      }
    } catch (error) {
      showError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="application-card">
      <div className="applicant-info">
        <h3>{application.user.first_name} {application.user.last_name}</h3>
        <p className="email">{application.user.email}</p>
        <p className="phone">{application.user.phone_number}</p>
      </div>
      
      <div className="details">
        <div className="category">
          <strong>Category:</strong> {application.category.name}
        </div>
        <div className="experience">
          <strong>Experience:</strong> {application.years_of_experience} years
        </div>
        <div className="skills">
          <strong>Skills:</strong>
          {application.skills.map(skill => (
            <span key={skill.id} className="skill-badge">{skill.name}</span>
          ))}
        </div>
        <div className="bio">
          <strong>Bio:</strong>
          <p>{application.bio}</p>
        </div>
      </div>
      
      <div className="actions">
        <button 
          onClick={handleApprove} 
          disabled={loading}
          className="btn-approve"
        >
          ✅ Approve
        </button>
        <button 
          onClick={() => setShowRejectModal(true)}
          disabled={loading}
          className="btn-reject"
        >
          ❌ Reject
        </button>
      </div>
      
      {showRejectModal && (
        <div className="modal">
          <div className="modal-content">
            <h3>Reject Application</h3>
            <p>Rejecting: {application.user.first_name} {application.user.last_name}</p>
            <textarea
              placeholder="Provide a reason for rejection (required)"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={4}
              required
            />
            <div className="modal-actions">
              <button onClick={() => setShowRejectModal(false)}>Cancel</button>
              <button onClick={handleReject} disabled={loading}>
                {loading ? 'Rejecting...' : 'Confirm Rejection'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

### Common Rejection Reasons (Suggested Dropdown)

```tsx
const REJECTION_REASONS = [
  "Insufficient experience for the category",
  "Incomplete profile information",
  "Skills do not match the selected category",
  "Unable to verify credentials",
  "Service area not currently covered",
  "Previous complaints or negative reviews",
  "Duplicate application",
  "Other (please specify)"
];

// In your rejection modal:
<select onChange={(e) => setRejectReason(e.target.value)}>
  <option value="">Select a reason...</option>
  {REJECTION_REASONS.map(reason => (
    <option key={reason} value={reason}>{reason}</option>
  ))}
</select>

{rejectReason === "Other (please specify)" && (
  <textarea 
    placeholder="Please specify the reason"
    onChange={(e) => setCustomReason(e.target.value)}
  />
)}
```

---

## 📊 Serviceman Status States

| State | `is_approved` | Visible to Clients? | Can Be Assigned? | Can Work? |
|-------|---------------|---------------------|------------------|-----------|
| **Pending** | `false` | ❌ No | ❌ No | ❌ No |
| **Approved** | `true` | ✅ Yes | ✅ Yes | ✅ Yes |
| **Rejected** | `false` + has `rejection_reason` | ❌ No | ❌ No | ❌ No |

---

## 🔔 Notifications Sent

### On Approval:
**To Serviceman:**
```
Title: "Serviceman Application Approved"
Message: "Congratulations! Your serviceman application has been approved by [admin_username]. 
You can now be assigned to service requests and are visible in serviceman listings."
Type: GENERAL
```

### On Rejection:
**To Serviceman:**
```
Title: "Serviceman Application Status"
Message: "We regret to inform you that your serviceman application has not been approved at this time. 
Reason: [rejection_reason]. 
You may contact support for more information or reapply with updated credentials."
Type: GENERAL
```

---

## 🔐 Security & Permissions

### Who Can Approve/Reject:
- ✅ **ADMIN users only**
- ❌ Servicemen cannot approve themselves
- ❌ Clients have no access
- ❌ Unauthenticated users have no access

### Validation Rules:
1. ✅ Admin must be authenticated
2. ✅ Serviceman ID must exist
3. ✅ Serviceman must be user_type = 'SERVICEMAN'
4. ✅ Cannot approve already approved servicemen
5. ✅ Cannot reject already approved servicemen
6. ✅ Rejection reason is **required** for rejections
7. ✅ Approval/rejection is logged with timestamp and admin user

---

## 📱 API Endpoints Summary

| Endpoint | Method | Role | Purpose |
|----------|--------|------|---------|
| `/api/users/admin/pending-servicemen/` | GET | Admin | List all pending applications |
| `/api/users/admin/approve-serviceman/` | POST | Admin | Approve a serviceman |
| `/api/users/admin/reject-serviceman/` | POST | Admin | Reject with reason |
| `/api/users/servicemen/?show_all=true` | GET | Admin | View all servicemen (approved + pending) |
| `/api/users/servicemen/` | GET | Public | View only approved servicemen |

---

## 🎯 Best Practices

### For Admins:
1. ✅ **Review carefully** - Check experience, skills, and credentials
2. ✅ **Be specific** - Provide clear, actionable rejection reasons
3. ✅ **Be prompt** - Review applications within 24-48 hours
4. ✅ **Communicate** - Use notifications to keep applicants informed
5. ✅ **Document** - Keep track of approval/rejection reasons

### For Frontend:
1. ✅ **Show pending count** - Display badge with number of pending applications
2. ✅ **Validate input** - Require rejection reason before allowing rejection
3. ✅ **Provide templates** - Offer common rejection reasons in dropdown
4. ✅ **Confirm actions** - Ask for confirmation before approval/rejection
5. ✅ **Update lists** - Refresh pending list after approval/rejection
6. ✅ **Show feedback** - Display success/error messages clearly

---

## 🚀 Quick Start Checklist

### Admin Dashboard Implementation:

- [ ] Add "Pending Applications" section to admin dashboard
- [ ] Fetch pending servicemen on page load
- [ ] Display application details (name, category, skills, bio, experience)
- [ ] Add "Approve" button with confirmation
- [ ] Add "Reject" button with reason modal
- [ ] Implement rejection reason dropdown with common reasons
- [ ] Show success/error messages
- [ ] Refresh list after approval/rejection
- [ ] Add notification badge for new applications
- [ ] Test approval flow end-to-end
- [ ] Test rejection flow with reasons
- [ ] Verify notifications are sent

---

## 📞 Support

For questions:
- Check this guide first
- Review API documentation: `API_DOCUMENTATION_FOR_FRONTEND.md`
- Contact backend team

---

**Last Updated**: November 2025  
**Status**: ✅ Fully Implemented and Ready
