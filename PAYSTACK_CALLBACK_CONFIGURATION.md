# 💳 Paystack Callback URL Configuration Guide

## Version 1.0 | Last Updated: November 6, 2025

---

## 🎯 Overview

Your backend sends users to Paystack for payment, and Paystack redirects them back to your frontend with payment status.

---

## 📍 Current Callback URLs

### Backend Configuration

The backend is configured to use these callback URLs:

| Payment Type | Backend Callback URL | Frontend Route |
|-------------|---------------------|----------------|
| **Booking Fee** | `{FRONTEND_URL}/payment/booking-callback` | `/payment/booking-callback` |
| **Service Payment** | `{FRONTEND_URL}/payment/callback` | `/payment/callback` |

Where `{FRONTEND_URL}` is:
- **Production**: `https://serviceman-frontend.vercel.app`
- **Development**: `http://localhost:3000`

---

## 🔧 Backend Code (Already Configured)

### Booking Fee Payment

```python
# apps/payments/views.py - InitializeBookingFeeView
callback_url = settings.FRONTEND_URL + "/payment/booking-callback"

# Example: https://serviceman-frontend.vercel.app/payment/booking-callback
```

### Service Payment

```python
# apps/payments/views.py - InitializePaymentView
callback_url = settings.FRONTEND_URL + "/payment/callback"

# Example: https://serviceman-frontend.vercel.app/payment/callback
```

---

## 🎨 Frontend Implementation Required

### Step 1: Create Callback Routes

You need to create these routes in your React app:

```javascript
// In your router (e.g., App.js or routes.js)
import BookingCallbackPage from './pages/BookingCallbackPage';
import PaymentCallbackPage from './pages/PaymentCallbackPage';

// Add these routes:
<Routes>
  {/* Other routes... */}
  
  {/* Paystack Callback Routes */}
  <Route path="/payment/booking-callback" element={<BookingCallbackPage />} />
  <Route path="/payment/callback" element={<PaymentCallbackPage />} />
</Routes>
```

---

### Step 2: Create Booking Callback Page

**File**: `src/pages/BookingCallbackPage.jsx`

```javascript
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

function BookingCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying'); // 'verifying' | 'success' | 'failed'
  const [message, setMessage] = useState('Verifying your payment...');

  useEffect(() => {
    verifyPayment();
  }, []);

  const verifyPayment = async () => {
    // Get reference from URL query params
    const reference = searchParams.get('reference');
    
    if (!reference) {
      setStatus('failed');
      setMessage('No payment reference found');
      return;
    }

    try {
      // Verify payment with backend
      const response = await axios.post(
        'https://serviceman-backend.onrender.com/api/payments/verify/',
        { reference },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
          }
        }
      );

      if (response.data.status === 'success') {
        setStatus('success');
        setMessage('Booking fee paid successfully! You can now create your service request.');
        
        // Store reference in localStorage for next step
        localStorage.setItem('bookingFeeReference', reference);
        
        // Redirect to service request form after 3 seconds
        setTimeout(() => {
          navigate('/create-service-request');
        }, 3000);
      } else {
        setStatus('failed');
        setMessage('Payment verification failed. Please try again.');
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      setStatus('failed');
      setMessage(error.response?.data?.message || 'Payment verification failed');
    }
  };

  return (
    <div className="payment-callback-container">
      {status === 'verifying' && (
        <div className="verifying-state">
          <div className="spinner"></div>
          <h2>Verifying Payment...</h2>
          <p>Please wait while we confirm your payment with Paystack.</p>
        </div>
      )}

      {status === 'success' && (
        <div className="success-state">
          <div className="success-icon">✓</div>
          <h2>Payment Successful!</h2>
          <p>{message}</p>
          <p className="redirect-message">Redirecting you to create your service request...</p>
        </div>
      )}

      {status === 'failed' && (
        <div className="failed-state">
          <div className="error-icon">✗</div>
          <h2>Payment Failed</h2>
          <p>{message}</p>
          <button onClick={() => navigate('/services')}>
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}

export default BookingCallbackPage;
```

---

### Step 3: Create Service Payment Callback Page

**File**: `src/pages/PaymentCallbackPage.jsx`

```javascript
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

function PaymentCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('verifying');
  const [message, setMessage] = useState('Verifying your payment...');
  const [serviceRequestId, setServiceRequestId] = useState(null);

  useEffect(() => {
    verifyPayment();
  }, []);

  const verifyPayment = async () => {
    const reference = searchParams.get('reference');
    
    if (!reference) {
      setStatus('failed');
      setMessage('No payment reference found');
      return;
    }

    try {
      const response = await axios.post(
        'https://serviceman-backend.onrender.com/api/payments/verify/',
        { reference },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
          }
        }
      );

      if (response.data.status === 'success') {
        setStatus('success');
        setMessage('Payment confirmed! The admin will authorize the serviceman to begin work.');
        
        // Extract service request ID from reference
        // Format: "9-SERVICE_PAYMENT-1730900000.123"
        const requestId = reference.split('-')[0];
        setServiceRequestId(requestId);
        
        // Redirect to service request details after 3 seconds
        setTimeout(() => {
          navigate(`/service-requests/${requestId}`);
        }, 3000);
      } else {
        setStatus('failed');
        setMessage('Payment verification failed. Please contact support.');
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      setStatus('failed');
      setMessage(error.response?.data?.message || 'Payment verification failed');
    }
  };

  return (
    <div className="payment-callback-container">
      {status === 'verifying' && (
        <div className="verifying-state">
          <div className="spinner"></div>
          <h2>Verifying Payment...</h2>
          <p>Please wait while we confirm your payment with Paystack.</p>
        </div>
      )}

      {status === 'success' && (
        <div className="success-state">
          <div className="success-icon">✓</div>
          <h2>Payment Successful!</h2>
          <p>{message}</p>
          <div className="payment-details">
            <p><strong>Service Request:</strong> #{serviceRequestId}</p>
          </div>
          <p className="redirect-message">Redirecting you to your service request...</p>
        </div>
      )}

      {status === 'failed' && (
        <div className="failed-state">
          <div className="error-icon">✗</div>
          <h2>Payment Failed</h2>
          <p>{message}</p>
          <button onClick={() => navigate('/dashboard')}>
            Go to Dashboard
          </button>
          <button onClick={() => navigate('/support')} className="secondary">
            Contact Support
          </button>
        </div>
      )}
    </div>
  );
}

export default PaymentCallbackPage;
```

---

## 📊 Payment Flow Diagram

### Booking Fee Flow

```
Client clicks "Book Now"
    ↓
Frontend calls: POST /api/payments/initialize-booking-fee/
    ↓
Backend returns Paystack URL
    ↓
Frontend redirects to Paystack
    ↓
Client pays on Paystack
    ↓
Paystack redirects to: https://serviceman-frontend.vercel.app/payment/booking-callback?reference=ABC123
    ↓
BookingCallbackPage verifies payment
    ↓
Redirects to /create-service-request
```

### Service Payment Flow

```
Client views finalized price
    ↓
Frontend calls: POST /api/payments/initialize/
    ↓
Backend returns Paystack URL
    ↓
Frontend redirects to Paystack
    ↓
Client pays on Paystack
    ↓
Paystack redirects to: https://serviceman-frontend.vercel.app/payment/callback?reference=9-SERVICE_PAYMENT-123
    ↓
PaymentCallbackPage verifies payment
    ↓
Redirects to /service-requests/9
```

---

## 🔒 Security Notes

### 1. Always Verify Payment with Backend

**Never trust the callback URL alone!** Always verify with your backend:

```javascript
// ❌ WRONG - Don't trust URL params
const success = searchParams.get('success'); // Can be faked!
if (success === 'true') {
  // ❌ Don't do this!
}

// ✅ CORRECT - Always verify with backend
const reference = searchParams.get('reference');
const response = await axios.post('/api/payments/verify/', { reference });
if (response.data.status === 'success') {
  // ✅ Do this!
}
```

### 2. Handle All Payment States

Your callback page should handle:
- ✅ Success
- ❌ Failed
- ⏳ Pending
- 🔄 Verifying

---

## 🎨 Styling Example (Optional)

```css
/* PaymentCallback.css */
.payment-callback-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.verifying-state,
.success-state,
.failed-state {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  text-align: center;
  max-width: 500px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.success-icon {
  width: 80px;
  height: 80px;
  background: #10b981;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: white;
  margin: 0 auto 1rem;
}

.error-icon {
  width: 80px;
  height: 80px;
  background: #ef4444;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: white;
  margin: 0 auto 1rem;
}

button {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  margin: 0.5rem;
}

button:hover {
  background: #5568d3;
}

button.secondary {
  background: #6b7280;
}
```

---

## 🧪 Testing Callback URLs

### Test in Development

1. **Start your React app**: `npm start`
2. **Make sure it's on**: `http://localhost:3000`
3. **Backend will use**: `http://localhost:3000/payment/booking-callback`
4. **Paystack will redirect to**: `http://localhost:3000/payment/booking-callback?reference=ABC123`

### Test in Production

1. **Deploy frontend to Vercel**: Already at `https://serviceman-frontend.vercel.app`
2. **Set backend env var**: `FRONTEND_URL=https://serviceman-frontend.vercel.app`
3. **Paystack will redirect to**: `https://serviceman-frontend.vercel.app/payment/callback?reference=XYZ789`

---

## 🌐 Configure Paystack Dashboard (Optional)

While not required (backend handles this), you can also set these in Paystack Dashboard:

1. **Login to**: https://dashboard.paystack.com
2. **Go to**: Settings → Payment Pages → Redirect URL
3. **Set Production URL**: `https://serviceman-frontend.vercel.app/payment/callback`
4. **Set Test URL**: `http://localhost:3000/payment/callback`

**Note**: Backend already sends callback URL with each payment, so this is optional.

---

## 📋 Checklist

Before going live, verify:

- [ ] ✅ Frontend has `/payment/booking-callback` route
- [ ] ✅ Frontend has `/payment/callback` route
- [ ] ✅ Both routes call `/api/payments/verify/` with reference
- [ ] ✅ Backend `FRONTEND_URL` is set correctly in Render
- [ ] ✅ Callback pages handle success/failed states
- [ ] ✅ Tested with Paystack test cards
- [ ] ✅ Production URLs use HTTPS

---

## 🧪 Test Cards (Paystack)

Use these to test in development:

| Card Number | CVV | Expiry | PIN | Result |
|------------|-----|--------|-----|--------|
| `4084 0840 8408 4081` | 408 | 12/30 | 0000 | Success |
| `5060 6666 6666 6666` | 123 | 12/30 | 1234 | Failed |

---

## 🐛 Common Issues

### Issue 1: "Callback URL not found (404)"

**Cause**: Frontend route not created  
**Fix**: Create the callback route in your React router

### Issue 2: "CORS error on callback"

**Cause**: Backend doesn't have frontend URL in CORS  
**Fix**: Already configured! Backend has your Vercel URL in CORS_ALLOWED_ORIGINS

### Issue 3: "Payment verified but page stuck"

**Cause**: Missing `navigate()` redirect  
**Fix**: Add `setTimeout(() => navigate('/next-page'), 3000)`

### Issue 4: "Reference not found in URL"

**Cause**: Paystack didn't append reference  
**Fix**: Check backend is sending correct callback_url to Paystack

---

## 📞 Support

If callback URLs aren't working:

1. **Check browser console** for errors
2. **Check Network tab** - see what URL Paystack redirected to
3. **Check backend logs** - verify callback_url sent to Paystack
4. **Test with Paystack test cards** before using real money

---

## ✅ Summary

| Setting | Value |
|---------|-------|
| **Production Frontend URL** | `https://serviceman-frontend.vercel.app` |
| **Booking Fee Callback** | `/payment/booking-callback` |
| **Service Payment Callback** | `/payment/callback` |
| **Backend Environment Variable** | `FRONTEND_URL=https://serviceman-frontend.vercel.app` |
| **Already Configured?** | ✅ Yes (backend updated) |
| **Action Required** | Create frontend callback routes |

---

**Backend is ready! Frontend needs to create the callback pages.** ✅

