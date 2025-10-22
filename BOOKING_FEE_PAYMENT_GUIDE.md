# 💳 Booking Fee Payment System - Frontend Developer Guide

## 🎯 Overview

**IMPORTANT:** Clients MUST pay a booking fee BEFORE creating a service request!

### Booking Fees
- **Normal Booking:** ₦2,000
- **Emergency Booking:** ₦5,000

---

## 🔄 Complete Payment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     BOOKING FEE PAYMENT FLOW                     │
└─────────────────────────────────────────────────────────────────┘

1. User fills service request form
   ├── Category
   ├── Booking date
   ├── Is emergency? (checkbox)
   ├── Address
   └── Description

2. User clicks "Submit Request"
   ↓
3. Frontend calculates fee
   ├── Emergency? → ₦5,000
   └── Normal? → ₦2,000
   ↓
4. Show payment confirmation modal
   "Please pay ₦X,XXX booking fee to proceed"
   ↓
5. User confirms payment
   ↓
6. Frontend calls: POST /api/payments/initialize-booking-fee/
   ↓
7. Backend returns Paystack URL
   ↓
8. Redirect user to Paystack payment page
   ↓
9. User completes payment on Paystack
   ↓
10. Paystack redirects to: /payment/booking-callback?reference=XXX
    ↓
11. Frontend calls: POST /api/payments/verify/
    ↓
12. Backend verifies payment with Paystack
    ↓
13. If successful, frontend calls: POST /api/services/requests/
    ↓
14. Backend verifies payment and creates service request
    ↓
15. ✅ DONE! Show success message
```

---

## 📡 API Endpoints

### 1. Initialize Booking Fee Payment

**Endpoint:** `POST /api/payments/initialize-booking-fee/`

**Authorization:** Bearer Token (Client only)

**Request Body:**
```json
{
  "is_emergency": false
}
```

**Response (201 Created):**
```json
{
  "payment": {
    "id": 123,
    "service_request": null,
    "payment_type": "INITIAL_BOOKING",
    "amount": "2000.00",
    "paystack_reference": "BOOKING-45-1729589234.567",
    "paystack_access_code": "abc123xyz",
    "status": "PENDING",
    "is_emergency": false,
    "paid_at": null,
    "created_at": "2025-10-22T10:30:00Z",
    "updated_at": "2025-10-22T10:30:00Z"
  },
  "paystack_url": "https://checkout.paystack.com/abc123xyz",
  "amount": "2000.00",
  "reference": "BOOKING-45-1729589234.567",
  "message": "Please complete payment of ₦2,000.00 to proceed"
}
```

**What to do:**
```javascript
// Save the reference to localStorage or state
localStorage.setItem('pendingPaymentReference', response.reference);
localStorage.setItem('pendingServiceRequest', JSON.stringify(formData));

// Redirect user to Paystack
window.location.href = response.paystack_url;
```

---

### 2. Verify Payment

**Endpoint:** `POST /api/payments/verify/`

**Authorization:** None (Public endpoint)

**Request Body:**
```json
{
  "reference": "BOOKING-45-1729589234.567"
}
```

**Response (200 OK):**
```json
{
  "status": "SUCCESSFUL"
}
```

**Possible Statuses:**
- `"SUCCESSFUL"` - Payment completed ✅
- `"PENDING"` - Payment not completed yet ⏳
- `"FAILED"` - Payment failed ❌

---

### 3. Create Service Request (WITH Payment Reference)

**Endpoint:** `POST /api/services/requests/`

**Authorization:** Bearer Token (Client only)

**Request Body:**
```json
{
  "payment_reference": "BOOKING-45-1729589234.567",
  "category_id": 1,
  "booking_date": "2025-10-25",
  "is_emergency": false,
  "client_address": "123 Main Street, Lagos",
  "service_description": "Kitchen sink is leaking",
  "initial_booking_fee": 2000
}
```

**Response (201 Created):**
```json
{
  "id": 456,
  "client": {...},
  "category": {...},
  "booking_date": "2025-10-25",
  "is_emergency": false,
  "status": "PENDING_ADMIN_ASSIGNMENT",
  "initial_booking_fee": "2000.00",
  "client_address": "123 Main Street, Lagos",
  "service_description": "Kitchen sink is leaking",
  "payment_reference": "BOOKING-45-1729589234.567",
  "payment_amount": "2000.00",
  "created_at": "2025-10-22T10:32:00Z"
}
```

**Error Responses:**

```json
// No payment reference provided
{
  "error": "Payment required",
  "detail": "You must pay the booking fee before creating a service request. Please call POST /api/payments/initialize-booking-fee/ first."
}

// Payment not found
{
  "error": "Invalid payment reference",
  "detail": "The provided payment reference does not exist."
}

// Payment not completed
{
  "error": "Payment not completed",
  "detail": "Payment status is 'PENDING'. Please complete payment first.",
  "payment_status": "PENDING"
}

// Payment already used
{
  "error": "Payment already used",
  "detail": "This payment has already been used for another service request.",
  "existing_request_id": 123
}

// Amount mismatch
{
  "error": "Payment amount mismatch",
  "detail": "Expected ₦5,000.00 for emergency booking, but payment was ₦2,000.00. Please initialize payment again with correct booking type."
}
```

---

## 🎨 Frontend Implementation

### Step 1: Service Request Form Component

```jsx
import { useState } from 'react';
import axios from 'axios';

function ServiceRequestForm() {
  const [formData, setFormData] = useState({
    category_id: '',
    booking_date: '',
    is_emergency: false,
    client_address: '',
    service_description: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  
  const bookingFee = formData.is_emergency ? 5000 : 2000;
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Show payment confirmation modal
    setShowPaymentModal(true);
  };
  
  const proceedToPayment = async () => {
    setLoading(true);
    
    try {
      // 1. Initialize booking fee payment
      const response = await axios.post(
        'https://serviceman-backend.onrender.com/api/payments/initialize-booking-fee/',
        { is_emergency: formData.is_emergency },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // 2. Save data to localStorage
      localStorage.setItem('pendingPaymentReference', response.data.reference);
      localStorage.setItem('pendingServiceRequest', JSON.stringify(formData));
      
      // 3. Redirect to Paystack
      window.location.href = response.data.paystack_url;
      
    } catch (error) {
      console.error('Payment initialization failed:', error);
      alert('Failed to initialize payment. Please try again.');
      setLoading(false);
    }
  };
  
  return (
    <div>
      <form onSubmit={handleSubmit}>
        <select 
          value={formData.category_id} 
          onChange={e => setFormData({...formData, category_id: e.target.value})}
          required
        >
          <option value="">Select Category</option>
          {/* Populate from categories API */}
        </select>
        
        <input 
          type="date"
          value={formData.booking_date}
          onChange={e => setFormData({...formData, booking_date: e.target.value})}
          min={new Date().toISOString().split('T')[0]}
          required
        />
        
        <label>
          <input 
            type="checkbox"
            checked={formData.is_emergency}
            onChange={e => setFormData({...formData, is_emergency: e.target.checked})}
          />
          Emergency Booking (+₦3,000)
        </label>
        
        <textarea
          placeholder="Service Address"
          value={formData.client_address}
          onChange={e => setFormData({...formData, client_address: e.target.value})}
          required
        />
        
        <textarea
          placeholder="Describe the service needed"
          value={formData.service_description}
          onChange={e => setFormData({...formData, service_description: e.target.value})}
          required
        />
        
        <button type="submit">Submit Request</button>
      </form>
      
      {showPaymentModal && (
        <PaymentModal 
          amount={bookingFee}
          onConfirm={proceedToPayment}
          onCancel={() => setShowPaymentModal(false)}
          loading={loading}
        />
      )}
    </div>
  );
}
```

---

### Step 2: Payment Callback Page

```jsx
// File: pages/payment/booking-callback.jsx
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import axios from 'axios';

function BookingPaymentCallback() {
  const router = useRouter();
  const { reference } = router.query;
  const [status, setStatus] = useState('verifying'); // verifying, success, failed
  
  useEffect(() => {
    if (reference) {
      verifyPaymentAndCreateRequest();
    }
  }, [reference]);
  
  const verifyPaymentAndCreateRequest = async () => {
    try {
      // 1. Verify payment
      const verifyResponse = await axios.post(
        'https://serviceman-backend.onrender.com/api/payments/verify/',
        { reference }
      );
      
      if (verifyResponse.data.status !== 'SUCCESSFUL') {
        setStatus('failed');
        return;
      }
      
      // 2. Get saved service request data
      const savedData = localStorage.getItem('pendingServiceRequest');
      if (!savedData) {
        throw new Error('No pending service request found');
      }
      
      const requestData = JSON.parse(savedData);
      
      // 3. Create service request with payment reference
      const createResponse = await axios.post(
        'https://serviceman-backend.onrender.com/api/services/requests/',
        {
          ...requestData,
          payment_reference: reference,
          initial_booking_fee: requestData.is_emergency ? 5000 : 2000
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      // 4. Clear saved data
      localStorage.removeItem('pendingPaymentReference');
      localStorage.removeItem('pendingServiceRequest');
      
      // 5. Show success
      setStatus('success');
      
      // 6. Redirect to request details page after 3 seconds
      setTimeout(() => {
        router.push(`/requests/${createResponse.data.id}`);
      }, 3000);
      
    } catch (error) {
      console.error('Error:', error);
      setStatus('failed');
    }
  };
  
  return (
    <div className="payment-callback">
      {status === 'verifying' && (
        <div>
          <div className="spinner" />
          <h2>Verifying Payment...</h2>
          <p>Please wait while we confirm your payment</p>
        </div>
      )}
      
      {status === 'success' && (
        <div className="success">
          <div className="checkmark">✓</div>
          <h2>Payment Successful!</h2>
          <p>Your service request has been created.</p>
          <p>Redirecting to request details...</p>
        </div>
      )}
      
      {status === 'failed' && (
        <div className="error">
          <div className="error-icon">✗</div>
          <h2>Payment Failed</h2>
          <p>Your payment could not be verified.</p>
          <button onClick={() => router.push('/requests/new')}>
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}

export default BookingPaymentCallback;
```

---

### Step 3: Payment Modal Component

```jsx
function PaymentModal({ amount, onConfirm, onCancel, loading }) {
  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Booking Fee Required</h2>
        <p>You need to pay a booking fee before submitting your request.</p>
        
        <div className="fee-display">
          <span className="currency">₦</span>
          <span className="amount">{amount.toLocaleString()}</span>
        </div>
        
        <p className="fee-note">
          {amount === 5000 ? (
            <>Emergency bookings require a ₦5,000 booking fee.</>
          ) : (
            <>Normal bookings require a ₦2,000 booking fee.</>
          )}
        </p>
        
        <div className="modal-actions">
          <button 
            onClick={onCancel} 
            disabled={loading}
            className="btn-cancel"
          >
            Cancel
          </button>
          <button 
            onClick={onConfirm} 
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Processing...' : 'Proceed to Payment'}
          </button>
        </div>
      </div>
    </div>
  );
}
```

---

## 🎯 Key Points for Frontend Developers

### ✅ DO:
1. **Always show the booking fee upfront** - Users should know the cost before submitting
2. **Save form data to localStorage** before redirecting to Paystack
3. **Verify payment status** on callback page before creating request
4. **Handle all error cases** - Payment failed, payment already used, etc.
5. **Clear localStorage** after successful request creation
6. **Show loading states** during all async operations
7. **Provide clear error messages** if payment fails

### ❌ DON'T:
1. **Don't skip payment** - Backend will reject requests without valid payment
2. **Don't reuse payment references** - Each payment can only be used once
3. **Don't submit form directly** - Always initialize payment first
4. **Don't lose form data** - Save to localStorage before Paystack redirect
5. **Don't assume payment success** - Always verify on callback

---

## 🔍 Testing Checklist

### Test Cases:
- [ ] Normal booking fee (₦2,000) is calculated correctly
- [ ] Emergency booking fee (₦5,000) is calculated correctly
- [ ] Payment modal shows correct amount
- [ ] Paystack redirect works
- [ ] Payment verification on callback works
- [ ] Service request is created after successful payment
- [ ] Error shown if payment not completed
- [ ] Error shown if payment reference missing
- [ ] Error shown if payment already used
- [ ] Form data persists through Paystack redirect
- [ ] localStorage is cleared after success

### Paystack Test Cards:
```
Success: 4084 0840 8408 4081 (CVV: 408, Expiry: Any future date)
Failed:  5060 6666 6666 6666 (CVV: 123, Expiry: Any future date)
```

---

## 🚨 Error Handling Examples

### Payment Reference Missing
```javascript
try {
  const response = await axios.post('/api/services/requests/', {
    // payment_reference missing!
    category_id: 1,
    // ...
  });
} catch (error) {
  if (error.response.status === 400) {
    alert('Payment required! Please pay the booking fee first.');
    router.push('/requests/new');
  }
}
```

### Payment Already Used
```javascript
if (error.response.data.error === 'Payment already used') {
  alert('This payment has already been used. Please make a new payment.');
  localStorage.removeItem('pendingPaymentReference');
  router.push('/requests/new');
}
```

### Amount Mismatch
```javascript
if (error.response.data.error === 'Payment amount mismatch') {
  alert('Payment amount doesn\'t match booking type. Please pay again.');
  localStorage.removeItem('pendingPaymentReference');
  router.push('/requests/new');
}
```

---

## 📱 Mobile Considerations

1. **Deep Links:** Ensure Paystack callback URL works on mobile browsers
2. **LocalStorage:** Verify localStorage persists across browser tabs/windows
3. **Network Errors:** Handle poor network conditions gracefully
4. **Session Timeout:** Refresh auth token if needed during payment flow

---

## 🎓 Summary

**Payment Flow in 3 Steps:**
1. **Initialize** → `POST /api/payments/initialize-booking-fee/`
2. **Pay** → Redirect to Paystack URL
3. **Create** → `POST /api/services/requests/` with `payment_reference`

**Remember:**
- Booking fee MUST be paid first
- Save form data before Paystack redirect
- Verify payment on callback
- Handle all error cases
- Clear localStorage after success

---

## 🆘 Support

If you encounter issues:
1. Check browser console for errors
2. Verify API responses match this documentation
3. Test with Paystack test cards first
4. Contact backend team with error details

---

**Happy coding! 🚀**

