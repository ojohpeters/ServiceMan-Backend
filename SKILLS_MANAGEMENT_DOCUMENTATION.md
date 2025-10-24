# Skills Management System Documentation

This document provides comprehensive information about the skills management system, including how to create, manage, and assign skills to servicemen.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Skills Endpoints](#skills-endpoints)
3. [Serviceman Skills Management](#serviceman-skills-management)
4. [Frontend Integration](#frontend-integration)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## 🎯 Overview

The skills system allows:
- **Admins** to create and manage skills
- **Servicemen** to showcase their expertise
- **Clients** to see serviceman capabilities
- **Filtering** by skill categories

### Skill Categories:
- `TECHNICAL` - Technical skills (programming, electronics, etc.)
- `MANUAL` - Manual labor (construction, maintenance, etc.)
- `CREATIVE` - Creative skills (design, art, etc.)
- `PROFESSIONAL` - Professional services (consulting, etc.)
- `OTHER` - Other skills

---

## 🔧 Skills Endpoints

### 1. List All Skills

**Endpoint:** `GET /api/users/skills/`

**Description:** Returns all active skills, optionally filtered by category.

**Access:** Public (no authentication required)

**Query Parameters:**
- `category` (optional): Filter by skill category

**Response Format:**
```json
[
  {
    "id": 1,
    "name": "Plumbing Repair",
    "category": "MANUAL",
    "category_display": "Manual Labor",
    "description": "General plumbing repair and maintenance",
    "is_active": true,
    "created_at": "2025-10-21T10:30:00Z",
    "updated_at": "2025-10-21T10:30:00Z"
  },
  {
    "id": 2,
    "name": "Electrical Wiring",
    "category": "TECHNICAL",
    "category_display": "Technical",
    "description": "Electrical installation and repair",
    "is_active": true,
    "created_at": "2025-10-21T10:30:00Z",
    "updated_at": "2025-10-21T10:30:00Z"
  }
]
```

**Example Usage:**
```bash
# Get all skills
GET /api/users/skills/

# Get only technical skills
GET /api/users/skills/?category=TECHNICAL

# Get only manual labor skills
GET /api/users/skills/?category=MANUAL
```

### 2. Get Skill Details

**Endpoint:** `GET /api/users/skills/{id}/`

**Description:** Returns details of a specific skill.

**Access:** Public (no authentication required)

**Response Format:**
```json
{
  "id": 1,
  "name": "Plumbing Repair",
  "category": "MANUAL",
  "category_display": "Manual Labor",
  "description": "General plumbing repair and maintenance",
  "is_active": true,
  "created_at": "2025-10-21T10:30:00Z",
  "updated_at": "2025-10-21T10:30:00Z"
}
```

### 3. Create New Skill (Admin Only)

**Endpoint:** `POST /api/users/skills/create/`

**Description:** Creates a new skill. Only administrators can create skills.

**Access:** Admin only

**Request Body:**
```json
{
  "name": "Carpentry",
  "category": "MANUAL",
  "description": "Woodworking and carpentry services"
}
```

**Response Format:**
```json
{
  "id": 3,
  "name": "Carpentry",
  "category": "MANUAL",
  "category_display": "Manual Labor",
  "description": "Woodworking and carpentry services",
  "is_active": true,
  "created_at": "2025-10-21T10:30:00Z",
  "updated_at": "2025-10-21T10:30:00Z"
}
```

### 4. Update Skill (Admin Only)

**Endpoint:** `PATCH/PUT /api/users/skills/{id}/`

**Description:** Updates an existing skill. Only administrators can update skills.

**Access:** Admin only

**Request Body:**
```json
{
  "name": "Advanced Carpentry",
  "description": "Advanced woodworking and custom carpentry services"
}
```

### 5. Delete Skill (Admin Only)

**Endpoint:** `DELETE /api/users/skills/{id}/`

**Description:** Soft deletes a skill (marks as inactive). Only administrators can delete skills.

**Access:** Admin only

**Response Format:**
```json
{
  "detail": "Skill deleted successfully"
}
```

---

## 👷 Serviceman Skills Management

### Get Serviceman's Skills

**Endpoint:** `GET /api/users/serviceman-profile/`

**Description:** Returns serviceman profile including their skills.

**Access:** Serviceman (own profile) or Admin

**Response Format:**
```json
{
  "user": 123,
  "category": {
    "id": 1,
    "name": "Plumbing"
  },
  "skills": [
    {
      "id": 1,
      "name": "Plumbing Repair",
      "category": "MANUAL",
      "category_display": "Manual Labor",
      "description": "General plumbing repair and maintenance",
      "is_active": true
    },
    {
      "id": 2,
      "name": "Pipe Installation",
      "category": "MANUAL",
      "category_display": "Manual Labor",
      "description": "Installation of pipes and fixtures",
      "is_active": true
    }
  ],
  "skill_ids": [1, 2],
  "rating": "4.50",
  "total_jobs_completed": 25,
  "bio": "Experienced plumber with 10 years of experience",
  "years_of_experience": 10,
  "phone_number": "+1234567890",
  "is_available": true,
  "active_jobs_count": 2,
  "availability_status": "Available",
  "is_approved": true,
  "approved_by": "admin_user",
  "approved_at": "2025-10-21T10:30:00Z",
  "created_at": "2025-10-21T10:30:00Z",
  "updated_at": "2025-10-21T10:30:00Z"
}
```

### Update Serviceman's Skills

**Endpoint:** `PATCH /api/users/serviceman-profile/`

**Description:** Updates serviceman profile including skills assignment.

**Access:** Serviceman (own profile) or Admin

**Request Body:**
```json
{
  "skill_ids": [1, 2, 3],
  "bio": "Updated bio with new skills",
  "years_of_experience": 12
}
```

**Response Format:**
```json
{
  "user": 123,
  "skills": [
    {
      "id": 1,
      "name": "Plumbing Repair",
      "category": "MANUAL",
      "category_display": "Manual Labor"
    },
    {
      "id": 2,
      "name": "Pipe Installation",
      "category": "MANUAL",
      "category_display": "Manual Labor"
    },
    {
      "id": 3,
      "name": "Emergency Repairs",
      "category": "MANUAL",
      "category_display": "Manual Labor"
    }
  ],
  "skill_ids": [1, 2, 3],
  "bio": "Updated bio with new skills",
  "years_of_experience": 12
}
```

---

## 🎨 Frontend Integration

### Skills Service Class

```javascript
class SkillsService {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  // Get all skills
  async getAllSkills(category = null) {
    const params = category ? `?category=${category}` : '';
    const response = await fetch(`${this.baseURL}/users/skills/${params}`, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  // Get skill by ID
  async getSkill(skillId) {
    const response = await fetch(`${this.baseURL}/users/skills/${skillId}/`, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  // Create skill (Admin only)
  async createSkill(skillData) {
    const response = await fetch(`${this.baseURL}/users/skills/create/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(skillData)
    });
    return response.json();
  }

  // Update skill (Admin only)
  async updateSkill(skillId, skillData) {
    const response = await fetch(`${this.baseURL}/users/skills/${skillId}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(skillData)
    });
    return response.json();
  }

  // Delete skill (Admin only)
  async deleteSkill(skillId) {
    const response = await fetch(`${this.baseURL}/users/skills/${skillId}/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  // Get serviceman's skills
  async getServicemanSkills() {
    const response = await fetch(`${this.baseURL}/users/serviceman-profile/`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    return response.json();
  }

  // Update serviceman's skills
  async updateServicemanSkills(skillIds) {
    const response = await fetch(`${this.baseURL}/users/serviceman-profile/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ skill_ids: skillIds })
    });
    return response.json();
  }
}
```

### React Hook for Skills

```javascript
import { useState, useEffect } from 'react';

function useSkills(token, category = null) {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        setLoading(true);
        const skillsService = new SkillsService('/api', token);
        const data = await skillsService.getAllSkills(category);
        setSkills(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSkills();
  }, [token, category]);

  return { skills, loading, error };
}

// Usage example
function SkillsList({ category }) {
  const { skills, loading, error } = useSkills(null, category); // No token needed for public endpoint

  if (loading) return <div>Loading skills...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Skills</h2>
      {skills.map(skill => (
        <div key={skill.id} className="skill-item">
          <h3>{skill.name}</h3>
          <p>{skill.category_display}</p>
          <p>{skill.description}</p>
        </div>
      ))}
    </div>
  );
}
```

### Skills Selection Component

```javascript
import React, { useState, useEffect } from 'react';

function SkillsSelector({ selectedSkills, onSkillsChange, category = null }) {
  const [allSkills, setAllSkills] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const response = await fetch(`/api/users/skills/${category ? `?category=${category}` : ''}`);
        const skills = await response.json();
        setAllSkills(skills);
      } catch (error) {
        console.error('Error fetching skills:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSkills();
  }, [category]);

  const handleSkillToggle = (skillId) => {
    const newSkills = selectedSkills.includes(skillId)
      ? selectedSkills.filter(id => id !== skillId)
      : [...selectedSkills, skillId];
    onSkillsChange(newSkills);
  };

  if (loading) return <div>Loading skills...</div>;

  return (
    <div className="skills-selector">
      <h3>Select Your Skills</h3>
      <div className="skills-grid">
        {allSkills.map(skill => (
          <label key={skill.id} className="skill-checkbox">
            <input
              type="checkbox"
              checked={selectedSkills.includes(skill.id)}
              onChange={() => handleSkillToggle(skill.id)}
            />
            <span className="skill-name">{skill.name}</span>
            <span className="skill-category">({skill.category_display})</span>
          </label>
        ))}
      </div>
    </div>
  );
}

// Usage example
function ServicemanProfileForm() {
  const [selectedSkills, setSelectedSkills] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/users/serviceman-profile/', {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ skill_ids: selectedSkills })
      });
      
      if (response.ok) {
        alert('Skills updated successfully!');
      }
    } catch (error) {
      console.error('Error updating skills:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <SkillsSelector
        selectedSkills={selectedSkills}
        onSkillsChange={setSelectedSkills}
        category="MANUAL" // Filter by category
      />
      <button type="submit">Update Skills</button>
    </form>
  );
}
```

---

## ❌ Error Handling

### Common Error Responses

**503 Service Unavailable (Migration Required):**
```json
{
  "error": "Database migration required",
  "detail": "The skills system requires database migrations to be run. Please contact the administrator to run: python manage.py migrate users"
}
```

**403 Forbidden (Admin Only):**
```json
{
  "detail": "Only administrators can create skills"
}
```

**400 Bad Request (Validation Error):**
```json
{
  "name": ["This field is required."],
  "category": ["Select a valid choice. OTHER is not one of the available choices."]
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

---

## 📝 Examples

### Complete Skills Management Flow

```javascript
// 1. Admin creates skills
const adminService = new SkillsService('/api', adminToken);

await adminService.createSkill({
  name: "Plumbing Repair",
  category: "MANUAL",
  description: "General plumbing repair and maintenance"
});

await adminService.createSkill({
  name: "Electrical Wiring",
  category: "TECHNICAL",
  description: "Electrical installation and repair"
});

// 2. Serviceman selects skills during registration/profile update
const servicemanService = new SkillsService('/api', servicemanToken);

// Get all available skills
const allSkills = await servicemanService.getAllSkills();

// Get skills by category
const technicalSkills = await servicemanService.getAllSkills('TECHNICAL');
const manualSkills = await servicemanService.getAllSkills('MANUAL');

// Update serviceman's skills
await servicemanService.updateServicemanSkills([1, 2, 3]);

// 3. Client views serviceman's skills
const servicemanProfile = await servicemanService.getServicemanSkills();
console.log('Serviceman skills:', servicemanProfile.skills);
```

### Skills Filtering and Search

```javascript
// Filter skills by category
const categories = ['TECHNICAL', 'MANUAL', 'CREATIVE', 'PROFESSIONAL', 'OTHER'];

categories.forEach(async (category) => {
  const skills = await skillsService.getAllSkills(category);
  console.log(`${category} skills:`, skills);
});

// Search skills by name (frontend filtering)
const searchSkills = (skills, searchTerm) => {
  return skills.filter(skill => 
    skill.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    skill.description.toLowerCase().includes(searchTerm.toLowerCase())
  );
};
```

---

## 🚀 Quick Reference

| Endpoint | Method | Description | Access |
|----------|--------|-------------|---------|
| `/api/users/skills/` | GET | List all skills | Public |
| `/api/users/skills/{id}/` | GET | Get skill details | Public |
| `/api/users/skills/create/` | POST | Create new skill | Admin only |
| `/api/users/skills/{id}/` | PATCH/PUT | Update skill | Admin only |
| `/api/users/skills/{id}/` | DELETE | Delete skill | Admin only |
| `/api/users/serviceman-profile/` | GET | Get serviceman skills | Owner/Admin |
| `/api/users/serviceman-profile/` | PATCH | Update serviceman skills | Owner/Admin |

---

## 🔧 Database Setup

If you encounter 503 errors, the skills table needs to be created:

```bash
# Run migrations to create skills table
python manage.py migrate users

# This will create:
# - users_skill table
# - users_servicemanprofile_skills many-to-many table
```

---

## 📞 Support

For questions or issues with the skills system, please contact the development team or check the main API documentation at `/api/docs/`.

---

**Last Updated:** October 24, 2025  
**Version:** 1.0.0