# 🔧 QUICK FIX: Payment Initialization

**Issue:** Frontend getting 404 error when initializing payment

---

## ❌ What Frontend Was Sending (Wrong)

```javascript
POST /api/payments/initialize/

{
  "email": "shimanayagba@gmail.com",
  "service_request_id": 9  // ❌ Wrong parameter name
}
```

**Error:** `No ServiceRequest matches the given query`

---

## ✅ What Frontend Should Send (Correct)

**Option 1: Use `service_request` (recommended)**
```javascript
POST /api/payments/initialize/

{
  "service_request": 9,           // ✅ Correct parameter name
  "payment_type": "SERVICE_PAYMENT",  // ✅ Required
  "amount": 16500.00                  // ✅ Required
}
```

**Option 2: Use `service_request_id` (now also works)**
```javascript
POST /api/payments/initialize/

{
  "service_request_id": 9,        // ✅ Also works now (backward compatible)
  "payment_type": "SERVICE_PAYMENT",
  "amount": 16500.00
}
```

**Backend has been updated to accept BOTH parameter names!**

---

## 📋 Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `service_request` or `service_request_id` | integer | ✅ Yes | Service request ID |
| `payment_type` | string | ✅ Yes | Must be "SERVICE_PAYMENT" |
| `amount` | number | ✅ Yes | Final cost from service request |

---

## ⚠️ Common Mistakes

### ❌ WRONG: Missing payment_type
```javascript
{
  "service_request": 9,
  "amount": 16500
  // ❌ Missing payment_type
}
```

### ❌ WRONG: Sending email (not needed)
```javascript
{
  "service_request": 9,
  "payment_type": "SERVICE_PAYMENT",
  "amount": 16500,
  "email": "client@example.com"  // ❌ Not needed - backend gets from auth token
}
```

### ✅ CORRECT: All required fields
```javascript
{
  "service_request": 9,
  "payment_type": "SERVICE_PAYMENT",
  "amount": 16500.00
}
```

---

## 💻 Frontend Implementation

### Complete Working Example

```javascript
const initializePayment = async (requestId) => {
  const accessToken = localStorage.getItem('accessToken');
  
  // Step 1: Get service request to get final_cost
  const requestResponse = await fetch(
    `/api/services/service-requests/${requestId}/`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  
  const serviceRequest = await requestResponse.json();
  
  // Step 2: Verify status and final_cost exist
  if (serviceRequest.status !== 'AWAITING_CLIENT_APPROVAL') {
    alert('This request is not ready for payment');
    return;
  }
  
  if (!serviceRequest.final_cost) {
    alert('Price has not been finalized yet');
    return;
  }
  
  // Step 3: Initialize payment
  const paymentResponse = await fetch('/api/payments/initialize/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      service_request: parseInt(requestId),  // Can also use service_request_id
      payment_type: 'SERVICE_PAYMENT',       // Important!
      amount: parseFloat(serviceRequest.final_cost)
    })
  });

  const paymentData = await paymentResponse.json();

  if (paymentResponse.ok) {
    // Save reference for verification
    localStorage.setItem('pendingPaymentReference', paymentData.payment.paystack_reference);
    localStorage.setItem('pendingServiceRequestId', requestId);
    
    // Redirect to Paystack
    window.location.href = paymentData.paystack_url;
  } else {
    alert('Payment initialization failed: ' + (paymentData.error || 'Unknown error'));
  }
};

// Usage
await initializePayment(9);
```

---

## 📊 Expected Response

**Success (201 Created):**
```json
{
  "payment": {
    "id": 456,
    "service_request": 9,
    "payment_type": "SERVICE_PAYMENT",
    "amount": "16500.00",
    "paystack_reference": "9-SERVICE_PAYMENT-1730820000.123",
    "paystack_access_code": "abc123xyz",
    "status": "PENDING",
    "created_at": "2025-11-05T15:30:00Z"
  },
  "paystack_url": "https://checkout.paystack.com/abc123xyz"
}
```

**Error (400 Bad Request):**
```json
{
  "error": "service_request or service_request_id is required"
}
```

**Error (404 Not Found):**
```json
{
  "detail": "No ServiceRequest matches the given query."
}
```
*This means the service_request ID doesn't exist in database*

---

## 🔍 Debugging Steps

### 1. Verify Service Request Exists

```javascript
// Check if request exists
const response = await fetch(`/api/services/service-requests/9/`, {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});

if (response.status === 404) {
  console.error('❌ Service request #9 does not exist!');
} else if (response.ok) {
  const data = await response.json();
  console.log('✅ Service request exists');
  console.log('Status:', data.status);
  console.log('Final cost:', data.final_cost);
}
```

### 2. Check Request Body

```javascript
// Log what you're sending
const requestBody = {
  service_request: 9,  // or service_request_id: 9
  payment_type: 'SERVICE_PAYMENT',
  amount: 16500.00
};

console.log('Sending to payment API:', JSON.stringify(requestBody, null, 2));

const response = await fetch('/api/payments/initialize/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(requestBody)
});

console.log('Response status:', response.status);
console.log('Response data:', await response.json());
```

### 3. Check Response in Network Tab

Open browser DevTools → Network tab:
- Look for `initialize` request
- Check Request Payload
- Check Response

---

## ✅ Frontend Fix Options

### Option 1: Change Parameter Name (Recommended)

```javascript
// Change from:
{
  "service_request_id": 9  // ❌ Old way
}

// To:
{
  "service_request": 9     // ✅ Correct way
}
```

### Option 2: Use New Backward Compatible Backend (Already Done)

Backend now accepts BOTH:
- ✅ `service_request`
- ✅ `service_request_id`

So frontend can use either!

---

## 📝 Correct Request Format

```javascript
// Complete request with all required fields
POST https://serviceman-backend.onrender.com/api/payments/initialize/

Headers:
{
  "Authorization": "Bearer <access_token>",
  "Content-Type": "application/json"
}

Body:
{
  "service_request": 9,              // ✅ Use this (or service_request_id)
  "payment_type": "SERVICE_PAYMENT", // ✅ Required
  "amount": 16500.00                 // ✅ Required (from service_request.final_cost)
}

// ❌ DO NOT SEND:
// "email" - backend gets from authenticated user
```

---

## 🎯 Step-by-Step Fix

### Step 1: Update Frontend Code

**Change this:**
```javascript
const response = await fetch('/api/payments/initialize/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    email: user.email,          // ❌ Remove this
    service_request_id: 9       // ⚠️ Works now, but use service_request
  })
});
```

**To this:**
```javascript
const response = await fetch('/api/payments/initialize/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_request: 9,           // ✅ Correct parameter name
    payment_type: 'SERVICE_PAYMENT',  // ✅ Add this
    amount: 16500.00                  // ✅ Add this
  })
});
```

---

### Step 2: Get Amount from Service Request

```javascript
// Don't hardcode amount - get it from service request
const getPaymentAmount = async (requestId) => {
  const response = await fetch(`/api/services/service-requests/${requestId}/`, {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  
  const data = await response.json();
  return parseFloat(data.final_cost);
};

// Then use it
const amount = await getPaymentAmount(9);

await fetch('/api/payments/initialize/', {
  method: 'POST',
  body: JSON.stringify({
    service_request: 9,
    payment_type: 'SERVICE_PAYMENT',
    amount: amount  // ✅ Dynamic from service request
  })
});
```

---

## 🚀 Complete Working Code

```javascript
// Complete payment initialization with all checks
const initializeServicePayment = async (serviceRequestId) => {
  const accessToken = localStorage.getItem('accessToken');
  
  try {
    // Step 1: Fetch service request
    const requestResponse = await fetch(
      `/api/services/service-requests/${serviceRequestId}/`,
      {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      }
    );

    if (!requestResponse.ok) {
      if (requestResponse.status === 404) {
        throw new Error(`Service request #${serviceRequestId} not found`);
      }
      throw new Error('Failed to fetch service request');
    }

    const serviceRequest = await requestResponse.json();

    // Step 2: Validate status
    if (serviceRequest.status !== 'AWAITING_CLIENT_APPROVAL') {
      throw new Error(`Cannot pay. Current status: ${serviceRequest.status}`);
    }

    // Step 3: Validate final_cost exists
    if (!serviceRequest.final_cost) {
      throw new Error('Price has not been finalized yet');
    }

    // Step 4: Initialize payment
    const paymentResponse = await fetch('/api/payments/initialize/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        service_request: parseInt(serviceRequestId),  // ✅ or service_request_id
        payment_type: 'SERVICE_PAYMENT',              // ✅ Required
        amount: parseFloat(serviceRequest.final_cost) // ✅ Required
      })
    });

    if (!paymentResponse.ok) {
      const errorData = await paymentResponse.json();
      throw new Error(errorData.error || errorData.detail || 'Payment initialization failed');
    }

    const paymentData = await paymentResponse.json();

    // Step 5: Save reference and redirect
    localStorage.setItem('pendingPaymentReference', paymentData.payment.paystack_reference);
    localStorage.setItem('pendingServiceRequestId', serviceRequestId);

    console.log('✅ Payment initialized successfully');
    console.log('Reference:', paymentData.payment.paystack_reference);
    console.log('Redirecting to Paystack...');

    // Redirect to Paystack
    window.location.href = paymentData.paystack_url;

  } catch (error) {
    console.error('❌ Payment initialization error:', error);
    alert(`Payment initialization failed: ${error.message}`);
  }
};

// Usage
await initializeServicePayment(9);
```

---

## 📱 React Component

```jsx
// PaymentButton.jsx
import { useState } from 'react';

function PaymentButton({ serviceRequest }) {
  const [loading, setLoading] = useState(false);

  const handlePay = async () => {
    if (serviceRequest.status !== 'AWAITING_CLIENT_APPROVAL') {
      alert('This request is not ready for payment');
      return;
    }

    setLoading(true);

    try {
      const accessToken = localStorage.getItem('accessToken');
      
      const response = await fetch('/api/payments/initialize/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          service_request: serviceRequest.id,
          payment_type: 'SERVICE_PAYMENT',
          amount: parseFloat(serviceRequest.final_cost)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Payment failed');
      }

      const data = await response.json();

      // Save and redirect
      localStorage.setItem('pendingPaymentReference', data.payment.paystack_reference);
      localStorage.setItem('pendingServiceRequestId', serviceRequest.id);
      
      window.location.href = data.paystack_url;

    } catch (error) {
      alert(`Error: ${error.message}`);
      setLoading(false);
    }
  };

  return (
    <button 
      onClick={handlePay}
      disabled={loading || serviceRequest.status !== 'AWAITING_CLIENT_APPROVAL'}
      className="btn-pay"
    >
      {loading ? 'Processing...' : `Pay ₦${parseFloat(serviceRequest.final_cost).toLocaleString()}`}
    </button>
  );
}

export default PaymentButton;
```

---

## 🎯 Summary

**What to Change:**

1. **Add `payment_type` field:**
   ```javascript
   payment_type: 'SERVICE_PAYMENT'  // MUST include
   ```

2. **Add `amount` field:**
   ```javascript
   amount: parseFloat(serviceRequest.final_cost)  // MUST include
   ```

3. **Fix parameter name (optional - both work now):**
   ```javascript
   service_request: 9  // Recommended
   // or
   service_request_id: 9  // Also works
   ```

4. **Remove `email` field:**
   ```javascript
   // ❌ Don't send - backend gets from auth token
   email: "user@example.com"
   ```

---

## ✅ Correct Request

**Copy this exact format:**

```javascript
const accessToken = localStorage.getItem('accessToken');

const response = await fetch('https://serviceman-backend.onrender.com/api/payments/initialize/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    service_request: 9,
    payment_type: 'SERVICE_PAYMENT',
    amount: 16500.00
  })
});

const data = await response.json();

if (response.ok) {
  console.log('✅ Success!');
  console.log('Paystack URL:', data.paystack_url);
  window.location.href = data.paystack_url;
} else {
  console.error('❌ Error:', data.error);
}
```

---

## 🧪 Test It

**Before testing, make sure:**
- ✅ Service request #9 exists
- ✅ Status is `AWAITING_CLIENT_APPROVAL`
- ✅ `final_cost` is not null
- ✅ You're authenticated as the client (request owner)

**Then send:**
```json
{
  "service_request": 9,
  "payment_type": "SERVICE_PAYMENT",
  "amount": 16500.00
}
```

**Expected:**
- ✅ 201 Created
- ✅ Returns payment object
- ✅ Returns paystack_url
- ✅ Can redirect to Paystack

---

**Backend Updated:** ✅ Now accepts both `service_request` and `service_request_id`  
**Frontend Action:** Update request body to include all 3 required fields  
**Status:** Ready to test!

