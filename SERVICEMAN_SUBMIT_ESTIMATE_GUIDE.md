# 💰 Serviceman: How to Submit Cost Estimate

**Complete guide for servicemen to submit cost estimates after site inspection**

---

## 📋 Overview

After admin assigns a serviceman to a service request, the serviceman must:
1. Visit the client's site
2. Inspect the job
3. Calculate the cost
4. Submit estimate through the API

---

## 🔄 The Workflow

```
STEP 2: Admin assigns serviceman
   Status: PENDING_ESTIMATION
   ↓
STEP 3: Serviceman submits estimate (THIS GUIDE)
   Status: ESTIMATION_SUBMITTED
   ↓
STEP 4: Admin adds platform fee
   Status: AWAITING_CLIENT_APPROVAL
```

---

## 📡 API Endpoint

**Endpoint:** `POST /api/services/service-requests/<id>/submit-estimate/`

**Method:** `POST`

**Authentication:** Required (Serviceman only)

**Permissions:**
- ✅ Only assigned serviceman can submit
- ✅ Status must be `PENDING_ESTIMATION`
- ❌ Backup serviceman cannot submit (only primary)

---

## 📝 Request Format

### Headers
```http
POST /api/services/service-requests/9/submit-estimate/
Authorization: Bearer <serviceman_access_token>
Content-Type: application/json
```

### Request Body
```json
{
  "estimated_cost": 15000.00,
  "notes": "Requires 3 new pipes, labor cost included"
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `estimated_cost` | number/decimal | **Required** | Your cost estimate in Naira (₦) |
| `notes` | string | Optional | Additional notes about the estimate |

---

## ✅ Successful Response

**Status Code:** `200 OK`

```json
{
  "message": "Estimate submitted successfully. Admin will review and finalize pricing.",
  "service_request": {
    "id": 9,
    "status": "ESTIMATION_SUBMITTED",
    "serviceman_estimated_cost": "15000.00",
    "client": {
      "id": 10,
      "username": "jane_doe",
      "full_name": "Jane Doe",
      "email": "jane@example.com"
    },
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
    "service_description": "Fix leaking pipe in kitchen",
    "is_emergency": false,
    "created_at": "2025-11-05T10:00:00Z"
  }
}
```

---

## ❌ Error Responses

### 1. Not a Serviceman
**Status:** `403 Forbidden`
```json
{
  "error": "Only servicemen can submit estimates"
}
```

### 2. Not Assigned to This Request
**Status:** `403 Forbidden`
```json
{
  "error": "You are not assigned to this service request"
}
```

### 3. Wrong Status
**Status:** `400 Bad Request`
```json
{
  "error": "Cannot submit estimate. Current status: Estimation Submitted"
}
```

### 4. Missing Cost
**Status:** `400 Bad Request`
```json
{
  "error": "estimated_cost is required"
}
```

### 5. Invalid Cost
**Status:** `400 Bad Request`
```json
{
  "error": "Invalid estimated_cost: Cost must be positive"
}
```

---

## 💻 Frontend Implementation

### React Component Example

```jsx
// ServicemanEstimateForm.jsx
import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function ServicemanEstimateForm() {
  const { requestId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    estimated_cost: '',
    notes: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validation
    if (!formData.estimated_cost || parseFloat(formData.estimated_cost) <= 0) {
      setError('Please enter a valid cost estimate');
      setLoading(false);
      return;
    }

    try {
      const accessToken = localStorage.getItem('accessToken');
      
      const response = await fetch(
        `/api/services/service-requests/${requestId}/submit-estimate/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            estimated_cost: parseFloat(formData.estimated_cost),
            notes: formData.notes || undefined
          })
        }
      );

      const data = await response.json();

      if (response.ok) {
        // Success!
        alert('✅ Estimate submitted successfully!\n\nThe admin will review and add the platform fee before sending to the client.');
        
        // Redirect to serviceman dashboard or job details
        navigate(`/serviceman/jobs/${requestId}`);
      } else {
        // Handle errors
        setError(data.error || data.detail || 'Failed to submit estimate');
      }
    } catch (error) {
      console.error('Error submitting estimate:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="estimate-form-container">
      <h2>Submit Cost Estimate</h2>
      <p className="info-text">
        After inspecting the site, provide your cost estimate below.
        The admin will review and add the platform fee before presenting to the client.
      </p>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="estimated_cost">
            Cost Estimate (₦) <span className="required">*</span>
          </label>
          <input
            type="number"
            id="estimated_cost"
            value={formData.estimated_cost}
            onChange={(e) => setFormData({...formData, estimated_cost: e.target.value})}
            placeholder="Enter your cost estimate"
            min="0"
            step="0.01"
            required
          />
          <p className="help-text">
            Enter the total cost for labor and materials. Do NOT include platform fee.
          </p>
        </div>

        <div className="form-group">
          <label htmlFor="notes">
            Notes (Optional)
          </label>
          <textarea
            id="notes"
            value={formData.notes}
            onChange={(e) => setFormData({...formData, notes: e.target.value})}
            placeholder="Add any notes about the estimate (e.g., materials needed, time required)"
            rows={4}
          />
          <p className="help-text">
            Explain what the cost includes (materials, labor, time estimate, etc.)
          </p>
        </div>

        <div className="estimate-summary">
          <h3>Estimate Summary</h3>
          <div className="summary-row">
            <span>Your Estimate:</span>
            <strong>₦{formData.estimated_cost ? parseFloat(formData.estimated_cost).toLocaleString() : '0'}</strong>
          </div>
          <div className="summary-row">
            <span>Platform Fee:</span>
            <span className="muted">(Admin will add ~10%)</span>
          </div>
          <div className="summary-row total">
            <span>Approximate Final Price:</span>
            <strong>
              ₦{formData.estimated_cost ? 
                (parseFloat(formData.estimated_cost) * 1.1).toLocaleString() : '0'}
            </strong>
          </div>
        </div>

        <div className="form-actions">
          <button 
            type="button" 
            onClick={() => navigate(-1)}
            className="btn-secondary"
            disabled={loading}
          >
            Cancel
          </button>
          <button 
            type="submit" 
            className="btn-primary"
            disabled={loading || !formData.estimated_cost}
          >
            {loading ? 'Submitting...' : 'Submit Estimate'}
          </button>
        </div>
      </form>

      <div className="info-box">
        <h4>ℹ️ What Happens Next?</h4>
        <ol>
          <li>Admin reviews your estimate</li>
          <li>Admin adds platform fee (usually ~10%)</li>
          <li>Final price is sent to client for approval</li>
          <li>Client pays the final amount</li>
          <li>Admin authorizes you to start work</li>
          <li>You complete the job</li>
        </ol>
      </div>
    </div>
  );
}

export default ServicemanEstimateForm;
```

---

### Vue.js Example

```vue
<template>
  <div class="estimate-form-container">
    <h2>Submit Cost Estimate</h2>
    <p class="info-text">
      After inspecting the site, provide your cost estimate below.
    </p>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <form @submit.prevent="submitEstimate">
      <div class="form-group">
        <label for="estimated_cost">
          Cost Estimate (₦) <span class="required">*</span>
        </label>
        <input
          v-model.number="formData.estimated_cost"
          type="number"
          id="estimated_cost"
          placeholder="Enter your cost estimate"
          min="0"
          step="0.01"
          required
        />
      </div>

      <div class="form-group">
        <label for="notes">Notes (Optional)</label>
        <textarea
          v-model="formData.notes"
          id="notes"
          rows="4"
          placeholder="Add any notes about the estimate"
        />
      </div>

      <div class="estimate-summary">
        <h3>Estimate Summary</h3>
        <div class="summary-row">
          <span>Your Estimate:</span>
          <strong>₦{{ formData.estimated_cost?.toLocaleString() || '0' }}</strong>
        </div>
        <div class="summary-row total">
          <span>Approximate Final Price:</span>
          <strong>₦{{ approximateFinal }}</strong>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" @click="$router.back()" class="btn-secondary">
          Cancel
        </button>
        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Submitting...' : 'Submit Estimate' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';

const route = useRoute();
const router = useRouter();
const { accessToken } = useAuth();

const loading = ref(false);
const error = ref('');
const formData = ref({
  estimated_cost: null,
  notes: ''
});

const approximateFinal = computed(() => {
  if (!formData.value.estimated_cost) return '0';
  return (formData.value.estimated_cost * 1.1).toLocaleString();
});

const submitEstimate = async () => {
  loading.value = true;
  error.value = '';

  try {
    const response = await fetch(
      `/api/services/service-requests/${route.params.id}/submit-estimate/`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken.value}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          estimated_cost: formData.value.estimated_cost,
          notes: formData.value.notes || undefined
        })
      }
    );

    const data = await response.json();

    if (response.ok) {
      alert('✅ Estimate submitted successfully!');
      router.push(`/serviceman/jobs/${route.params.id}`);
    } else {
      error.value = data.error || data.detail || 'Failed to submit estimate';
    }
  } catch (err) {
    error.value = 'Network error. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>
```

---

## 🎯 Step-by-Step Usage

### 1. Serviceman Receives Assignment

```
📧 Notification: "New Job Assignment - Request #9"

You have been assigned to a new service request.

📋 Job Details:
• Category: Plumbing
• Booking Date: 2025-11-15
• Address: 123 Main St, Lagos
• Description: Fix leaking pipe in kitchen

👤 Client Contact:
• Name: Jane Doe
• Phone: +234 123 456 7890

📝 Next Step: Please contact the client to schedule a site visit and provide a cost estimate.
```

### 2. Serviceman Contacts Client

- Call/message client
- Schedule site visit
- Inspect the problem

### 3. Serviceman Calculates Cost

Example calculation:
```
Materials:
- 3 new pipes: ₦3,000
- Fittings: ₦1,500
- Sealant: ₦500

Labor:
- Time estimate: 3 hours
- Rate: ₦3,000/hour
- Labor cost: ₦9,000

Transportation: ₦1,000

TOTAL ESTIMATE: ₦15,000
```

### 4. Serviceman Submits Estimate

```javascript
POST /api/services/service-requests/9/submit-estimate/

{
  "estimated_cost": 15000,
  "notes": "Requires 3 new pipes (₦3k), fittings (₦1.5k), labor (3hrs @ ₦3k/hr). Includes transportation."
}
```

### 5. System Actions

**Automatically:**
- ✅ Status changes to `ESTIMATION_SUBMITTED`
- ✅ Admin receives notification
- ✅ Client receives notification that estimate is being reviewed
- ✅ Estimate is saved in database

---

## 📊 What Admin Sees

Admin receives:
```
📧 Notification: "Cost Estimate Submitted - Request #9"

Serviceman John Plumber submitted cost estimate of ₦15,000.00 for service request #9. 
Please review and add platform fee.

Notes: Requires 3 new pipes (₦3k), fittings (₦1.5k), labor (3hrs @ ₦3k/hr). 
Includes transportation.
```

Admin then:
1. Reviews the estimate
2. Adds platform fee (typically 10%)
3. Final price = ₦16,500 (₦15,000 + ₦1,500 platform fee)
4. Sends to client for approval

---

## 💡 Best Practices

### For Servicemen

1. **Be Thorough**
   - Inspect the entire problem area
   - Check for related issues
   - Consider all materials needed

2. **Be Transparent**
   - Break down costs in notes
   - Explain what's included
   - Mention time estimate

3. **Be Realistic**
   - Don't lowball to win job
   - Include buffer for unexpected issues
   - Consider your time and effort

4. **Be Professional**
   - Submit promptly after inspection
   - Communicate clearly with client
   - Be available for questions

5. **Good Notes Examples**
   ```
   ✅ "3 pipes (₦3k), fittings (₦1.5k), 3hrs labor (₦9k). Total includes transport."
   ✅ "Full bathroom repair: tiles (₦8k), plumbing (₦5k), 2-day job, labor ₦15k."
   ✅ "Emergency fix: immediate service fee ₦5k, parts ₦3k, 4hrs work ₦8k."
   
   ❌ "15000"  // Too vague
   ❌ "Cost"  // No information
   ```

---

## 🔒 Security & Validation

**Backend Validates:**
- ✅ User is authenticated
- ✅ User is a SERVICEMAN
- ✅ Serviceman is assigned to this request
- ✅ Status is PENDING_ESTIMATION
- ✅ estimated_cost is provided
- ✅ estimated_cost is a valid positive number
- ✅ estimated_cost is not negative or zero

**Frontend Should Validate:**
- ✅ Cost is a number
- ✅ Cost is positive
- ✅ Cost is reasonable (not too low/high)
- ✅ Notes are not too long (< 1000 chars)

---

## 🧪 Testing

### Test Scenarios

**1. Valid Submission**
```bash
curl -X POST \
  http://localhost:8001/api/services/service-requests/9/submit-estimate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "estimated_cost": 15000,
    "notes": "3 pipes, fittings, labor included"
  }'
```

**2. Missing Cost**
```bash
curl -X POST \
  http://localhost:8001/api/services/service-requests/9/submit-estimate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Some notes"
  }'
# Expected: 400 Bad Request - "estimated_cost is required"
```

**3. Negative Cost**
```bash
curl -X POST \
  http://localhost:8001/api/services/service-requests/9/submit-estimate/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "estimated_cost": -1000
  }'
# Expected: 400 Bad Request - "Cost must be positive"
```

---

## ✅ Checklist for Frontend

- [ ] Create estimate submission form
- [ ] Add cost input field (number, required)
- [ ] Add notes textarea (optional)
- [ ] Show estimate summary/preview
- [ ] Validate cost before submission
- [ ] Handle loading state
- [ ] Display success message
- [ ] Handle all error cases
- [ ] Redirect after success
- [ ] Show "What happens next?" info
- [ ] Format currency properly (₦)
- [ ] Add confirmation dialog (optional)

---

## 🎨 UI/UX Suggestions

1. **Show Client Info**
   - Display client name, phone, address
   - Easy access to contact client

2. **Job Details**
   - Show service description
   - Display booking date
   - Show any photos/attachments

3. **Cost Calculator** (Optional)
   - Materials section
   - Labor section
   - Transportation section
   - Auto-calculates total

4. **Estimate Preview**
   - Show serviceman's estimate
   - Show approximate platform fee (~10%)
   - Show approximate final price

5. **Success Confirmation**
   - Clear success message
   - Next steps explanation
   - Link to view job status

---

## 📞 Support

**Questions?**
- Check service request status via GET `/api/services/service-requests/<id>/`
- View your job history via GET `/api/serviceman/job-history/`
- Contact admin if issues

---

**Last Updated:** November 5, 2025  
**Version:** 1.0  
**Status:** ✅ Backend Ready | 🔄 Frontend Implementation Needed

