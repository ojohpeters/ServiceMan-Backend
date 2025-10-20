# 👑 Admin Category Assignment - Complete Guide

## ✅ NEW! 3 Admin Endpoints for Category Management

---

## 📋 Overview

Admins can now:
- ✅ Assign serviceman to a category
- ✅ Reassign serviceman to different category
- ✅ Bulk assign multiple servicemen
- ✅ View servicemen grouped by category
- ✅ See unassigned servicemen

---

## 🚀 API Endpoints

### 1. Assign Serviceman to Category

**Endpoint**: `POST /api/users/admin/assign-category/`

**Purpose**: Assign or reassign a single serviceman to a category

**Auth**: Admin only

**Request Body:**
```json
{
  "serviceman_id": 5,
  "category_id": 2
}
```

**To Remove Category** (set to null):
```json
{
  "serviceman_id": 5,
  "category_id": null
}
```

**Response:**
```json
{
  "detail": "Category assignment updated successfully",
  "serviceman": {
    "id": 5,
    "username": "john_electrician",
    "full_name": "John Smith"
  },
  "previous_category": {
    "id": 1,
    "name": "Plumbing"
  },
  "new_category": {
    "id": 2,
    "name": "Electrical"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/users/admin/assign-category/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceman_id": 5,
    "category_id": 2
  }'
```

---

### 2. Bulk Assign Category

**Endpoint**: `POST /api/users/admin/bulk-assign-category/`

**Purpose**: Assign multiple servicemen to the same category at once

**Auth**: Admin only

**Request Body:**
```json
{
  "serviceman_ids": [5, 6, 7, 8, 9],
  "category_id": 2
}
```

**Response:**
```json
{
  "detail": "Successfully assigned 5 servicemen to category 'Electrical'",
  "category": {
    "id": 2,
    "name": "Electrical"
  },
  "updated_servicemen": [
    {
      "id": 5,
      "username": "john_elec",
      "full_name": "John Smith"
    },
    {
      "id": 6,
      "username": "mike_elec",
      "full_name": "Mike Johnson"
    }
  ],
  "total_updated": 5,
  "not_found": 0
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/users/admin/bulk-assign-category/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "serviceman_ids": [5, 6, 7, 8, 9],
    "category_id": 2
  }'
```

---

### 3. Get Servicemen Grouped by Category

**Endpoint**: `GET /api/users/admin/servicemen-by-category/`

**Purpose**: View all servicemen organized by their categories

**Auth**: Admin only

**Response:**
```json
{
  "total_servicemen": 25,
  "total_categories": 5,
  "categories": [
    {
      "category": {
        "id": 1,
        "name": "Plumbing",
        "description": "Plumbing services"
      },
      "servicemen_count": 8,
      "servicemen": [
        {
          "id": 1,
          "username": "plumber1",
          "full_name": "John Plumber",
          "email": "john@example.com",
          "is_available": true,
          "rating": 4.8,
          "total_jobs_completed": 45
        }
      ]
    },
    {
      "category": {
        "id": 2,
        "name": "Electrical",
        "description": "Electrical services"
      },
      "servicemen_count": 12,
      "servicemen": [...]
    },
    {
      "category": null,
      "servicemen_count": 5,
      "servicemen": [...],
      "note": "Unassigned servicemen - no category set"
    }
  ]
}
```

**Example:**
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/users/admin/servicemen-by-category/
```

---

## 🎯 Use Cases

### Use Case 1: Assign New Serviceman to Category

**Scenario**: Admin reviews new serviceman registration and assigns them to correct category

```javascript
// Admin dashboard - Serviceman management
async function assignServicemanToCategory(servicemanId, categoryId, adminToken) {
  const response = await fetch('/api/users/admin/assign-category/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      serviceman_id: servicemanId,
      category_id: categoryId
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    alert(`${data.serviceman.full_name} assigned to ${data.new_category.name}`);
  } else {
    alert('Error: ' + data.detail);
  }
  
  return data;
}

// Usage
await assignServicemanToCategory(5, 2, adminToken);
```

### Use Case 2: Move Multiple Servicemen Between Categories

**Scenario**: Admin reorganizes servicemen, moving several from one category to another

```javascript
async function moveServicemenToCategory(servicemanIds, newCategoryId, adminToken) {
  const response = await fetch('/api/users/admin/bulk-assign-category/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${adminToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      serviceman_ids: servicemanIds,
      category_id: newCategoryId
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    alert(`${data.total_updated} servicemen moved to ${data.category.name}`);
  }
  
  return data;
}

// Usage: Move 5 servicemen to Electrical category
await moveServicemenToCategory([5, 6, 7, 8, 9], 2, adminToken);
```

### Use Case 3: Admin Dashboard - Category Overview

**Scenario**: Admin views servicemen distribution across categories

```javascript
async function getCategoryOverview(adminToken) {
  const response = await fetch('/api/users/admin/servicemen-by-category/', {
    headers: {
      'Authorization': `Bearer ${adminToken}`
    }
  });
  
  return await response.json();
}

// React Component
function CategoryOverviewDashboard() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    getCategoryOverview(adminToken).then(setData);
  }, []);
  
  if (!data) return <div>Loading...</div>;
  
  return (
    <div className="admin-dashboard">
      <h1>Servicemen by Category</h1>
      
      <div className="stats">
        <p>Total Servicemen: {data.total_servicemen}</p>
        <p>Total Categories: {data.total_categories}</p>
      </div>
      
      {data.categories.map((item, idx) => (
        <div key={idx} className="category-section">
          <h2>
            {item.category ? item.category.name : 'Unassigned'}
            <span className="badge">{item.servicemen_count}</span>
          </h2>
          
          {item.note && <p className="text-orange-600">{item.note}</p>}
          
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Rating</th>
                <th>Jobs</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {item.servicemen.map(s => (
                <tr key={s.id}>
                  <td>{s.full_name || s.username}</td>
                  <td>{s.email}</td>
                  <td>⭐ {s.rating}</td>
                  <td>{s.total_jobs_completed}</td>
                  <td>
                    <span className={s.is_available ? 'badge-green' : 'badge-orange'}>
                      {s.is_available ? 'Available' : 'Busy'}
                    </span>
                  </td>
                  <td>
                    <button onClick={() => reassignServiceman(s.id)}>
                      Reassign
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
```

### Use Case 4: Reassign Serviceman with Confirmation

```javascript
function ReassignServicemanModal({ serviceman, onClose, onSuccess }) {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  
  useEffect(() => {
    // Load categories
    fetch('/api/categories/')
      .then(r => r.json())
      .then(setCategories);
  }, []);
  
  const handleReassign = async () => {
    if (!selectedCategory) {
      alert('Please select a category');
      return;
    }
    
    const data = await assignServicemanToCategory(
      serviceman.id,
      selectedCategory,
      adminToken
    );
    
    if (data.detail) {
      alert(data.detail);
      onSuccess();
      onClose();
    }
  };
  
  return (
    <div className="modal">
      <h3>Reassign {serviceman.full_name}</h3>
      <p>Current Category: {serviceman.category?.name || 'None'}</p>
      
      <select 
        value={selectedCategory || ''} 
        onChange={(e) => setSelectedCategory(Number(e.target.value))}
      >
        <option value="">-- Select Category --</option>
        {categories.map(cat => (
          <option key={cat.id} value={cat.id}>
            {cat.name}
          </option>
        ))}
      </select>
      
      <div className="buttons">
        <button onClick={handleReassign}>Reassign</button>
        <button onClick={onClose}>Cancel</button>
      </div>
    </div>
  );
}
```

---

## 📊 Complete Admin Workflow

### Initial Setup: Assign New Servicemen

```javascript
// 1. Get unassigned servicemen
const overview = await getCategoryOverview(adminToken);
const unassigned = overview.categories.find(c => c.category === null);

if (unassigned && unassigned.servicemen_count > 0) {
  console.log(`${unassigned.servicemen_count} servicemen need category assignment`);
  
  // 2. Show assignment form for each
  for (const serviceman of unassigned.servicemen) {
    // Show modal to select category
    const categoryId = await showCategorySelectionModal(serviceman);
    
    // 3. Assign to selected category
    await assignServicemanToCategory(serviceman.id, categoryId, adminToken);
  }
}
```

### Reorganization: Move Servicemen Between Categories

```javascript
// Scenario: Move all "General" servicemen to specific categories
async function reorganizeServicemen(adminToken) {
  // 1. Get all servicemen by category
  const overview = await getCategoryOverview(adminToken);
  
  // 2. Find "General" category servicemen
  const generalCategory = overview.categories.find(
    c => c.category?.name === 'General'
  );
  
  if (!generalCategory) return;
  
  // 3. Group by skills and reassign
  for (const serviceman of generalCategory.servicemen) {
    // Get their skills
    const profile = await fetch(`/api/users/servicemen/${serviceman.id}/`)
      .then(r => r.json());
    
    // Determine best category based on skills
    const newCategoryId = determineCategoryFromSkills(profile.skills);
    
    // Reassign
    await assignServicemanToCategory(
      serviceman.id,
      newCategoryId,
      adminToken
    );
  }
}
```

---

## 🎨 Frontend Components

### Category Assignment Form
```javascript
function CategoryAssignmentForm({ serviceman, onSuccess }) {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(
    serviceman.category?.id || null
  );
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetch('/api/categories/')
      .then(r => r.json())
      .then(setCategories);
  }, []);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await assignServicemanToCategory(
        serviceman.id,
        selectedCategory,
        adminToken
      );
      alert('Category assigned successfully!');
      onSuccess();
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <h3>Assign Category for {serviceman.full_name}</h3>
      
      <div className="form-group">
        <label>Current Category:</label>
        <p>{serviceman.category?.name || 'None'}</p>
      </div>
      
      <div className="form-group">
        <label>New Category:</label>
        <select 
          value={selectedCategory || ''} 
          onChange={(e) => setSelectedCategory(Number(e.target.value) || null)}
          required
        >
          <option value="">-- Select Category --</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
          <option value="">Remove Category</option>
        </select>
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Assigning...' : 'Assign Category'}
      </button>
    </form>
  );
}
```

### Bulk Assignment Interface
```javascript
function BulkCategoryAssignment() {
  const [servicemen, setServicemen] = useState([]);
  const [selectedServicemen, setSelectedServicemen] = useState([]);
  const [targetCategory, setTargetCategory] = useState(null);
  const [categories, setCategories] = useState([]);
  
  useEffect(() => {
    // Load all servicemen
    fetch('/api/users/servicemen/')
      .then(r => r.json())
      .then(data => setServicemen(data.results));
    
    // Load categories
    fetch('/api/categories/')
      .then(r => r.json())
      .then(setCategories);
  }, []);
  
  const handleBulkAssign = async () => {
    if (selectedServicemen.length === 0) {
      alert('Please select servicemen');
      return;
    }
    
    if (!targetCategory) {
      alert('Please select target category');
      return;
    }
    
    try {
      const response = await fetch('/api/users/admin/bulk-assign-category/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${adminToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          serviceman_ids: selectedServicemen,
          category_id: targetCategory
        })
      });
      
      const data = await response.json();
      alert(data.detail);
      
      // Reload servicemen
      window.location.reload();
      
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };
  
  const toggleSelection = (id) => {
    setSelectedServicemen(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id)
        : [...prev, id]
    );
  };
  
  return (
    <div className="bulk-assignment">
      <h2>Bulk Category Assignment</h2>
      
      <div className="controls">
        <select 
          value={targetCategory || ''}
          onChange={(e) => setTargetCategory(Number(e.target.value))}
        >
          <option value="">-- Select Target Category --</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
        
        <button 
          onClick={handleBulkAssign}
          disabled={selectedServicemen.length === 0 || !targetCategory}
        >
          Assign {selectedServicemen.length} Servicemen
        </button>
      </div>
      
      <table>
        <thead>
          <tr>
            <th><input type="checkbox" onChange={(e) => {
              if (e.target.checked) {
                setSelectedServicemen(servicemen.map(s => s.user));
              } else {
                setSelectedServicemen([]);
              }
            }}/></th>
            <th>Name</th>
            <th>Current Category</th>
            <th>Rating</th>
          </tr>
        </thead>
        <tbody>
          {servicemen.map(s => (
            <tr key={s.user}>
              <td>
                <input 
                  type="checkbox" 
                  checked={selectedServicemen.includes(s.user)}
                  onChange={() => toggleSelection(s.user)}
                />
              </td>
              <td>{s.user.full_name || s.user.username}</td>
              <td>{s.category?.name || 'Unassigned'}</td>
              <td>⭐ {s.rating}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### Category Overview Dashboard
```javascript
function CategoryOverviewDashboard() {
  const [overview, setOverview] = useState(null);
  
  useEffect(() => {
    fetch('/api/users/admin/servicemen-by-category/', {
      headers: { 'Authorization': `Bearer ${adminToken}` }
    })
      .then(r => r.json())
      .then(setOverview);
  }, []);
  
  if (!overview) return <div>Loading...</div>;
  
  return (
    <div className="dashboard">
      <h1>Category Management Dashboard</h1>
      
      <div className="stats-cards">
        <div className="stat-card">
          <h3>{overview.total_servicemen}</h3>
          <p>Total Servicemen</p>
        </div>
        <div className="stat-card">
          <h3>{overview.total_categories}</h3>
          <p>Categories</p>
        </div>
      </div>
      
      {overview.categories.map((item, idx) => (
        <div key={idx} className="category-panel">
          <div className="category-header">
            <h2>
              {item.category ? item.category.name : '⚠️ Unassigned'}
            </h2>
            <span className="count-badge">{item.servicemen_count}</span>
          </div>
          
          {item.note && (
            <div className="alert alert-warning">{item.note}</div>
          )}
          
          <div className="servicemen-grid">
            {item.servicemen.map(s => (
              <div key={s.id} className="serviceman-card">
                <h4>{s.full_name || s.username}</h4>
                <p>{s.email}</p>
                <p>⭐ {s.rating} | {s.total_jobs_completed} jobs</p>
                <span className={s.is_available ? 'badge-green' : 'badge-orange'}>
                  {s.is_available ? 'Available' : 'Busy'}
                </span>
                
                {item.category === null && (
                  <button onClick={() => showAssignModal(s)}>
                    Assign Category
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔧 Admin API Helper Class

```javascript
class AdminCategoryAPI {
  constructor(baseURL, getToken) {
    this.baseURL = baseURL;
    this.getToken = getToken;
  }
  
  async request(endpoint, options = {}) {
    const token = await this.getToken();
    const response = await fetch(this.baseURL + endpoint, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }
    
    return await response.json();
  }
  
  // Assign single serviceman to category
  async assignCategory(servicemanId, categoryId) {
    return this.request('/api/users/admin/assign-category/', {
      method: 'POST',
      body: JSON.stringify({
        serviceman_id: servicemanId,
        category_id: categoryId
      })
    });
  }
  
  // Bulk assign servicemen
  async bulkAssignCategory(servicemanIds, categoryId) {
    return this.request('/api/users/admin/bulk-assign-category/', {
      method: 'POST',
      body: JSON.stringify({
        serviceman_ids: servicemanIds,
        category_id: categoryId
      })
    });
  }
  
  // Get overview
  async getCategoryOverview() {
    return this.request('/api/users/admin/servicemen-by-category/');
  }
  
  // Remove category (set to null)
  async removeCategory(servicemanId) {
    return this.request('/api/users/admin/assign-category/', {
      method: 'POST',
      body: JSON.stringify({
        serviceman_id: servicemanId,
        category_id: null
      })
    });
  }
}

// Usage
const getToken = () => localStorage.getItem('access_token');
const adminAPI = new AdminCategoryAPI('http://localhost:8000', getToken);

// Assign category
await adminAPI.assignCategory(5, 2);

// Bulk assign
await adminAPI.bulkAssignCategory([5, 6, 7], 2);

// Get overview
const overview = await adminAPI.getCategoryOverview();

// Remove category
await adminAPI.removeCategory(5);
```

---

## 🧪 Testing

### Test Single Assignment
```bash
curl -X POST http://localhost:8000/api/users/admin/assign-category/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceman_id": 5, "category_id": 2}'
```

### Test Bulk Assignment
```bash
curl -X POST http://localhost:8000/api/users/admin/bulk-assign-category/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"serviceman_ids": [5,6,7,8], "category_id": 2}'
```

### Test Category Overview
```bash
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/users/admin/servicemen-by-category/
```

---

## ✅ Features

| Feature | Endpoint |
|---------|----------|
| Assign single serviceman | `POST /api/users/admin/assign-category/` |
| Bulk assign servicemen | `POST /api/users/admin/bulk-assign-category/` |
| View by category | `GET /api/users/admin/servicemen-by-category/` |
| Remove assignment | Same endpoint with `category_id: null` |

### Benefits
✅ **Single Assignment** - Quick category changes  
✅ **Bulk Operations** - Assign multiple at once  
✅ **Overview Dashboard** - See all categories  
✅ **Unassigned Detection** - Find servicemen without categories  
✅ **Audit Logging** - All changes logged  
✅ **Admin Only** - Secure access control  

---

## 📞 Support

**Interactive Testing**: http://localhost:8000/api/docs/  
**Full Docs**: See API_ENDPOINTS_VISUAL_MAP.md

---

**Status**: ✅ IMPLEMENTED  
**Endpoints**: 3 new admin endpoints  
**Auth**: Admin only  
**Ready**: Production ready

