# 🔧 ServiceMan Backend API

Production-grade Django REST API for connecting clients with skilled service providers.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-Proprietary-yellow.svg)]()

---

## 📚 Documentation

### **👉 [Complete Frontend API Documentation](FRONTEND_API_DOCUMENTATION.md)**

**This is the ONLY documentation file you need!** It includes everything:

- ✅ All API endpoints with request/response examples
- ✅ Authentication & JWT token management
- ✅ Complete service request workflow (8 steps)
- ✅ Paystack payment integration & callback setup
- ✅ Real-time notifications system
- ✅ Skills & serviceman management
- ✅ Error handling best practices
- ✅ React/Vue.js code examples
- ✅ Timezone handling for notifications
- ✅ Common scenarios & use cases

### **For Deployment:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**Note:** All other guide files have been consolidated into the main documentation above.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ (3.11 or 3.12 recommended)
- PostgreSQL 12+
- Redis (for Celery tasks)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ServiceMan-Backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your configuration
```

Required environment variables:
```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/serviceman_db
PAYSTACK_SECRET_KEY=your-paystack-secret-key
PAYSTACK_PUBLIC_KEY=your-paystack-public-key
FRONTEND_URL=http://localhost:3000
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create admin user**
```bash
python manage.py createsuperuser
```

7. **Start development server**
```bash
python manage.py runserver
```

8. **Start Celery worker (in another terminal)**
```bash
celery -A config worker -l info
```

The API will be available at `http://localhost:8000/api/`

---

## 🎯 Key Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (CLIENT, SERVICEMAN, ADMIN)
- Email verification system
- Password reset functionality

### Service Request Management
- Professional 8-step workflow
- Real-time status tracking
- Admin-managed assignments
- Emergency service support

### Payment Integration
- Paystack payment gateway
- Booking fee system (₦2,000 / ₦5,000)
- Final payment processing
- Payment history tracking

### Serviceman Management
- Skills-based categorization
- Admin approval workflow
- Availability tracking
- Job history & statistics
- Rating & review system

### Notifications
- In-app notification system
- Status transition notifications
- Role-specific notifications
- Unread count tracking

### Admin Features
- Serviceman approval/rejection
- Service request assignment
- Price finalization
- Work authorization
- Complete workflow oversight

---

## 📡 API Endpoints Overview

### Authentication
- `POST /api/users/register/` - Register new user
- `POST /api/users/login/` - Login
- `POST /api/users/token/refresh/` - Refresh access token
- `GET /api/users/verify-email/` - Verify email

### User Management
- `GET /api/users/profile/` - Get current user profile
- `GET /api/users/servicemen/` - List all servicemen (with filters)
- `PATCH /api/users/serviceman-profile/` - Update serviceman profile
- `PATCH /api/users/client-profile/` - Update client profile

### Service Requests
- `GET /api/services/service-requests/` - List service requests
- `POST /api/services/service-requests/` - Create service request
- `POST /api/services/service-requests/{id}/assign/` - Assign serviceman (Admin)
- `POST /api/services/service-requests/{id}/submit-estimate/` - Submit estimate (Serviceman)
- `POST /api/services/service-requests/{id}/finalize-price/` - Finalize price (Admin)
- `POST /api/services/service-requests/{id}/authorize-work/` - Authorize work (Admin)
- `POST /api/services/service-requests/{id}/complete-job/` - Complete job (Serviceman)
- `POST /api/services/service-requests/{id}/submit-review/` - Submit review (Client)

### Payments
- `POST /api/payments/initialize-booking-fee/` - Initialize booking fee
- `POST /api/payments/initialize/` - Initialize final payment
- `GET /api/payments/verify/` - Verify payment
- `GET /api/payments/history/` - Payment history

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/mark-read/` - Mark as read
- `POST /api/notifications/mark-all-read/` - Mark all as read

### Admin
- `GET /api/users/admin/pending-servicemen/` - Pending serviceman applications
- `POST /api/users/admin/approve-serviceman/` - Approve serviceman
- `POST /api/users/admin/reject-serviceman/` - Reject serviceman

**📖 For complete endpoint details, see [FRONTEND_API_DOCUMENTATION.md](FRONTEND_API_DOCUMENTATION.md)**

---

## 🏗️ Project Structure

```
ServiceMan-Backend/
├── apps/
│   ├── users/          # User management, authentication, profiles
│   ├── services/       # Service categories, requests, workflow
│   ├── payments/       # Paystack integration, payment processing
│   ├── notifications/  # Notification system
│   ├── ratings/        # Rating & review system
│   └── negotiations/   # Price negotiation (future)
├── config/
│   ├── settings/       # Django settings (base, production)
│   ├── urls.py         # Main URL configuration
│   └── celery.py       # Celery configuration
├── templates/
│   └── emails/         # Email templates
├── requirements.txt    # Python dependencies
├── manage.py           # Django management script
├── build.sh            # Render build script
├── start.sh            # Render start script
└── render.yaml         # Render deployment config
```

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users
python manage.py test apps.services

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

---

## 🔧 Development Tools

### API Documentation
- **Swagger UI:** `http://localhost:8000/api/schema/swagger-ui/`
- **ReDoc:** `http://localhost:8000/api/schema/redoc/`
- **OpenAPI Schema:** `http://localhost:8000/api/schema/`

### Admin Panel
- Access Django admin at `http://localhost:8000/admin/`

### Database Management
```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Create test data
python manage.py create_test_servicemen
```

---

## 🚢 Deployment

The project is configured for deployment on **Render.com**

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

Key deployment files:
- `render.yaml` - Render service configuration
- `build.sh` - Build script (installs deps, runs migrations)
- `start.sh` - Start script (runs Gunicorn)

---

## 🔐 Environment Variables

### Required Variables
```env
SECRET_KEY=              # Django secret key
DATABASE_URL=            # PostgreSQL connection string
PAYSTACK_SECRET_KEY=     # Paystack secret key
PAYSTACK_PUBLIC_KEY=     # Paystack public key
FRONTEND_URL=            # Frontend URL (for CORS)
```

### Optional Variables
```env
DEBUG=False              # Debug mode (False in production)
ALLOWED_HOSTS=           # Comma-separated allowed hosts
REDIS_URL=               # Redis connection URL (for Celery)
SENTRY_DSN=              # Sentry error tracking
EMAIL_BACKEND=           # Email backend configuration
EMAIL_HOST=              # SMTP host
EMAIL_PORT=              # SMTP port
EMAIL_HOST_USER=         # SMTP username
EMAIL_HOST_PASSWORD=     # SMTP password
```

---

## 📊 Tech Stack

- **Framework:** Django 4.2 + Django REST Framework 3.16
- **Database:** PostgreSQL
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Task Queue:** Celery + Redis
- **Payment Gateway:** Paystack
- **API Docs:** drf-spectacular (OpenAPI 3.0)
- **Monitoring:** Sentry
- **Server:** Gunicorn + Whitenoise

---

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

---

## 📄 License

This project is proprietary and confidential. Unauthorized use is prohibited.

---

## 📞 Support

For questions or issues:
- Check the [API Documentation](FRONTEND_API_DOCUMENTATION.md)
- Review the [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Contact the development team

---

## 🎯 Roadmap

- [x] User authentication & authorization
- [x] Service request workflow
- [x] Paystack payment integration
- [x] Notification system
- [x] Skills management
- [x] Serviceman approval system
- [x] Admin dashboard endpoints
- [x] Query optimization (N+1 fix)
- [ ] WebSocket support for real-time updates
- [ ] Mobile app API enhancements
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

---

**Built with ❤️ by the ServiceMan Team**
