# 🚨 URGENT: Update Render Dashboard Settings

## ⚠️ Problem

Your Render service is using **OLD commands** from the dashboard instead of our new scripts. That's why migrations aren't running!

Your current Render start command:
```bash
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

This runs migrations in the START phase (too late) and doesn't show proper output.

---

## ✅ SOLUTION: Update Render Dashboard

### Step 1: Go to Render Dashboard
1. Open: https://dashboard.render.com
2. Select your **serviceman-backend** service
3. Click **"Settings"** (in the left sidebar)

### Step 2: Update Build & Deploy Settings
Scroll down to **"Build & Deploy"** section:

#### Build Command:
**CHANGE FROM:**
```
pip install -r requirements.txt
```

**TO:**
```
./build.sh
```

#### Start Command:
**CHANGE FROM:**
```
python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**TO:**
```
./start.sh
```

### Step 3: Save and Deploy
1. Click **"Save Changes"** at the bottom
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Watch the logs!

---

## 📋 What You Should See in Logs

### During Build:
```
📦 Installing Python dependencies...
...
🗂️ Collecting static files...
161 static files copied...
🗄️ Running database migrations...
Current migrations status:
payments
 [X] 0001_initial
 [X] 0002_initial
 [ ] 0003_payment_booking_fee_support  ← NOT APPLIED YET

Applying migrations...
Operations to perform:
  Apply all migrations: payments
Running migrations:
  Applying payments.0003_payment_booking_fee_support... OK  ← THIS IS KEY!
✅ Build completed successfully!
```

### During Start:
```
🚀 Starting application...
📍 Port: 10000
🌐 Host: 0.0.0.0
[INFO] Starting gunicorn...
[INFO] Listening at: http://0.0.0.0:10000
==> Your service is live 🎉
```

---

## 🎯 After Successful Deploy

Test the booking fee endpoint:
```bash
curl -X POST https://serviceman-backend.onrender.com/api/payments/initialize-booking-fee/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_emergency": false}'
```

### ✅ Expected Response:
```json
{
  "payment": {
    "id": 1,
    "payment_type": "INITIAL_BOOKING",
    "amount": "2000.00",
    "status": "PENDING",
    "is_emergency": false
  },
  "paystack_url": "https://checkout.paystack.com/...",
  "message": "Please complete payment of ₦2,000.00 to proceed"
}
```

---

## 🔴 Alternative: Use Single Command (If Scripts Don't Work)

If `./build.sh` and `./start.sh` don't work, use these single commands:

### Build Command:
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --verbosity 2
```

### Start Command:
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2 --timeout 120 --access-logfile - --error-logfile - --log-level info
```

---

## ❓ Why This Matters

The current setup:
- ❌ Runs migrations in START phase (should be in BUILD)
- ❌ No verbose output (can't see if migrations actually run)
- ❌ Migrations might fail silently
- ❌ Bookingfee feature doesn't work

The new setup:
- ✅ Migrations run in BUILD phase
- ✅ Shows exactly which migrations are applied
- ✅ Fails loudly if something goes wrong
- ✅ Booking fee feature works immediately

---

## 🚀 DO THIS NOW!

1. Go to Render Dashboard
2. Settings → Build & Deploy
3. Update Build Command to: `./build.sh`
4. Update Start Command to: `./start.sh`
5. Save Changes
6. Manual Deploy
7. Watch logs for "Applying payments.0003_payment_booking_fee_support... OK"
8. Test the endpoint!

**This should take 5-10 minutes total!** 🎯

