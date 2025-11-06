# 💳 Client: How to Pay Final Amount After Price Approval

**Complete guide for clients to pay the final service cost after admin sets the price**

---

## 📋 Overview

After the serviceman submits an estimate and admin adds the platform fee, the client must:
1. Review the final price
2. Approve the price
3. Pay via Paystack
4. Verify payment
5. Work begins!

---

## 🔄 The Payment Workflow

```
STEP 3: Serviceman submits estimate (₦15,000)
   Status: ESTIMATION_SUBMITTED
   ↓
STEP 4: Admin adds platform fee (10% = ₦1,500)
   Final Cost: ₦16,500
   Status: AWAITING_CLIENT_APPROVAL
   ↓
STEP 5: Client pays final amount (THIS GUIDE)
   Status: PAYMENT_COMPLETED
   ↓
STEP 6: Admin authorizes work to begin
   Status: IN_PROGRESS
```

---

## 📧 Client Receives Notification

After admin finalizes price, client receives:

```
📧 Notification: "Price Ready for Your Approval - Request #9"

Your service request has been priced:

• Service Cost: ₦15,000.00
• Platform Fee (10%): ₦1,500.00
• Total Amount: ₦16,500.00

Please review and proceed with payment to confirm the job.
```

---

## 📡 Step 1: View Final Price

**Endpoint:** `GET /api/services/service-requests/<id>/`

```javascript
// Client views their service request to see final price
const viewServiceRequest = async (requestId) => {
  const accessToken = localStorage.getItem('accessToken');
  
  const response = await fetch(
    `/api/services/service-requests/${requestId}/`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );

  const serviceRequest = await response.json();
  
  console.log('Status:', serviceRequest.status);
  console.log('Serviceman Estimate:', serviceRequest.serviceman_estimated_cost);
  console.log('Platform Fee %:', serviceRequest.admin_markup_percentage);
  console.log('Final Cost:', serviceRequest.final_cost);
  
  return serviceRequest;
};
```

**Response:**
```json
{
  "id": 9,
  "status": "AWAITING_CLIENT_APPROVAL",
  "serviceman_estimated_cost": "15000.00",
  "admin_markup_percentage": "10.00",
  "final_cost": "16500.00",
  "initial_booking_fee": "2000.00",
  "client": {...},
  "serviceman": {
    "id": 22,
    "user": {
      "full_name": "John Plumber"
    },
    "rating": "4.70"
  },
  "category": {
    "id": 1,
    "name": "Plumbing"
  },
  "booking_date": "2025-11-15",
  "client_address": "123 Main St, Lagos",
  "service_description": "Fix leaking pipe"
}
```

---

## 💰 Step 2: Initialize Payment for Final Amount

**Endpoint:** `POST /api/payments/initialize/`

```javascript
// Initialize payment for the final service cost
const initializeFinalPayment = async (serviceRequestId) => {
  const accessToken = localStorage.getItem('accessToken');
  
  // First, get the service request to get final_cost
  const requestResponse = await fetch(
    `/api/services/service-requests/${serviceRequestId}/`,
    { headers: { 'Authorization': `Bearer ${accessToken}` } }
  );
  const serviceRequest = await requestResponse.json();
  
  // Verify status
  if (serviceRequest.status !== 'AWAITING_CLIENT_APPROVAL') {
    alert('This request is not ready for payment');
    return;
  }
  
  // Initialize payment
  const response = await fetch('/api/payments/initialize/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      service_request: serviceRequestId,  // or service_request_id (both work)
      payment_type: 'SERVICE_PAYMENT',    // Required: This is the final payment
      amount: parseFloat(serviceRequest.final_cost)  // Required: Final cost
    })
  });

  const data = await response.json();
  
  if (response.ok) {
    console.log('Payment initialized:', data);
    console.log('Paystack URL:', data.authorization_url);
    console.log('Reference:', data.reference);
    
    // Save reference for verification later
    localStorage.setItem('pendingPaymentReference', data.reference);
    localStorage.setItem('pendingServiceRequestId', serviceRequestId);
    
    // Redirect to Paystack
    window.location.href = data.authorization_url;
  } else {
    alert('Failed to initialize payment: ' + (data.error || 'Unknown error'));
  }
};

// Usage
await initializeFinalPayment(9);
```

**Request Body:**
```json
{
  "service_request": 9,
  "payment_type": "SERVICE_PAYMENT",
  "amount": 16500.00
}
```

**Response (201 Created):**
```json
{
  "id": 456,
  "service_request": 9,
  "payment_type": "SERVICE_PAYMENT",
  "amount": "16500.00",
  "paystack_reference": "9-SERVICE_PAYMENT-1730820000.123",
  "paystack_access_code": "abc123xyz",
  "authorization_url": "https://checkout.paystack.com/abc123xyz",
  "status": "PENDING",
  "created_at": "2025-11-05T15:30:00Z"
}
```

---

## ✅ Step 3: Verify Payment

**Endpoint:** `GET /api/payments/verify/?reference=<reference>`

**After Paystack redirects back:**

```javascript
// PaymentCallbackPage.jsx
import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

function PaymentCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying');
  const [message, setMessage] = useState('');

  useEffect(() => {
    verifyPayment();
  }, []);

  const verifyPayment = async () => {
    // Get reference from URL or localStorage
    const reference = searchParams.get('reference') || 
                     localStorage.getItem('pendingPaymentReference');
    
    if (!reference) {
      setStatus('error');
      setMessage('No payment reference found');
      return;
    }

    try {
      const accessToken = localStorage.getItem('accessToken');
      
      const response = await fetch(
        `/api/payments/verify/?reference=${reference}`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        }
      );

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        setStatus('success');
        setMessage('Payment successful!');
        
        // Clear localStorage
        localStorage.removeItem('pendingPaymentReference');
        localStorage.removeItem('pendingServiceRequestId');
        
        // Wait 2 seconds then redirect
        setTimeout(() => {
          const requestId = data.service_request_id || 
                          localStorage.getItem('pendingServiceRequestId');
          navigate(`/my-requests/${requestId}`);
        }, 2000);
        
      } else {
        setStatus('error');
        setMessage(data.message || 'Payment verification failed');
      }
    } catch (error) {
      console.error('Verification error:', error);
      setStatus('error');
      setMessage('Network error during verification');
    }
  };

  return (
    <div className="payment-callback-page">
      {status === 'verifying' && (
        <div className="verifying">
          <div className="spinner"></div>
          <h2>Verifying Your Payment...</h2>
          <p>Please wait while we confirm your payment with Paystack.</p>
        </div>
      )}

      {status === 'success' && (
        <div className="success">
          <div className="success-icon">✅</div>
          <h2>Payment Successful!</h2>
          <p>{message}</p>
          <p>Your service request is now being processed.</p>
          <p>Redirecting to request details...</p>
        </div>
      )}

      {status === 'error' && (
        <div className="error">
          <div className="error-icon">❌</div>
          <h2>Payment Failed</h2>
          <p>{message}</p>
          <button onClick={() => navigate('/my-requests')}>
            Go to My Requests
          </button>
        </div>
      )}
    </div>
  );
}

export default PaymentCallbackPage;
```

**Verify Response (Success):**
```json
{
  "status": "success",
  "message": "Payment verified successfully",
  "amount": 16500.00,
  "reference": "9-SERVICE_PAYMENT-1730820000.123",
  "paid_at": "2025-11-05T15:35:00Z",
  "service_request_id": 9
}
```

---

## 🎨 Complete Payment Flow Component

```jsx
// ClientPaymentPage.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function ClientPaymentPage() {
  const { requestId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [serviceRequest, setServiceRequest] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchServiceRequest();
  }, [requestId]);

  const fetchServiceRequest = async () => {
    const accessToken = localStorage.getItem('accessToken');
    
    try {
      const response = await fetch(
        `/api/services/service-requests/${requestId}/`,
        { headers: { 'Authorization': `Bearer ${accessToken}` } }
      );

      if (response.ok) {
        const data = await response.json();
        setServiceRequest(data);
        
        // Verify can pay
        if (data.status !== 'AWAITING_CLIENT_APPROVAL') {
          setError(`Cannot pay. Current status: ${data.status}`);
        }
      }
    } catch (err) {
      setError('Failed to load service request');
    }
  };

  const handlePayment = async () => {
    setLoading(true);
    setError('');

    try {
      const accessToken = localStorage.getItem('accessToken');
      
      // Initialize payment
      const response = await fetch('/api/payments/initialize/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          service_request: parseInt(requestId),
          payment_type: 'SERVICE_PAYMENT',
          amount: parseFloat(serviceRequest.final_cost)
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Save for callback verification
        localStorage.setItem('pendingPaymentReference', data.paystack_reference);
        localStorage.setItem('pendingServiceRequestId', requestId);
        
        // Redirect to Paystack
        window.location.href = data.authorization_url;
      } else {
        setError(data.error || 'Failed to initialize payment');
        setLoading(false);
      }
    } catch (err) {
      console.error('Payment error:', err);
      setError('Network error. Please try again.');
      setLoading(false);
    }
  };

  if (!serviceRequest) {
    return <div>Loading...</div>;
  }

  if (serviceRequest.status !== 'AWAITING_CLIENT_APPROVAL') {
    return (
      <div className="payment-page">
        <div className="info-message">
          <h3>Payment Not Required</h3>
          <p>Current Status: {serviceRequest.status}</p>
          <button onClick={() => navigate(`/my-requests/${requestId}`)}>
            View Request Details
          </button>
        </div>
      </div>
    );
  }

  const baseCost = parseFloat(serviceRequest.serviceman_estimated_cost);
  const platformFee = baseCost * (parseFloat(serviceRequest.admin_markup_percentage) / 100);
  const totalCost = parseFloat(serviceRequest.final_cost);
  const bookingFee = parseFloat(serviceRequest.initial_booking_fee);

  return (
    <div className="client-payment-page">
      <h2>Payment Required - Request #{requestId}</h2>

      {error && (
        <div className="error-message">{error}</div>
      )}

      {/* Service Details */}
      <div className="service-summary">
        <h3>Service Summary</h3>
        <div className="summary-row">
          <span>Category:</span>
          <strong>{serviceRequest.category.name}</strong>
        </div>
        <div className="summary-row">
          <span>Serviceman:</span>
          <strong>{serviceRequest.serviceman?.user?.full_name || 'Assigned'}</strong>
        </div>
        <div className="summary-row">
          <span>Date:</span>
          <strong>{serviceRequest.booking_date}</strong>
        </div>
        <div className="summary-row">
          <span>Address:</span>
          <strong>{serviceRequest.client_address}</strong>
        </div>
      </div>

      {/* Price Breakdown */}
      <div className="price-breakdown">
        <h3>💰 Price Breakdown</h3>
        
        <div className="breakdown-row">
          <span className="label">Service Cost:</span>
          <span className="amount">₦{baseCost.toLocaleString('en-NG', {minimumFractionDigits: 2})}</span>
        </div>
        
        <div className="breakdown-row">
          <span className="label">
            Platform Fee ({serviceRequest.admin_markup_percentage}%):
          </span>
          <span className="amount">₦{platformFee.toLocaleString('en-NG', {minimumFractionDigits: 2})}</span>
        </div>
        
        <div className="breakdown-divider"></div>
        
        <div className="breakdown-row total">
          <span className="label"><strong>Total to Pay:</strong></span>
          <span className="amount total-amount">
            ₦{totalCost.toLocaleString('en-NG', {minimumFractionDigits: 2})}
          </span>
        </div>

        <div className="breakdown-row paid">
          <span className="label">Already Paid (Booking Fee):</span>
          <span className="amount paid-amount">
            -₦{bookingFee.toLocaleString('en-NG', {minimumFractionDigits: 2})}
          </span>
        </div>
        
        <div className="breakdown-divider"></div>
        
        <div className="breakdown-row final">
          <span className="label"><strong>Amount Due Now:</strong></span>
          <span className="amount final-amount">
            ₦{totalCost.toLocaleString('en-NG', {minimumFractionDigits: 2})}
          </span>
        </div>
      </div>

      {/* What's Included */}
      <div className="whats-included">
        <h3>📋 What's Included</h3>
        <p>{serviceRequest.service_description}</p>
        
        {serviceRequest.serviceman_notes && (
          <div className="serviceman-notes">
            <h4>Serviceman's Notes:</h4>
            <p>{serviceRequest.serviceman_notes}</p>
          </div>
        )}
      </div>

      {/* Payment Button */}
      <div className="payment-actions">
        <button
          onClick={handlePayment}
          disabled={loading}
          className="btn-pay-now"
        >
          {loading ? 'Processing...' : `Pay ₦${totalCost.toLocaleString()} with Paystack`}
        </button>
        
        <button
          onClick={() => navigate(`/my-requests/${requestId}`)}
          className="btn-cancel"
          disabled={loading}
        >
          Review Later
        </button>
      </div>

      {/* What Happens Next */}
      <div className="info-box">
        <h4>📋 What Happens After Payment?</h4>
        <ol>
          <li>✅ Payment processed securely via Paystack</li>
          <li>📧 Admin receives payment confirmation</li>
          <li>✅ Admin authorizes serviceman to start work</li>
          <li>📧 Serviceman receives work authorization</li>
          <li>🔧 Serviceman begins the job</li>
          <li>✅ Serviceman completes and notifies you</li>
          <li>⭐ You rate and review the serviceman</li>
        </ol>
      </div>

      {/* Security Info */}
      <div className="security-info">
        <h4>🔒 Secure Payment</h4>
        <p>
          All payments are processed securely through Paystack. 
          We never store your card details.
        </p>
      </div>
    </div>
  );
}

export default ClientPaymentPage;
```

---

## 📱 Simplified One-Click Payment

```jsx
// QuickPayButton.jsx - For inline payment on request details page
function QuickPayButton({ serviceRequest }) {
  const [loading, setLoading] = useState(false);

  const handleQuickPay = async () => {
    if (serviceRequest.status !== 'AWAITING_CLIENT_APPROVAL') {
      alert('This request is not ready for payment');
      return;
    }

    setLoading(true);

    try {
      const accessToken = localStorage.getItem('accessToken');
      
      // Initialize payment
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

      const data = await response.json();

      if (response.ok) {
        // Save for verification
        localStorage.setItem('pendingPaymentReference', data.paystack_reference);
        localStorage.setItem('pendingServiceRequestId', serviceRequest.id);
        
        // Redirect to Paystack
        window.location.href = data.authorization_url;
      } else {
        alert('Payment failed: ' + (data.error || 'Unknown error'));
        setLoading(false);
      }
    } catch (error) {
      alert('Network error. Please try again.');
      setLoading(false);
    }
  };

  if (serviceRequest.status !== 'AWAITING_CLIENT_APPROVAL') {
    return null;
  }

  return (
    <button 
      onClick={handleQuickPay}
      disabled={loading}
      className="btn-pay-now"
    >
      {loading ? 'Processing...' : `💳 Pay ₦${parseFloat(serviceRequest.final_cost).toLocaleString()}`}
    </button>
  );
}
```

---

## 🎯 Integration Points

### 1. Add Payment Button to Request Details

```jsx
// MyRequestDetailsPage.jsx
function MyRequestDetailsPage() {
  const { requestId } = useParams();
  const [serviceRequest, setServiceRequest] = useState(null);

  return (
    <div className="request-details">
      <h2>Request #{requestId}</h2>
      
      {/* Request info */}
      <div className="request-info">
        <p>Status: {serviceRequest.status}</p>
        <p>Category: {serviceRequest.category.name}</p>
        {/* ... more details */}
      </div>

      {/* Price Section (if finalized) */}
      {serviceRequest.final_cost && (
        <div className="price-section">
          <h3>Pricing</h3>
          <p>Service Cost: ₦{parseFloat(serviceRequest.serviceman_estimated_cost).toLocaleString()}</p>
          <p>Platform Fee: ₦{(parseFloat(serviceRequest.final_cost) - parseFloat(serviceRequest.serviceman_estimated_cost)).toLocaleString()}</p>
          <p><strong>Total: ₦{parseFloat(serviceRequest.final_cost).toLocaleString()}</strong></p>
        </div>
      )}

      {/* Payment Button */}
      {serviceRequest.status === 'AWAITING_CLIENT_APPROVAL' && (
        <div className="payment-section">
          <div className="alert-info">
            ℹ️ Payment required to proceed with this service request
          </div>
          <QuickPayButton serviceRequest={serviceRequest} />
        </div>
      )}

      {/* Status-specific actions */}
      {serviceRequest.status === 'PAYMENT_COMPLETED' && (
        <div className="alert-success">
          ✅ Payment completed! Waiting for admin to authorize work.
        </div>
      )}

      {serviceRequest.status === 'IN_PROGRESS' && (
        <div className="alert-info">
          🔧 Work in progress. Serviceman is working on your request.
        </div>
      )}
    </div>
  );
}
```

---

### 2. Add Notification Handler

```jsx
// NotificationItem.jsx
function NotificationItem({ notification }) {
  const navigate = useNavigate();

  const handleClick = () => {
    // Mark as read
    markNotificationAsRead(notification.id);

    // If payment request notification, navigate to payment page
    if (notification.notification_type === 'PAYMENT_REQUEST') {
      // Extract request ID from notification
      const requestId = notification.service_request_id || 
                       extractRequestIdFromMessage(notification.message);
      
      if (requestId) {
        navigate(`/my-requests/${requestId}/payment`);
      }
    } else {
      // Navigate to request details
      const requestId = notification.service_request_id;
      if (requestId) {
        navigate(`/my-requests/${requestId}`);
      }
    }
  };

  return (
    <div 
      className={`notification-item ${notification.is_read ? 'read' : 'unread'}`}
      onClick={handleClick}
    >
      <div className="notification-header">
        <h4>{notification.title}</h4>
        <span className="notification-time">
          {new Date(notification.created_at).toLocaleString()}
        </span>
      </div>
      <p className="notification-message">{notification.message}</p>
      {!notification.is_read && <span className="unread-dot">●</span>}
    </div>
  );
}
```

---

## 🔔 What Happens After Payment

### Automatic Actions:

1. **Payment Status Updated**
   - Payment status: `PENDING` → `SUCCESSFUL`
   - Paid timestamp recorded

2. **Service Request Updated**
   - Status: `AWAITING_CLIENT_APPROVAL` → `PAYMENT_COMPLETED`

3. **Notifications Sent**
   - **Admin:** "Payment Received - Request #9"
   - **Client:** "Payment Confirmed - Request #9"

4. **Admin Authorizes Work** (Manual Step)
   - Admin reviews payment confirmation
   - Admin authorizes serviceman to start
   - Status: `PAYMENT_COMPLETED` → `IN_PROGRESS`

5. **Serviceman Notified**
   - Gets work authorization notification
   - Can now begin the job

---

## 📊 Price Calculation Reference

```javascript
// Helper function to calculate pricing
const calculatePricing = (serviceRequest) => {
  const baseCost = parseFloat(serviceRequest.serviceman_estimated_cost);
  const markupPercent = parseFloat(serviceRequest.admin_markup_percentage);
  const platformFee = baseCost * (markupPercent / 100);
  const finalCost = baseCost + platformFee;
  const bookingFee = parseFloat(serviceRequest.initial_booking_fee);
  
  return {
    baseCost,           // ₦15,000
    platformFee,        // ₦1,500
    finalCost,          // ₦16,500
    bookingFee,         // ₦2,000
    markupPercent       // 10%
  };
};

// Usage
const pricing = calculatePricing(serviceRequest);
console.log(`Total to pay: ₦${pricing.finalCost.toLocaleString()}`);
```

---

## ⚠️ Important Notes

### 1. Payment Types

There are **TWO different payments**:

| Payment Type | When | Amount | Purpose |
|-------------|------|--------|---------|
| `INITIAL_BOOKING` | Before creating request | ₦2,000 or ₦5,000 | Booking fee |
| `SERVICE_PAYMENT` | After price approval | Final cost | Service payment |

**Make sure you use the correct `payment_type`!**

### 2. Amount Validation

Backend will validate:
- ✅ Amount matches `final_cost` in service request
- ✅ Service request status is `AWAITING_CLIENT_APPROVAL`
- ✅ Client is the request owner

### 3. Callback URL

Set your callback URL to handle payment verification:
```javascript
// The URL Paystack redirects to after payment
const callbackUrl = `${window.location.origin}/verify-payment`;
```

This page should:
- Parse `?reference=` from URL
- Call `/api/payments/verify/`
- Show success/error
- Redirect to request details

---

## ✅ Frontend Checklist

**Payment Page:**
- [ ] Fetch service request details
- [ ] Verify status is `AWAITING_CLIENT_APPROVAL`
- [ ] Display price breakdown clearly
- [ ] Show what's included (description, notes)
- [ ] Show serviceman info
- [ ] "Pay Now" button triggers payment
- [ ] Handle loading state
- [ ] Show error messages

**Payment Flow:**
- [ ] Initialize payment via API
- [ ] Save payment reference in localStorage
- [ ] Redirect to Paystack authorization URL
- [ ] Handle Paystack callback
- [ ] Verify payment via API
- [ ] Show success/failure message
- [ ] Clear localStorage on success
- [ ] Redirect to request details

**UI/UX:**
- [ ] Clear price breakdown (base + fee + total)
- [ ] Show booking fee already paid
- [ ] Security badges (Paystack logo, SSL icon)
- [ ] "What happens next?" section
- [ ] Mobile-responsive design
- [ ] Confirmation before payment

---

## 🎨 CSS Styling Example

```css
.price-breakdown {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin: 20px 0;
}

.breakdown-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #dee2e6;
}

.breakdown-row.total {
  font-size: 1.2em;
  color: #667eea;
  border-bottom: 2px solid #667eea;
}

.breakdown-row.paid {
  color: #28a745;
}

.breakdown-row.final {
  font-size: 1.5em;
  font-weight: bold;
  color: #212529;
  border: none;
  padding-top: 20px;
}

.final-amount {
  color: #667eea;
  font-size: 1.8em;
}

.btn-pay-now {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px 40px;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  margin-top: 20px;
  transition: transform 0.2s;
}

.btn-pay-now:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-pay-now:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.security-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background: #e7f3ff;
  border-radius: 6px;
  margin-top: 20px;
  font-size: 0.9em;
  color: #0c5460;
}

.security-info::before {
  content: '🔒';
  font-size: 1.5em;
}
```

---

## 🧪 Testing Scenarios

### Scenario 1: Happy Path

1. Client receives "Price Ready" notification
2. Client views request - sees final price
3. Client clicks "Pay Now"
4. Redirects to Paystack
5. Client pays successfully
6. Redirects back to app
7. Payment verified
8. Status changes to PAYMENT_COMPLETED
9. Admin and client notified
10. Admin authorizes work

**Expected:** ✅ All steps succeed

---

### Scenario 2: Payment Failure

1. Client clicks "Pay Now"
2. Redirects to Paystack
3. Client cancels or payment fails
4. Redirects back to app
5. Verification shows failure
6. Client sees error message
7. Can try again

**Expected:** ✅ User can retry payment

---

### Scenario 3: Wrong Status

Client tries to pay when status is not `AWAITING_CLIENT_APPROVAL`

**Expected:** ❌ Show message "Payment not required at this time"

---

## 🔍 Debugging

### Check Request Status

```javascript
const request = await fetch(`/api/services/service-requests/${requestId}/`);
const data = await request.json();

console.log('Status:', data.status);
console.log('Can pay?', data.status === 'AWAITING_CLIENT_APPROVAL');
console.log('Final cost:', data.final_cost);
console.log('Has final cost?', !!data.final_cost);
```

### Check Payment Initialization

```javascript
const response = await fetch('/api/payments/initialize/', {
  method: 'POST',
  body: JSON.stringify({
    service_request: 9,
    payment_type: 'SERVICE_PAYMENT',
    amount: 16500
  })
});

console.log('Status:', response.status);
console.log('Data:', await response.json());
```

### Check Payment Verification

```javascript
const response = await fetch(`/api/payments/verify/?reference=${reference}`);
const data = await response.json();

console.log('Payment status:', data.status);
console.log('Success?', data.status === 'success');
console.log('Request updated?', data.service_request_id);
```

---

## 📞 Support

**If payment fails:**
1. Check console for errors
2. Verify service request status
3. Ensure amount matches final_cost
4. Check Paystack dashboard
5. Contact admin if issues persist

---

## 🎯 Quick Implementation Summary

**3 Simple Steps for Frontend:**

1. **Payment Page:**
   - Show price breakdown
   - "Pay Now" button
   - POST `/api/payments/initialize/`

2. **Paystack Redirect:**
   - Save reference in localStorage
   - Redirect to `authorization_url`

3. **Callback Page:**
   - GET `/api/payments/verify/?reference=X`
   - Show success/error
   - Redirect to request details

**That's it!** 🚀

---

**Last Updated:** November 5, 2025  
**Status:** ✅ Backend Ready | 🔄 Frontend Implementation Needed  
**Note:** Console email backend in use (no SMTP yet)

