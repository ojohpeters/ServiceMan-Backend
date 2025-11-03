# Professional Service Request Workflow Documentation

## 🎯 Overview

This document describes the complete professional workflow for service requests in the ServiceMan platform. **All communication flows through the admin as the central bridge** - there is NO direct communication between clients and servicemen through the system.

## 🔄 Complete Workflow with Notifications

### **STEP 1: Client Books Service & Pays Booking Fee**

**Action**: Client creates service request after paying booking fee

**Endpoint**: `POST /api/services/service-requests/`

**Request Body**:
```json
{
  "category_id": 1,
  "booking_date": "2025-11-05",
  "is_emergency": false,
  "client_address": "123 Main St, Lagos",
  "service_description": "Need plumbing repair for leaking pipes",
  "payment_reference": "PAY_REF_FROM_PAYSTACK"
}
```

**Status Change**: → `PENDING_ADMIN_ASSIGNMENT`

**Notifications Sent**:
- ✅ **ADMIN**: "New Service Request #X - Client Y has booked a service. Please assign a serviceman."
- ✅ **CLIENT**: "Service Request Received - Our admin will review and assign a serviceman shortly."

**Who Can See**:
- Admin: All pending requests
- Client: Their own request

---

### **STEP 2: Admin Assigns Serviceman**

**Action**: Admin selects and assigns serviceman to the request

**Endpoint**: `POST /api/services/service-requests/{id}/assign/`

**Request Body**:
```json
{
  "serviceman_id": 5,
  "backup_serviceman_id": 7,
  "notes": "Client prefers morning appointments"
}
```

**Status Change**: `PENDING_ADMIN_ASSIGNMENT` → `PENDING_ESTIMATION`

**Notifications Sent**:
- ✅ **SERVICEMAN**: "New Job Assignment - Request #X. Contact client to schedule site visit and provide cost estimate. Client contact: Name, Phone"
- ✅ **CLIENT**: "Serviceman Assigned - A serviceman will contact you shortly to schedule a site visit."
- ❌ **ADMIN**: No notification (admin performed the action)

**Who Can See**:
- Admin: Full request details
- Serviceman: Assigned job with client contact info
- Client: Request status update

**Next Step**: Serviceman contacts client directly via phone to schedule site visit.

---

### **STEP 3: Serviceman Submits Cost Estimate**

**Action**: After site inspection, serviceman submits cost estimate through dashboard

**Endpoint**: `POST /api/services/service-requests/{id}/submit-estimate/`

**Request Body**:
```json
{
  "estimated_cost": 25000.00,
  "notes": "Includes parts replacement and 2 days labor"
}
```

**Status Change**: `PENDING_ESTIMATION` → `ESTIMATION_SUBMITTED`

**Notifications Sent**:
- ✅ **ADMIN**: "Cost Estimate Submitted - Serviceman X submitted estimate of ₦25,000 for request #Y. Please review and add platform fee."
- ❌ **CLIENT**: No notification yet (admin reviews first)
- ❌ **SERVICEMAN**: No notification (serviceman performed the action)

**Who Can See**:
- Admin: Estimate details
- Serviceman: Confirmation of submission
- Client: Status shows "Processing" (no cost visible yet)

---

### **STEP 4: Admin Finalizes Price with Platform Fee**

**Action**: Admin reviews estimate, adds platform fee, and sends to client

**Endpoint**: `POST /api/services/service-requests/{id}/finalize-price/`

**Request Body**:
```json
{
  "markup_percentage": 10,
  "admin_notes": "Price includes all materials and labor"
}
```

**Calculation**:
- Base Cost: ₦25,000 (from serviceman)
- Platform Fee (10%): ₦2,500
- **Total**: ₦27,500

**Status Change**: `ESTIMATION_SUBMITTED` → `AWAITING_CLIENT_APPROVAL`

**Notifications Sent**:
- ✅ **CLIENT**: "Price Ready for Approval - Your service request has been priced at ₦27,500 (Service: ₦25,000 + Platform Fee: ₦2,500). Please review and proceed with payment."
- ❌ **ADMIN**: No notification (admin performed the action)
- ❌ **SERVICEMAN**: No notification (waits for payment confirmation)

**Who Can See**:
- Admin: Full pricing breakdown
- Client: Final cost with payment button
- Serviceman: Status shows "Awaiting Payment"

---

### **STEP 5: Client Pays Full Amount**

**Action**: Client approves and pays the final cost

**Endpoint**: 
1. Initialize: `POST /api/payments/initialize-payment/`
2. Verify: `POST /api/payments/verify-payment/`

**Status Change**: `AWAITING_CLIENT_APPROVAL` → `PAYMENT_COMPLETED`

**Notifications Sent**:
- ✅ **ADMIN**: "Payment Received - Client Y has paid ₦27,500 for request #X. Please authorize serviceman to begin work."
- ✅ **CLIENT**: "Payment Confirmed - Your payment has been confirmed. Work will begin shortly."
- ❌ **SERVICEMAN**: No notification yet (waits for admin authorization)

**Who Can See**:
- Admin: Payment confirmed, ready to authorize
- Client: Payment receipt
- Serviceman: Status shows "Payment Confirmed"

---

### **STEP 6: Admin Authorizes Work to Begin**

**Action**: Admin confirms payment and authorizes serviceman to start work

**Endpoint**: `POST /api/services/service-requests/{id}/authorize-work/`

**Request Body**:
```json
{
  "instructions": "Client available weekdays 9am-5pm"
}
```

**Status Change**: `PAYMENT_COMPLETED` → `IN_PROGRESS`

**Notifications Sent**:
- ✅ **SERVICEMAN**: "Work Authorized - Payment confirmed! Begin work on request #X. Job Amount: ₦25,000. Client: Name, Phone, Address."
- ✅ **CLIENT**: "Work Has Begun - Your service request is now in progress. The serviceman will contact you shortly."
- ❌ **ADMIN**: No notification (admin performed the action)

**Who Can See**:
- Admin: Job in progress
- Serviceman: Active job with full details
- Client: Work status "In Progress"

**Next Step**: Serviceman contacts client to coordinate and complete the work.

---

### **STEP 7: Serviceman Marks Job Complete**

**Action**: Serviceman completes work and marks job as done in dashboard

**Endpoint**: `POST /api/services/service-requests/{id}/complete-job/`

**Request Body**:
```json
{
  "completion_notes": "All pipes repaired and tested. No leaks detected."
}
```

**Status Change**: `IN_PROGRESS` → `COMPLETED`

**Notifications Sent**:
- ✅ **ADMIN**: "Job Completed - Serviceman X has marked request #Y as completed. Please verify and notify the client."
- ❌ **CLIENT**: No notification yet (admin verifies first)
- ❌ **SERVICEMAN**: No notification (serviceman performed the action)

**Who Can See**:
- Admin: Completion pending verification
- Serviceman: Job marked complete, awaiting confirmation
- Client: Status still shows "In Progress"

---

### **STEP 8: Admin Confirms Completion to Client**

**Action**: Admin verifies work is done and notifies client

**Endpoint**: `POST /api/services/service-requests/{id}/confirm-completion/`

**Request Body**:
```json
{
  "message_to_client": "Work has been verified as complete. Please check and rate your experience."
}
```

**Status Change**: `COMPLETED` → `COMPLETED` (remains same, awaiting review)

**Notifications Sent**:
- ✅ **CLIENT**: "Job Completed - Your service request has been completed successfully. Please rate your experience."
- ❌ **ADMIN**: No notification (admin performed the action)
- ❌ **SERVICEMAN**: No notification yet (waits for client review)

**Who Can See**:
- Admin: Awaiting client review
- Client: Review prompt
- Serviceman: Job complete, awaiting rating

---

### **STEP 9: Client Submits Rating & Review**

**Action**: Client rates the serviceman (1-5 stars) and optional feedback

**Endpoint**: `POST /api/services/service-requests/{id}/submit-review/`

**Request Body**:
```json
{
  "rating": 5,
  "review": "Excellent work! Very professional and timely."
}
```

**Status Change**: `COMPLETED` → `CLIENT_REVIEWED`

**Notifications Sent**:
- ✅ **SERVICEMAN**: "New Review - ⭐⭐⭐⭐⭐ You received a 5-star rating from Client Y. Review: Excellent work!"
- ✅ **ADMIN**: "Client Review Submitted - Client Y rated Serviceman X 5/5 stars."
- ❌ **CLIENT**: No notification (client performed the action)

**Who Can See**:
- Admin: Complete review
- Serviceman: Rating and review on profile
- Client: Thank you confirmation

**Workflow Complete!** ✅

---

## 📊 Status Flow Diagram

```
CLIENT BOOKS (pays booking fee)
         ↓
   [PENDING_ADMIN_ASSIGNMENT] 
         ↓ (Admin assigns)
   [PENDING_ESTIMATION]
         ↓ (Serviceman submits estimate)
   [ESTIMATION_SUBMITTED]
         ↓ (Admin adds platform fee)
   [AWAITING_CLIENT_APPROVAL]
         ↓ (Client pays full amount)
   [PAYMENT_COMPLETED]
         ↓ (Admin authorizes work)
   [IN_PROGRESS]
         ↓ (Serviceman completes)
   [COMPLETED]
         ↓ (Admin confirms to client)
   [COMPLETED] (awaiting review)
         ↓ (Client rates)
   [CLIENT_REVIEWED] ✅ FINAL
```

---

## 🔔 Notification Summary

| Action | Admin | Serviceman | Client |
|--------|-------|------------|--------|
| **1. Client books** | ✅ New request | ❌ | ✅ Confirmation |
| **2. Admin assigns** | ❌ | ✅ New job | ✅ Assigned |
| **3. Serviceman estimates** | ✅ Review estimate | ❌ | ❌ |
| **4. Admin finalizes price** | ❌ | ❌ | ✅ Payment request |
| **5. Client pays** | ✅ Payment received | ❌ | ✅ Confirmed |
| **6. Admin authorizes** | ❌ | ✅ Begin work | ✅ Started |
| **7. Serviceman completes** | ✅ Verify job | ❌ | ❌ |
| **8. Admin confirms** | ❌ | ❌ | ✅ Rate us |
| **9. Client reviews** | ✅ Review received | ✅ Rating | ❌ |

---

## 🎨 Frontend Implementation Guide

### Client Dashboard Views

#### 1. **Service Request Creation** (`PENDING_ADMIN_ASSIGNMENT`)
```typescript
// Show after successful booking fee payment
<div className="status-card">
  <StatusBadge status="PENDING_ADMIN_ASSIGNMENT" color="yellow" />
  <h3>Request Submitted</h3>
  <p>Waiting for admin to assign a serviceman.</p>
  <ActionButton disabled>Awaiting Assignment</ActionButton>
</div>
```

#### 2. **Serviceman Assigned** (`PENDING_ESTIMATION`)
```typescript
<div className="status-card">
  <StatusBadge status="PENDING_ESTIMATION" color="blue" />
  <h3>Serviceman Assigned</h3>
  <p>A serviceman will contact you for site inspection.</p>
  <ActionButton disabled>Awaiting Estimate</ActionButton>
</div>
```

#### 3. **Price Ready** (`AWAITING_CLIENT_APPROVAL`)
```typescript
<div className="status-card">
  <StatusBadge status="AWAITING_CLIENT_APPROVAL" color="orange" />
  <h3>Price Ready</h3>
  <PricingBreakdown>
    <Line>Service Cost: ₦{serviceman_cost}</Line>
    <Line>Platform Fee: ₦{platform_fee}</Line>
    <Line><strong>Total: ₦{final_cost}</strong></Line>
  </PricingBreakdown>
  <ActionButton onClick={handlePayment}>Pay Now</ActionButton>
</div>
```

#### 4. **Work in Progress** (`IN_PROGRESS`)
```typescript
<div className="status-card">
  <StatusBadge status="IN_PROGRESS" color="green" />
  <h3>Work in Progress</h3>
  <p>Serviceman is working on your request.</p>
  <ProgressIndicator active />
</div>
```

#### 5. **Job Complete** (`COMPLETED`)
```typescript
<div className="status-card">
  <StatusBadge status="COMPLETED" color="green" />
  <h3>Job Completed</h3>
  <p>Please rate your experience.</p>
  <ActionButton onClick={showReviewModal}>Rate Serviceman</ActionButton>
</div>
```

### Serviceman Dashboard Views

#### 1. **New Assignment** (`PENDING_ESTIMATION`)
```typescript
<div className="job-card">
  <StatusBadge status="PENDING_ESTIMATION" color="blue" />
  <h3>New Job Assignment</h3>
  <ClientInfo>
    <p>Name: {client.name}</p>
    <p>Phone: {client.phone}</p>
    <p>Address: {client_address}</p>
  </ClientInfo>
  <ActionButton onClick={showEstimateForm}>Submit Estimate</ActionButton>
</div>
```

#### 2. **Estimate Submitted** (`ESTIMATION_SUBMITTED`)
```typescript
<div className="job-card">
  <StatusBadge status="ESTIMATION_SUBMITTED" color="yellow" />
  <h3>Estimate Submitted</h3>
  <p>Your estimate: ₦{estimated_cost}</p>
  <p>Waiting for admin to finalize price.</p>
  <ActionButton disabled>Awaiting Admin</ActionButton>
</div>
```

#### 3. **Ready to Start** (`IN_PROGRESS`)
```typescript
<div className="job-card">
  <StatusBadge status="IN_PROGRESS" color="green" />
  <h3>Active Job</h3>
  <p>Job Amount: ₦{serviceman_cost}</p>
  <ClientInfo>{client.phone}</ClientInfo>
  <ActionButton onClick={markComplete}>Mark as Complete</ActionButton>
</div>
```

### Admin Dashboard Views

#### 1. **New Requests** (`PENDING_ADMIN_ASSIGNMENT`)
```typescript
<div className="admin-task">
  <StatusBadge status="PENDING_ADMIN_ASSIGNMENT" color="red" />
  <h3>New Request #{id}</h3>
  <p>Client: {client.name}</p>
  <p>Category: {category.name}</p>
  <ActionButton onClick={showAssignModal}>Assign Serviceman</ActionButton>
</div>
```

#### 2. **Review Estimate** (`ESTIMATION_SUBMITTED`)
```typescript
<div className="admin-task">
  <StatusBadge status="ESTIMATION_SUBMITTED" color="orange" />
  <h3>Review Estimate #{id}</h3>
  <p>Serviceman Estimate: ₦{serviceman_cost}</p>
  <InputField label="Platform Fee %" value={markup} />
  <p>Final Cost: ₦{calculated_final}</p>
  <ActionButton onClick={finalizePrice}>Send to Client</ActionButton>
</div>
```

#### 3. **Payment Received** (`PAYMENT_COMPLETED`)
```typescript
<div className="admin-task">
  <StatusBadge status="PAYMENT_COMPLETED" color="green" />
  <h3>Payment Received #{id}</h3>
  <p>Amount: ₦{payment_amount}</p>
  <p>Serviceman: {serviceman.name}</p>
  <ActionButton onClick={authorizeWork}>Authorize Work</ActionButton>
</div>
```

#### 4. **Job Done** (`COMPLETED`)
```typescript
<div className="admin-task">
  <StatusBadge status="COMPLETED" color="blue" />
  <h3>Job Completed #{id}</h3>
  <p>Serviceman: {serviceman.name}</p>
  <p>Completion Notes: {notes}</p>
  <ActionButton onClick={confirmToClient}>Confirm to Client</ActionButton>
</div>
```

---

## 🔐 Role-Based Access Control

### Client Can:
- ✅ Create service requests (after booking fee)
- ✅ View own requests
- ✅ Pay for approved estimates
- ✅ Submit reviews/ratings
- ❌ Contact serviceman directly through system
- ❌ See serviceman phone number
- ❌ Assign servicemen

### Serviceman Can:
- ✅ View assigned jobs
- ✅ See client contact info (for phone calls)
- ✅ Submit cost estimates
- ✅ Mark jobs complete
- ✅ View own ratings
- ❌ See payment amounts (only their service cost)
- ❌ Assign themselves to jobs
- ❌ Contact clients through system messages

### Admin Can:
- ✅ View all service requests
- ✅ Assign servicemen to requests
- ✅ Review and finalize pricing
- ✅ Authorize work to begin
- ✅ Confirm job completion
- ✅ View all payments
- ✅ Manage all users

---

## 🌟 Key Principles

1. **Admin is the Bridge**: All workflow transitions require admin action or approval
2. **Phone Communication**: Serviceman and client communicate directly via phone, not through the app
3. **Transparency**: Clients see final prices only after admin review
4. **Protection**: Platform fee is added by admin, not visible to serviceman
5. **Quality Control**: Admin verifies job completion before client notification
6. **Accountability**: Every action triggers appropriate notifications

---

## 📱 API Endpoints Summary

| Endpoint | Method | Role | Purpose |
|----------|--------|------|---------|
| `/api/services/service-requests/` | POST | Client | Create request |
| `/api/services/service-requests/{id}/assign/` | POST | Admin | Assign serviceman |
| `/api/services/service-requests/{id}/submit-estimate/` | POST | Serviceman | Submit cost |
| `/api/services/service-requests/{id}/finalize-price/` | POST | Admin | Add platform fee |
| `/api/payments/verify-payment/` | POST | System | Confirm payment |
| `/api/services/service-requests/{id}/authorize-work/` | POST | Admin | Start job |
| `/api/services/service-requests/{id}/complete-job/` | POST | Serviceman | Mark done |
| `/api/services/service-requests/{id}/confirm-completion/` | POST | Admin | Verify completion |
| `/api/services/service-requests/{id}/submit-review/` | POST | Client | Rate serviceman |

---

## 🎯 Success Metrics

Track these metrics for workflow optimization:

- **Time from booking to assignment** (Target: < 2 hours)
- **Time from assignment to estimate** (Target: < 24 hours)
- **Time from price approval to payment** (Target: < 12 hours)
- **Time from payment to work start** (Target: < 4 hours)
- **Time from work start to completion** (Varies by job)
- **Client satisfaction ratings** (Target: > 4.5/5)
- **Serviceman response rate** (Target: > 95%)

---

## 🚨 Error Handling

### Common Scenarios:

1. **Client tries to pay before price is finalized**
   - Error: "Price not yet ready. Please wait for admin approval."
   - Status: Still in `ESTIMATION_SUBMITTED`

2. **Serviceman tries to submit estimate twice**
   - Error: "Estimate already submitted. Contact admin to update."
   - Status: `ESTIMATION_SUBMITTED`

3. **Admin tries to authorize work before payment**
   - Error: "Payment not yet received. Current status: {status}"
   - Status: Check current status

4. **Client tries to review before admin confirms**
   - Error: "Job not yet confirmed complete. Please wait."
   - Status: `COMPLETED` but not yet CLIENT_REVIEWED

---

## 📞 Support & Questions

For technical integration questions, contact the backend team.

For workflow clarification, refer to this document first.

**Last Updated**: November 2025  
**API Version**: 1.0  
**Backend**: Django Rest Framework

