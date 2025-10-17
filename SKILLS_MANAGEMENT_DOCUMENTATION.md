# Skills Management System - Complete Documentation

## 📋 Overview

The ServiceMan Platform now includes a comprehensive skills management system that allows servicemen to showcase their expertise and enables better matching between clients and service providers.

## ✨ Features Implemented

### 1. Skill Model
- **Categorized Skills**: Skills organized by category (Technical, Manual, Creative, Professional, Other)
- **Many-to-Many Relationship**: Servicemen can have multiple skills
- **Soft Deletion**: Skills marked as inactive instead of deleted
- **Timestamps**: Track creation and update times

### 2. Skills During Registration
- Servicemen can add skills when creating their account
- Skills validated against active skills in database
- Automatic profile association

### 3. Profile Management
- View skills on serviceman profiles
- Add/remove skills after registration
- Update skills via profile endpoint

### 4. Admin Control
- Only admins can create new skills
- Admin interface with bulk actions
- Track skill usage (number of servicemen per skill)

## 📁 Files Created/Modified

```
apps/users/
├── models.py              # Added Skill model + many-to-many relationship
├── serializers.py         # Added skill serializers
├── views.py               # Added 6 skills management views
├── urls.py                # Added skills URL routes
└── admin.py               # Enhanced admin interface
```

## 🗄️ Database Schema

### Skill Model
```python
class Skill(models.Model):
    name = CharField(max_length=100, unique=True)
    category = CharField(choices=CATEGORY_CHOICES)
    description = TextField(blank=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Skill Categories
- `TECHNICAL`: Technical skills (e.g., Electrical Work, Plumbing)
- `MANUAL`: Manual labor skills (e.g., Carpentry, Masonry)
- `CREATIVE`: Creative skills (e.g., Interior Design, Landscaping)
- `PROFESSIONAL`: Professional services (e.g., Consulting, Training)
- `OTHER`: Other skills

### ServicemanProfile Relationship
```python
class ServicemanProfile(models.Model):
    # ... other fields
    skills = ManyToManyField(Skill, related_name='servicemen', blank=True)
```

## 🚀 API Endpoints

### 1. List All Skills (Public)
```http
GET /api/users/skills/
GET /api/users/skills/?category=TECHNICAL
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Electrical Wiring",
    "category": "TECHNICAL",
    "description": "Installation and repair of electrical systems",
    "is_active": true,
    "created_at": "2025-10-01T10:00:00Z",
    "updated_at": "2025-10-01T10:00:00Z"
  },
  {
    "id": 2,
    "name": "Plumbing",
    "category": "TECHNICAL",
    "description": "Installation and repair of water systems",
    "is_active": true,
    "created_at": "2025-10-01T10:05:00Z",
    "updated_at": "2025-10-01T10:05:00Z"
  }
]
```

### 2. Get Skill Details (Public)
```http
GET /api/users/skills/{skill_id}/
```

**Response:**
```json
{
  "id": 1,
  "name": "Electrical Wiring",
  "category": "TECHNICAL",
  "description": "Installation and repair of electrical systems",
  "is_active": true,
  "created_at": "2025-10-01T10:00:00Z",
  "updated_at": "2025-10-01T10:00:00Z"
}
```

### 3. Create Skill (Admin Only)
```http
POST /api/users/skills/create/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Smart Home Installation",
  "category": "TECHNICAL",
  "description": "Installation and configuration of smart home devices"
}
```

**Response:**
```json
{
  "id": 15,
  "name": "Smart Home Installation",
  "category": "TECHNICAL",
  "description": "Installation and configuration of smart home devices",
  "is_active": true,
  "created_at": "2025-10-17T12:00:00Z",
  "updated_at": "2025-10-17T12:00:00Z"
}
```

### 4. Update Skill (Admin Only)
```http
PUT /api/users/skills/{skill_id}/update/
PATCH /api/users/skills/{skill_id}/update/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "name": "Advanced Electrical Wiring",
  "description": "Updated description"
}
```

### 5. Delete Skill (Admin Only - Soft Delete)
```http
DELETE /api/users/skills/{skill_id}/delete/
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "detail": "Skill deactivated successfully."
}
```

**Note**: This is a soft delete. The skill is marked as `is_active=False` instead of being permanently deleted.

### 6. Get Serviceman Skills (Public)
```http
GET /api/users/servicemen/{serviceman_id}/skills/
```

**Response:**
```json
{
  "serviceman": {
    "id": 5,
    "username": "john_electrician",
    "full_name": "John Smith"
  },
  "skills": [
    {
      "id": 1,
      "name": "Electrical Wiring",
      "category": "TECHNICAL",
      "description": "Installation and repair of electrical systems",
      "is_active": true,
      "created_at": "2025-10-01T10:00:00Z",
      "updated_at": "2025-10-01T10:00:00Z"
    },
    {
      "id": 15,
      "name": "Smart Home Installation",
      "category": "TECHNICAL",
      "description": "Installation and configuration of smart home devices",
      "is_active": true,
      "created_at": "2025-10-17T12:00:00Z",
      "updated_at": "2025-10-17T12:00:00Z"
    }
  ]
}
```

### 7. Add Skills to Serviceman (Serviceman or Admin)
```http
POST /api/users/servicemen/{serviceman_id}/skills/
Authorization: Bearer <token>
Content-Type: application/json

{
  "skill_ids": [1, 15, 23]
}
```

**Response:**
```json
{
  "message": "Added 3 skill(s) successfully.",
  "skills": [
    { "id": 1, "name": "Electrical Wiring", ... },
    { "id": 15, "name": "Smart Home Installation", ... },
    { "id": 23, "name": "HVAC Systems", ... }
  ]
}
```

### 8. Remove Skills from Serviceman (Serviceman or Admin)
```http
DELETE /api/users/servicemen/{serviceman_id}/skills/
Authorization: Bearer <token>
Content-Type: application/json

{
  "skill_ids": [15]
}
```

**Response:**
```json
{
  "message": "Removed 1 skill(s) successfully.",
  "skills": [
    { "id": 1, "name": "Electrical Wiring", ... },
    { "id": 23, "name": "HVAC Systems", ... }
  ]
}
```

## 💼 Registration with Skills

### Register Serviceman with Skills
```http
POST /api/users/register/
Content-Type: application/json

{
  "username": "mike_plumber",
  "email": "mike@example.com",
  "password": "SecurePass123!",
  "user_type": "SERVICEMAN",
  "skill_ids": [2, 5, 8]
}
```

**Response:**
```json
{
  "id": 10,
  "username": "mike_plumber",
  "email": "mike@example.com",
  "user_type": "SERVICEMAN",
  "is_email_verified": false
}
```

**Note**: Skills are automatically associated with the serviceman profile.

## 🎯 Profile Management

### Update Serviceman Profile with Skills
```http
PUT /api/users/serviceman-profile/
PATCH /api/users/serviceman-profile/
Authorization: Bearer <serviceman_token>
Content-Type: application/json

{
  "bio": "Experienced plumber with 10+ years",
  "years_of_experience": 10,
  "phone_number": "+2348012345678",
  "skill_ids": [2, 5, 8, 12]
}
```

**Response:**
```json
{
  "user": 10,
  "category": 3,
  "skills": [
    { "id": 2, "name": "Plumbing", ... },
    { "id": 5, "name": "Pipe Fitting", ... },
    { "id": 8, "name": "Drain Cleaning", ... },
    { "id": 12, "name": "Water Heater Repair", ... }
  ],
  "rating": 4.7,
  "total_jobs_completed": 45,
  "bio": "Experienced plumber with 10+ years",
  "years_of_experience": 10,
  "phone_number": "+2348012345678",
  "is_available": true,
  "created_at": "2025-10-15T08:00:00Z",
  "updated_at": "2025-10-17T14:30:00Z"
}
```

## 🔧 Usage Examples

### Frontend Integration (React/JavaScript)

#### List Skills by Category
```javascript
async function getSkillsByCategory(category) {
  const response = await fetch(
    `/api/users/skills/?category=${category}`
  );
  const skills = await response.json();
  return skills;
}

// Usage
const technicalSkills = await getSkillsByCategory('TECHNICAL');
```

#### Add Skills to Serviceman Profile
```javascript
async function addSkills(servicemanId, skillIds, token) {
  const response = await fetch(
    `/api/users/servicemen/${servicemanId}/skills/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ skill_ids: skillIds }),
    }
  );
  
  const data = await response.json();
  return data;
}

// Usage
const result = await addSkills(5, [1, 15, 23], userToken);
console.log(result.message); // "Added 3 skill(s) successfully."
```

#### Display Serviceman Skills
```javascript
async function getServicemanSkills(servicemanId) {
  const response = await fetch(
    `/api/users/servicemen/${servicemanId}/skills/`
  );
  const data = await response.json();
  return data.skills;
}

// Usage in React component
function ServicemanProfile({ servicemanId }) {
  const [skills, setSkills] = useState([]);
  
  useEffect(() => {
    getServicemanSkills(servicemanId).then(setSkills);
  }, [servicemanId]);
  
  return (
    <div>
      <h3>Skills:</h3>
      <ul>
        {skills.map(skill => (
          <li key={skill.id}>
            <strong>{skill.name}</strong> - {skill.category}
            <p>{skill.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 👑 Admin Interface

### Admin Features
1. **Skill Management**
   - Create, update, and soft-delete skills
   - Bulk activate/deactivate skills
   - View skill usage statistics

2. **Enhanced Serviceman Admin**
   - Filter servicemen by skills
   - Horizontal filter widget for easy skill selection
   - View skill count per serviceman

3. **Statistics**
   - Number of servicemen per skill
   - Active vs inactive skills
   - Skill category distribution

### Accessing Admin Interface
```
http://localhost:8000/admin/users/skill/
http://localhost:8000/admin/users/servicemanprofile/
```

## 🔒 Permissions

### Skill Creation/Management
- **Create**: Admin only
- **Update**: Admin only
- **Delete (Soft)**: Admin only
- **List**: Public (no authentication required)
- **Detail**: Public (no authentication required)

### Serviceman Skills
- **View**: Public
- **Add**: Serviceman themselves or Admin
- **Remove**: Serviceman themselves or Admin

## 🐛 Troubleshooting

### Common Issues

**Skills not appearing in profile**
- Ensure skills are marked as `is_active=True`
- Verify skill IDs exist in database
- Check serviceman profile is created

**Cannot add skills**
- Verify authentication token is valid
- Ensure user is the serviceman or an admin
- Check skill IDs are valid and active

**Skills validation errors during registration**
- Ensure all skill IDs exist in database
- Verify skills are active
- Check skills array format is correct

## 📊 Database Migration

After implementing skills system, run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Sample Data Creation

Create sample skills via admin interface or Django shell:

```python
python manage.py shell

from apps.users.models import Skill

# Create technical skills
Skill.objects.create(
    name="Electrical Wiring",
    category="TECHNICAL",
    description="Installation and repair of electrical systems"
)

Skill.objects.create(
    name="Plumbing",
    category="TECHNICAL",
    description="Installation and repair of water systems"
)

# Create manual skills
Skill.objects.create(
    name="Carpentry",
    category="MANUAL",
    description="Wood working and furniture making"
)

# ... add more skills
```

## 🚀 Future Enhancements

### Possible Improvements
- [ ] Skill verification/certification system
- [ ] Skill endorsements from clients
- [ ] Skill-based search and filtering
- [ ] Skill levels (Beginner, Intermediate, Expert)
- [ ] Skill tags and synonyms
- [ ] Skill recommendations based on category
- [ ] Skill trends and analytics

## 📞 Support

For issues or questions:
- **Email**: support@servicemanplatform.com
- **API Documentation**: http://localhost:8000/api/docs/

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Maintained by**: ServiceMan Platform Team


