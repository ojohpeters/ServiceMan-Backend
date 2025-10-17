# API Documentation Access Guide

## 📚 Interactive API Documentation

The ServiceMan Platform API includes comprehensive, interactive documentation powered by **DRF Spectacular (Swagger/OpenAPI)**.

## 🌐 Access Points

### 1. Swagger UI (Interactive)
```
http://localhost:8000/api/docs/
```

**Features:**
- Interactive API browser
- Try-it-out functionality
- Request/response examples
- Authentication support
- Real-time API testing

### 2. ReDoc (Alternative View)
```
http://localhost:8000/api/redoc/
```

**Features:**
- Clean, responsive documentation
- Three-panel layout
- Search functionality
- Code samples
- Mobile-friendly

### 3. OpenAPI Schema (JSON)
```
http://localhost:8000/api/schema/
```

**Use Cases:**
- Generate client SDKs
- Import into Postman
- API testing tools
- Custom documentation

## 🚀 Using Swagger UI

### Step 1: Access the Documentation
1. Start your development server: `python manage.py runserver`
2. Open browser and navigate to: `http://localhost:8000/api/docs/`

### Step 2: Authenticate
For endpoints requiring authentication:

1. Click the **"Authorize"** button (lock icon) at the top right
2. Enter your JWT token in the format: `Bearer <your_token>`
3. Click **"Authorize"**
4. Click **"Close"**

### Step 3: Test Endpoints
1. Click on any endpoint to expand it
2. Click **"Try it out"**
3. Fill in required parameters
4. Click **"Execute"**
5. View the response below

## 🔐 Authentication

### Getting a JWT Token

**Step 1: Register or Login**
```bash
# Register a new user
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "user_type": "CLIENT"
  }'

# Get JWT token
curl -X POST http://localhost:8000/api/users/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Step 2: Use Token in Requests**
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## 📋 API Endpoints Overview

### Authentication & Registration
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/register/` | Register new user | No |
| POST | `/api/users/token/` | Get JWT token | No |
| POST | `/api/users/token/refresh/` | Refresh JWT token | No |
| GET | `/api/users/verify-email/` | Verify email address | No |
| POST | `/api/users/resend-verification-email/` | Resend verification email | No |

### Password Reset
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/password-reset/` | Request password reset | No |
| POST | `/api/users/password-reset-confirm/` | Confirm password reset | No |

### User Profiles
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/me/` | Get current user info | Yes |
| GET/PATCH | `/api/users/client-profile/` | Get/Update client profile | Yes (Client) |
| GET/PATCH | `/api/users/serviceman-profile/` | Get/Update serviceman profile | Yes (Serviceman) |
| GET | `/api/users/servicemen/{id}/` | Get public serviceman profile | No |

### Skills Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users/skills/` | List all skills | No |
| GET | `/api/users/skills/{id}/` | Get skill details | No |
| POST | `/api/users/skills/create/` | Create new skill | Yes (Admin) |
| PUT/PATCH | `/api/users/skills/{id}/update/` | Update skill | Yes (Admin) |
| DELETE | `/api/users/skills/{id}/delete/` | Delete skill (soft) | Yes (Admin) |
| GET | `/api/users/servicemen/{id}/skills/` | Get serviceman skills | No |
| POST | `/api/users/servicemen/{id}/skills/` | Add skills to serviceman | Yes |
| DELETE | `/api/users/servicemen/{id}/skills/` | Remove skills from serviceman | Yes |

### Admin Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/admin/create/` | Create new admin user | Yes (Admin) |

## 🎯 Common Use Cases

### Use Case 1: Register and Verify Email
```javascript
// 1. Register
const registerResponse = await fetch('/api/users/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'newuser',
    email: 'user@example.com',
    password: 'SecurePass123!',
    user_type: 'CLIENT'
  })
});

// 2. User receives email with verification link
// 3. User clicks link (handled by frontend routing)
// 4. Frontend calls verify endpoint
const verifyResponse = await fetch(
  '/api/users/verify-email/?uid=5&token=abc123...',
  { method: 'GET' }
);
```

### Use Case 2: Login and Access Protected Resource
```javascript
// 1. Login
const loginResponse = await fetch('/api/users/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'newuser',
    password: 'SecurePass123!'
  })
});

const { access } = await loginResponse.json();

// 2. Access protected endpoint
const profileResponse = await fetch('/api/users/me/', {
  headers: { 'Authorization': `Bearer ${access}` }
});

const user = await profileResponse.json();
```

### Use Case 3: Serviceman Profile with Skills
```javascript
// 1. Get skills
const skillsResponse = await fetch('/api/users/skills/?category=TECHNICAL');
const skills = await skillsResponse.json();

// 2. Update profile with skills
const profileResponse = await fetch('/api/users/serviceman-profile/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    bio: 'Experienced electrician',
    years_of_experience: 10,
    skill_ids: [1, 5, 8]
  })
});
```

### Use Case 4: Admin Creates New Skill
```javascript
// Admin creates new skill
const skillResponse = await fetch('/api/users/skills/create/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Solar Panel Installation',
    category: 'TECHNICAL',
    description: 'Installation and maintenance of solar panels'
  })
});

const newSkill = await skillResponse.json();
```

## 📦 Importing into Postman

### Method 1: Direct Import
1. Open Postman
2. Click **Import** button
3. Select **Link** tab
4. Enter: `http://localhost:8000/api/schema/`
5. Click **Continue** and **Import**

### Method 2: Download and Import
1. Download schema: `curl http://localhost:8000/api/schema/ > schema.json`
2. In Postman, click **Import**
3. Select **File** tab
4. Choose the downloaded `schema.json`
5. Click **Import**

### Setting Up Environment in Postman
1. Create new environment: **ServiceMan Dev**
2. Add variables:
   - `base_url`: `http://localhost:8000`
   - `access_token`: (will be set after login)
3. Update requests to use `{{base_url}}`
4. Add authorization: `Bearer {{access_token}}`

## 🔍 Searching Documentation

### In Swagger UI
- Use browser's Find function (Ctrl+F / Cmd+F)
- Look for specific endpoints or keywords

### In ReDoc
- Click search icon at top
- Enter search term
- Navigate through results

## 🎨 Customizing Documentation

### Adding Tags to Views
```python
class SkillListView(generics.ListAPIView):
    """
    List all skills.
    
    Tags: Skills
    """
    # ... view implementation
```

### Adding Examples
```python
from drf_spectacular.utils import extend_schema, OpenApiExample

class RegisterView(generics.CreateAPIView):
    @extend_schema(
        examples=[
            OpenApiExample(
                'Client Registration',
                value={
                    'username': 'john_client',
                    'email': 'john@example.com',
                    'password': 'SecurePass123!',
                    'user_type': 'CLIENT'
                }
            ),
        ]
    )
    def post(self, request):
        # ... implementation
```

## 🐛 Troubleshooting

### Documentation Not Loading
1. Ensure `drf-spectacular` is installed: `pip install drf-spectacular`
2. Check `INSTALLED_APPS` includes `'drf_spectacular'`
3. Verify URLs are properly configured
4. Clear browser cache

### Endpoints Not Showing
1. Ensure views have proper docstrings
2. Check URL patterns are registered
3. Verify `DEFAULT_SCHEMA_CLASS` is set in settings
4. Restart development server

### Authentication Not Working
1. Verify token format: `Bearer <token>`
2. Check token hasn't expired
3. Ensure Authorization header is set correctly
4. Try refreshing the token

## 📱 Mobile Access

The documentation is fully responsive and works on mobile devices:

1. Access from mobile browser
2. Use same URLs as desktop
3. Navigate using mobile-optimized UI
4. Test endpoints directly from mobile

## 🌐 Production Deployment

### Security Considerations
```python
# In production settings
SPECTACULAR_SETTINGS = {
    # ... other settings
    'SERVE_INCLUDE_SCHEMA': False,  # Disable if you don't want to expose schema
}

# Or remove documentation URLs entirely in production
if not DEBUG:
    urlpatterns = [
        # ... app URLs only
    ]
```

### External Documentation Hosting
Consider hosting documentation separately:
1. Generate static docs: `python manage.py spectacular --file schema.yml`
2. Use tools like Stoplight, Swagger Hub, or ReadTheDocs
3. Keep internal API docs for development only

## 📚 Additional Resources

- **DRF Spectacular Docs**: https://drf-spectacular.readthedocs.io/
- **OpenAPI Specification**: https://swagger.io/specification/
- **Swagger UI**: https://swagger.io/tools/swagger-ui/
- **ReDoc**: https://github.com/Redocly/redoc

## 📞 Support

For documentation issues:
- **Email**: support@servicemanplatform.com
- **GitHub**: [Report documentation issues]

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Maintained by**: ServiceMan Platform Team


