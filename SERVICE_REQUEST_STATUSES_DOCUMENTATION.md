# Service Request Status Flow - Frontend Integration Guide

## 📋 Overview

This document provides comprehensive information about the service request status flow for frontend developers integrating with the ServiceMan backend API.

---

## 🎯 Service Request Statuses

The service request lifecycle follows a specific status progression. Below is the complete list of statuses with their descriptions and usage:

### **TypeScript Enum Definition**

```typescript
export enum ServiceRequestStatus {
  // --- Initial State ---
  PENDING_ADMIN_ASSIGNMENT = "PENDING_ADMIN_ASSIGNMENT",  // Initial state after client booking & booking fee payment. Waiting for admin to assign a serviceman.

  // --- Estimation Phase ---
  PENDING_ESTIMATION = "PENDING_ESTIMATION",  // Admin has assigned serviceman. Serviceman needs to visit site and provide raw estimate.
  ESTIMATION_SUBMITTED = "ESTIMATION_SUBMITTED",  // Serviceman has submitted raw estimate. Waiting for admin to add platform fee.

  // --- Client Approval & Payment Phase ---
  AWAITING_CLIENT_APPROVAL = "AWAITING_CLIENT_APPROVAL",  // Admin has added platform fee and sent final price to client. Waiting for client to approve and pay.
  PAYMENT_COMPLETED = "PAYMENT_COMPLETED",  // Client has successfully paid the full amount. Job is now officially active.

  // --- Execution Phase ---
  IN_PROGRESS = "IN_PROGRESS",  // Serviceman has started the work. Job appears on both client and serviceman dashboards.
  COMPLETED = "COMPLETED",  // Serviceman has marked the job as finished.

  // --- Final State ---
  CLIENT_REVIEWED = "CLIENT_REVIEWED",  // Client has left a rating and review for the serviceman.

  // --- Cancellation State ---
  CANCELLED = "CANCELLED",  // Job was cancelled by admin, client, or serviceman before completion.

  // --- Legacy Statuses (Deprecated but still in database) ---
  ASSIGNED_TO_SERVICEMAN = "ASSIGNED_TO_SERVICEMAN",
  SERVICEMAN_INSPECTED = "SERVICEMAN_INSPECTED",
  NEGOTIATING = "NEGOTIATING",
  AWAITING_PAYMENT = "AWAITING_PAYMENT",
  PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED",
}
```

---

## 🔄 Complete Status Flow

### **Visual Flow Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PENDING_ADMIN_ASSIGNMENT                                │
│    Client creates service request and pays booking fee      │
│    ↓                                                         │
│ 2. PENDING_ESTIMATION                                       │
│    Admin assigns serviceman                                 │
│    ↓                                                         │
│ 3. ESTIMATION_SUBMITTED                                     │
│    Serviceman submits raw estimate                          │
│    ↓                                                         │
│ 4. AWAITING_CLIENT_APPROVAL                                │
│    Admin adds platform fee, final price sent to client      │
│    ↓                                                         │
│ 5. PAYMENT_COMPLETED                                        │
│    Client pays full amount                                  │
│    ↓                                                         │
│ 6. IN_PROGRESS                                              │
│    Serviceman starts work                                   │
│    ↓                                                         │
│ 7. COMPLETED                                                 │
│    Serviceman marks job as finished                         │
│    ↓                                                         │
│ 8. CLIENT_REVIEWED                                          │
│    Client leaves review and rating                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│    CANCELLED (Can occur at any point before COMPLETED)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Status Details

### **1. PENDING_ADMIN_ASSIGNMENT** 🔴
**Description:** Initial state after client booking and booking fee payment.  
**Who's waiting:** Admin to assign a serviceman  
**UI Display:** "Waiting for admin to assign serviceman"  
**User Action Required:** None (auto-transitions when admin assigns)  
**Can Cancel:** Yes (client)

```typescript
const statusConfig = {
  label: "Waiting for Assignment",
  icon: "ClockIcon",
  color: "yellow",
  message: "Waiting for admin to assign a serviceman",
  canCancel: true,
  showProgress: true,
};
```

---

### **2. PENDING_ESTIMATION** 🔵
**Description:** Admin has assigned serviceman. Serviceman needs to visit site and provide raw estimate.  
**Who's waiting:** Serviceman to provide estimation  
**UI Display:** "Waiting for serviceman's estimate"  
**User Action Required:** Serviceman must submit estimate  
**Can Cancel:** Yes (client)

```typescript
const statusConfig = {
  label: "Pending Estimation",
  icon: "CalculatorIcon",
  color: "blue",
  message: "Serviceman is preparing your estimate",
  canCancel: true,
  showProgress: true,
};
```

---

### **3. ESTIMATION_SUBMITTED** 🟡
**Description:** Serviceman has submitted raw estimate. Waiting for admin to add platform fee.  
**Who's waiting:** Admin to add platform fee  
**UI Display:** "Estimate submitted, calculating final price"  
**User Action Required:** None  
**Can Cancel:** Yes (client)

```typescript
const statusConfig = {
  label: "Processing Estimate",
  icon: "DocumentCheckIcon",
  color: "orange",
  message: "Admin is adding platform fees",
  canCancel: true,
  showProgress: true,
};
```

---

### **4. AWAITING_CLIENT_APPROVAL** 🟠
**Description:** Admin has added platform fee and sent final price to client. Waiting for client to approve and pay.  
**Who's waiting:** Client to approve and pay  
**UI Display:** "Pending your approval"  
**User Action Required:** Client must approve and pay  
**Can Cancel:** Yes (client)

```typescript
const statusConfig = {
  label: "Awaiting Your Approval",
  icon: "CreditCardIcon",
  color: "amber",
  message: "Please review and pay the final amount",
  canCancel: true,
  showProgress: true,
  paymentRequired: true,
  amount: request.final_cost,
};
```

---

### **5. PAYMENT_COMPLETED** 🟢
**Description:** Client has successfully paid the full amount. Job is now officially active.  
**Who's waiting:** Serviceman to start work  
**UI Display:** "Payment received, waiting to begin"  
**User Action Required:** None (auto-transitions when serviceman starts)  
**Can Cancel:** With admin approval only

```typescript
const statusConfig = {
  label: "Ready to Start",
  icon: "CheckCircleIcon",
  color: "green",
  message: "Payment received. Serviceman will begin work soon",
  canCancel: false,
  showProgress: true,
};
```

---

### **6. IN_PROGRESS** 🔵
**Description:** Serviceman has started the work. Job appears on both client and serviceman dashboards.  
**Who's waiting:** Serviceman to complete work  
**UI Display:** "Work in progress"  
**User Action Required:** Serviceman must complete work  
**Can Cancel:** No (work has started)

```typescript
const statusConfig = {
  label: "Work in Progress",
  icon: "WrenchScrewdriverIcon",
  color: "indigo",
  message: "Service is currently being performed",
  canCancel: false,
  showProgress: true,
  showActiveJob: true,
};
```

---

### **7. COMPLETED** 🟢
**Description:** Serviceman has marked the job as finished.  
**Who's waiting:** Client to review  
**UI Display:** "Service completed"  
**User Action Required:** Client must leave review  
**Can Cancel:** No (job complete)

```typescript
const statusConfig = {
  label: "Service Completed",
  icon: "CheckBadgeIcon",
  color: "green",
  message: "Please rate your experience",
  canCancel: false,
  showProgress: true,
  reviewRequired: true,
};
```

---

### **8. CLIENT_REVIEWED** ✅
**Description:** Client has left a rating and review for the serviceman.  
**Who's waiting:** No one (final state)  
**UI Display:** "Thank you for your feedback"  
**User Action Required:** None  
**Can Cancel:** No (final state)

```typescript
const statusConfig = {
  label: "All Done!",
  icon: "SparklesIcon",
  color: "purple",
  message: "Thank you for using ServiceMan",
  canCancel: false,
  showProgress: false,
  isFinal: true,
};
```

---

### **9. CANCELLED** ❌
**Description:** Job was cancelled by admin, client, or serviceman before completion.  
**Who's waiting:** No one  
**UI Display:** "Cancelled"  
**User Action Required:** None  
**Can Cancel:** No (already cancelled)

```typescript
const statusConfig = {
  label: "Cancelled",
  icon: "XCircleIcon",
  color: "gray",
  message: "This request was cancelled",
  canCancel: false,
  showProgress: false,
};
```

---

## 🎨 Frontend Implementation

### **Status Helper Functions**

```typescript
// Get status configuration
const getStatusConfig = (status: ServiceRequestStatus) => {
  const configs = {
    [ServiceRequestStatus.PENDING_ADMIN_ASSIGNMENT]: {
      label: "Waiting for Assignment",
      icon: "ClockIcon",
      color: "yellow",
      badge: "Waiting",
      description: "Waiting for admin to assign a serviceman",
      canCancel: true,
      isActionRequired: false,
      nextStatus: ServiceRequestStatus.PENDING_ESTIMATION,
    },
    [ServiceRequestStatus.PENDING_ESTIMATION]: {
      label: "Pending Estimation",
      icon: "CalculatorIcon",
      color: "blue",
      badge: "Estimating",
      description: "Serviceman is preparing your estimate",
      canCancel: true,
      isActionRequired: false, // Serviceman's action
      nextStatus: ServiceRequestStatus.ESTIMATION_SUBMITTED,
    },
    [ServiceRequestStatus.ESTIMATION_SUBMITTED]: {
      label: "Processing Estimate",
      icon: "DocumentCheckIcon",
      color: "orange",
      badge: "Processing",
      description: "Admin is adding platform fees",
      canCancel: true,
      isActionRequired: false,
      nextStatus: ServiceRequestStatus.AWAITING_CLIENT_APPROVAL,
    },
    [ServiceRequestStatus.AWAITING_CLIENT_APPROVAL]: {
      label: "Awaiting Your Approval",
      icon: "CreditCardIcon",
      color: "amber",
      badge: "Action Required",
      description: "Please review and pay the final amount",
      canCancel: true,
      isActionRequired: true,
      requiresPayment: true,
      nextStatus: ServiceRequestStatus.PAYMENT_COMPLETED,
    },
    [ServiceRequestStatus.PAYMENT_COMPLETED]: {
      label: "Ready to Start",
      icon: "CheckCircleIcon",
      color: "green",
      badge: "Ready",
      description: "Payment received. Serviceman will begin work soon",
      canCancel: false,
      isActionRequired: false,
      nextStatus: ServiceRequestStatus.IN_PROGRESS,
    },
    [ServiceRequestStatus.IN_PROGRESS]: {
      label: "Work in Progress",
      icon: "WrenchScrewdriverIcon",
      color: "indigo",
      badge: "Active",
      description: "Service is currently being performed",
      canCancel: false,
      isActionRequired: false,
      nextStatus: ServiceRequestStatus.COMPLETED,
    },
    [ServiceRequestStatus.COMPLETED]: {
      label: "Service Completed",
      icon: "CheckBadgeIcon",
      color: "green",
      badge: "Done",
      description: "Please rate your experience",
      canCancel: false,
      isActionRequired: true, // Review required
      requiresReview: true,
      nextStatus: ServiceRequestStatus.CLIENT_REVIEWED,
    },
    [ServiceRequestStatus.CLIENT_REVIEWED]: {
      label: "All Done!",
      icon: "SparklesIcon",
      color: "purple",
      badge: "Completed",
      description: "Thank you for using ServiceMan",
      canCancel: false,
      isActionRequired: false,
      isFinal: true,
    },
    [ServiceRequestStatus.CANCELLED]: {
      label: "Cancelled",
      icon: "XCircleIcon",
      color: "gray",
      badge: "Cancelled",
      description: "This request was cancelled",
      canCancel: false,
      isActionRequired: false,
    },
  };
  
  return configs[status] || configs[ServiceRequestStatus.CANCELLED];
};

// Check if status allows cancellation
const canCancelRequest = (status: ServiceRequestStatus): boolean => {
  const cannotCancel = [
    ServiceRequestStatus.IN_PROGRESS,
    ServiceRequestStatus.COMPLETED,
    ServiceRequestStatus.CLIENT_REVIEWED,
    ServiceRequestStatus.CANCELLED,
    ServiceRequestStatus.PAYMENT_COMPLETED,
  ];
  return !cannotCancel.includes(status);
};

// Check if user action is required
const requiresUserAction = (
  status: ServiceRequestStatus, 
  userRole: 'CLIENT' | 'SERVICEMAN' | 'ADMIN'
): boolean => {
  const actionRequiredMap = {
    [ServiceRequestStatus.AWAITING_CLIENT_APPROVAL]: userRole === 'CLIENT',
    [ServiceRequestStatus.COMPLETED]: userRole === 'CLIENT',
    [ServiceRequestStatus.PENDING_ESTIMATION]: userRole === 'SERVICEMAN',
    [ServiceRequestStatus.PENDING_ADMIN_ASSIGNMENT]: userRole === 'ADMIN',
  };
  
  return actionRequiredMap[status] || false;
};

// Get next possible statuses (for admin/client transitions)
const getNextStatuses = (currentStatus: ServiceRequestStatus): ServiceRequestStatus[] => {
  const nextMap = {
    [ServiceRequestStatus.PENDING_ADMIN_ASSIGNMENT]: [
      ServiceRequestStatus.PENDING_ESTIMATION,
      ServiceRequestStatus.CANCELLED,
    ],
    [ServiceRequestStatus.PENDING_ESTIMATION]: [
      ServiceRequestStatus.ESTIMATION_SUBMITTED,
      ServiceRequestStatus.CANCELLED,
    ],
    [ServiceRequestStatus.ESTIMATION_SUBMITTED]: [
      ServiceRequestStatus.AWAITING_CLIENT_APPROVAL,
      ServiceRequestStatus.CANCELLED,
    ],
    [ServiceRequestStatus.AWAITING_CLIENT_APPROVAL]: [
      ServiceRequestStatus.PAYMENT_COMPLETED,
      ServiceRequestStatus.CANCELLED,
    ],
    [ServiceRequestStatus.PAYMENT_COMPLETED]: [
      ServiceRequestStatus.IN_PROGRESS,
    ],
    [ServiceRequestStatus.IN_PROGRESS]: [
      ServiceRequestStatus.COMPLETED,
    ],
    [ServiceRequestStatus.COMPLETED]: [
      ServiceRequestStatus.CLIENT_REVIEWED,
    ],
    [ServiceRequestStatus.CLIENT_REVIEWED]: [], // Final state
    [ServiceRequestStatus.CANCELLED]: [], // Final state
  };
  
  return nextMap[currentStatus] || [];
};
```

---

## 🔌 API Endpoints

### **GET /api/services/service-requests/**
**Description:** List all service requests for the authenticated user  
**Response:** Array of service requests with status field  
**Example Response:**
```json
[
  {
    "id": 1,
    "status": "PENDING_ADMIN_ASSIGNMENT",
    "booking_date": "2025-10-22",
    "is_emergency": false,
    "initial_booking_fee": "2000.00",
    "client_address": "123 Main St",
    "service_description": "Fix leaking pipe",
    "created_at": "2025-10-22T10:00:00Z",
    "updated_at": "2025-10-22T10:00:00Z",
    "client": {...},
    "serviceman": null,
    "category": {...}
  }
]
```

---

### **GET /api/services/service-requests/{id}/**
**Description:** Get single service request details  
**Response:** Single service request object with status field

---

### **PATCH /api/services/service-requests/{id}/**
**Description:** Update service request (admin/client/serviceman)  
**Request Body:**
```json
{
  "status": "IN_PROGRESS"
}
```
**Note:** Status transitions are validated by backend permissions

---

### **POST /api/services/service-requests/{id}/assign/**
**Description:** Admin assigns serviceman to request (changes status to PENDING_ESTIMATION)  
**Request Body:**
```json
{
  "serviceman_id": 5
}
```

---

## 🎯 User Role Actions

### **Client Actions**
- **View all requests** (GET /api/services/service-requests/)
- **Create request** (POST /api/services/service-requests/)
- **Approve estimate & pay** (PATCH status → AWAITING_CLIENT_APPROVAL → PAYMENT_COMPLETED)
- **Leave review** (PATCH status → CLIENT_REVIEWED)
- **Cancel request** (PATCH status → CANCELLED) before IN_PROGRESS

### **Serviceman Actions**
- **Submit estimation** (POST /api/services/submit-estimation/) → ESTIMATION_SUBMITTED
- **Start work** (PATCH status → IN_PROGRESS)
- **Complete work** (PATCH status → COMPLETED)

### **Admin Actions**
- **Assign serviceman** (POST /api/services/service-requests/{id}/assign/)
- **Add platform fee** (PATCH final_cost) → AWAITING_CLIENT_APPROVAL
- **Cancel any request** (PATCH status → CANCELLED)

---

## 📝 Status Transitions

### **Automatic Transitions**
```typescript
// When admin assigns serviceman
status: PENDING_ADMIN_ASSIGNMENT → PENDING_ESTIMATION

// When serviceman submits estimation
status: PENDING_ESTIMATION → ESTIMATION_SUBMITTED

// When admin adds platform fee
status: ESTIMATION_SUBMITTED → AWAITING_CLIENT_APPROVAL

// When client pays
status: AWAITING_CLIENT_APPROVAL → PAYMENT_COMPLETED

// When serviceman starts work
status: PAYMENT_COMPLETED → IN_PROGRESS

// When serviceman finishes
status: IN_PROGRESS → COMPLETED

// When client reviews
status: COMPLETED → CLIENT_REVIEWED
```

### **Manual Transitions**
```typescript
// Cancellation (any point before IN_PROGRESS)
status: * → CANCELLED
```

---

## 🎨 UI/UX Recommendations

### **Status Badge Colors**
```typescript
const statusColors = {
  PENDING_ADMIN_ASSIGNMENT: "bg-yellow-100 text-yellow-800",
  PENDING_ESTIMATION: "bg-blue-100 text-blue-800",
  ESTIMATION_SUBMITTED: "bg-orange-100 text-orange-800",
  AWAITING_CLIENT_APPROVAL: "bg-amber-100 text-amber-800",
  PAYMENT_COMPLETED: "bg-green-100 text-green-800",
  IN_PROGRESS: "bg-indigo-100 text-indigo-800",
  COMPLETED: "bg-green-100 text-green-800",
  CLIENT_REVIEWED: "bg-purple-100 text-purple-800",
  CANCELLED: "bg-gray-100 text-gray-800",
};
```

### **Progress Indicators**
Show progress bars indicating:
- **0%** - PENDING_ADMIN_ASSIGNMENT
- **12%** - PENDING_ESTIMATION
- **25%** - ESTIMATION_SUBMITTED
- **37%** - AWAITING_CLIENT_APPROVAL
- **50%** - PAYMENT_COMPLETED
- **62%** - IN_PROGRESS
- **75%** - COMPLETED
- **100%** - CLIENT_REVIEWED

### **Action Buttons**
Display appropriate action buttons based on status and user role:
- **"Cancel Request"** - When `canCancel: true`
- **"Pay Now"** - When `requiresPayment: true`
- **"Start Work"** - When status is PAYMENT_COMPLETED (serviceman)
- **"Complete Job"** - When status is IN_PROGRESS (serviceman)
- **"Leave Review"** - When `requiresReview: true`

---

## 🐛 Troubleshooting

### **Common Issues**

1. **Status not updating after payment**
   - Check payment verification webhook
   - Ensure payment status is SUCCESSFUL

2. **Cannot cancel in IN_PROGRESS**
   - This is expected behavior (work has started)
   - Contact admin for cancellation

3. **Status stuck in ESTIMATION_SUBMITTED**
   - Admin needs to add platform fee
   - Check admin dashboard

---

## 📚 Additional Resources

- **API Documentation:** `/api/docs/`
- **Service Request Endpoints:** See `USER_SPECIFIC_ENDPOINTS_DOCUMENTATION.md`
- **Payment Integration:** See `BOOKING_FEE_PAYMENT_GUIDE.md`

---

**🎉 Ready to integrate!** This comprehensive guide covers all aspects of the service request status flow for frontend development.

