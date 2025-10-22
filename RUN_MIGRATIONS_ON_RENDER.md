# 🚀 Run Database Migrations on Render

## ⚠️ CRITICAL: Migrations Required for Booking Fee Feature

The booking fee payment feature requires database migrations to be run. Until migrations are applied, users will receive a **503 error** with the message:

```json
{
  "error": "Database migration required",
  "detail": "The booking fee payment feature requires database migrations to be run..."
}
```

## 📋 What These Migrations Do

**Migration: `0003_payment_booking_fee_support.py`**

1. **Makes `service_request` nullable** on the `Payment` model
   - Allows booking fee payments to be created BEFORE a service request exists
   - Changes: `null=False` → `null=True, blank=True`

2. **Adds `is_emergency` field** to the `Payment` model
   - Tracks whether the payment is for an emergency booking (₦5,000) or normal (₦2,000)
   - Type: `BooleanField(default=False)`

---

## 🔧 How to Run Migrations on Render

### Option 1: Via Render Shell (Recommended)

1. **Go to your Render dashboard**: https://dashboard.render.com
2. **Select your service**: `serviceman-backend`
3. **Click "Shell"** in the top right corner
4. **Run the migration command**:
   ```bash
   python manage.py migrate payments
   ```
5. **Verify the migration**:
   ```bash
   python manage.py showmigrations payments
   ```
   
   You should see:
   ```
   payments
    [X] 0001_initial
    [X] 0002_initial
    [X] 0003_payment_booking_fee_support  ← This should be marked with [X]
   ```

### Option 2: Add to Render Build Command

1. Go to your Render dashboard
2. Select your service
3. Go to **Settings** → **Build & Deploy**
4. Update the **Build Command** to include migrations:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
5. **Manual Deploy** to trigger the build

### Option 3: SSH into Render (Advanced)

If you have SSH access configured:
```bash
ssh render@your-service.onrender.com
cd /opt/render/project/src
python manage.py migrate payments
```

---

## ✅ After Running Migrations

Once migrations are applied:

1. **Test the booking fee endpoint**:
   ```bash
   curl -X POST https://serviceman-backend.onrender.com/api/payments/initialize-booking-fee/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"is_emergency": false}'
   ```

2. **Expected response**:
   ```json
   {
     "payment": {
       "id": 1,
       "payment_type": "INITIAL_BOOKING",
       "amount": "2000.00",
       "status": "PENDING",
       "is_emergency": false,
       ...
     },
     "paystack_url": "https://checkout.paystack.com/...",
     "amount": "2000.00",
     "reference": "BOOKING-1-1729606123.456",
     "message": "Please complete payment of ₦2,000.00 to proceed"
   }
   ```

---

## 🔍 Troubleshooting

### Error: "no such table: payments_payment"
This means no migrations have been run at all. Run:
```bash
python manage.py migrate
```

### Error: "column is_emergency already exists"
The migration has already been applied. You're good to go!

### Error: "relation payments_payment does not exist"
Run all migrations:
```bash
python manage.py migrate
```

### Verify Current Migration State
```bash
python manage.py showmigrations
```

### Check Database Schema
```bash
python manage.py dbshell
\d payments_payment
```

---

## 📊 Migration Details

### Before Migration
```sql
CREATE TABLE payments_payment (
    id SERIAL PRIMARY KEY,
    service_request_id INTEGER NOT NULL,  -- ❌ NOT NULL
    payment_type VARCHAR(16) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    -- ... other fields
    -- ❌ is_emergency field does NOT exist
);
```

### After Migration
```sql
CREATE TABLE payments_payment (
    id SERIAL PRIMARY KEY,
    service_request_id INTEGER NULL,  -- ✅ NULLABLE
    payment_type VARCHAR(16) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    is_emergency BOOLEAN NOT NULL DEFAULT FALSE,  -- ✅ NEW FIELD
    -- ... other fields
);
```

---

## 🚨 Important Notes

1. **Zero Downtime**: These migrations are safe to run in production:
   - Adding a nullable column = non-blocking
   - Adding a field with default = non-blocking
   - Making a field nullable = non-blocking

2. **Rollback Safety**: If something goes wrong, you can rollback:
   ```bash
   python manage.py migrate payments 0002_initial
   ```

3. **Data Safety**: These migrations don't modify or delete any existing data

4. **Backend Code**: The backend code is **already migration-safe**:
   - Checks if columns exist before using them
   - Falls back to raw SQL when needed
   - Provides clear error messages

---

## 📞 Need Help?

If you encounter issues:
1. Check the Render logs: Dashboard → Logs
2. Verify environment variables are set
3. Ensure DATABASE_URL is correct
4. Check PostgreSQL connection

---

## ✨ After Success

Once migrations are applied, the booking fee payment flow will be fully operational:

1. ✅ Client calls `POST /api/payments/initialize-booking-fee/`
2. ✅ Client pays on Paystack
3. ✅ Client creates service request with `payment_reference`
4. ✅ System verifies payment and creates request

**Happy deploying! 🎉**

