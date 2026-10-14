# REST API Specification & Reference

## Overview

The Feedback Intelligence System provides a versioned, secure REST API adhering to OpenAPI 3.0 standards. All API endpoints reside under the `/api/v1` namespace, except for global health check probes located at `/health` and `/ready`.

- **Base URL (Local Development):** `http://localhost:8000/api/v1`
- **Base URL (Docker Reverse Proxy):** `http://localhost:3000/api/v1` (or relative `/api/v1`)
- **Interactive Documentation:** `http://localhost:8000/docs` (Swagger UI) & `http://localhost:8000/redoc` (ReDoc)

---

## Standard Headers & Authentication

All protected routes require an HTTP Authorization header containing a valid JSON Web Token (JWT):

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Role Hierarchy
- **Viewer:** Read-only access to feedback records, analytics metrics, and trend charts.
- **Analyst:** All Viewer capabilities + ability to create feedback, edit feedback, and trigger AI analysis.
- **Admin:** Full access + user management, role modification, account deactivation, and feedback deletion.

---

## Standard Error Response

When an error occurs, the API returns a structured JSON payload:

```json
{
  "status": "error",
  "error_code": "RESOURCE_NOT_FOUND",
  "message": "Feedback record with ID 99999 was not found.",
  "timestamp": "2026-10-14T14:10:00.000000"
}
```

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### Register New Account
`POST /api/v1/auth/register`
Creates a new analyst or viewer account. Note: Administrator accounts cannot be created via public registration.

**Request Body:**
```json
{
  "name": "Jane Analyst",
  "email": "jane@example.com",
  "password": "SecurePassword123!",
  "role": "analyst"
}
```

**Response (`201 Created`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "name": "Jane Analyst",
    "email": "jane@example.com",
    "role": "analyst",
    "is_active": true,
    "created_at": "2026-10-14T08:30:00Z",
    "updated_at": "2026-10-14T08:30:00Z"
  }
}
```

---

### User Login
`POST /api/v1/auth/login`
Authenticates user credentials and returns a signed JWT access token.

**Request Body:**
```json
{
  "email": "jane@example.com",
  "password": "SecurePassword123!"
}
```

**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "name": "Jane Analyst",
    "email": "jane@example.com",
    "role": "analyst",
    "is_active": true,
    "created_at": "2026-10-14T08:30:00Z",
    "updated_at": "2026-10-14T08:30:00Z"
  }
}
```

---

### Current Session Profile
`GET /api/v1/auth/me`
Retrieves the authenticated user's account details.

**Response (`200 OK`):**
```json
{
  "id": 2,
  "name": "Jane Analyst",
  "email": "jane@example.com",
  "role": "analyst",
  "is_active": true,
  "created_at": "2026-10-14T08:30:00Z",
  "updated_at": "2026-10-14T08:30:00Z"
}
```

---

### User Logout (Token Revocation)
`POST /api/v1/auth/logout`
Revokes the caller's JWT token, rendering it permanently invalid.

**Response (`200 OK`):**
```json
{
  "status": "success",
  "message": "Successfully logged out. Access token has been revoked."
}
```

---

## 2. User Administration Endpoints (`/api/v1/users`)
*Requires Admin role.*

### List All Users
`GET /api/v1/users?skip=0&limit=50`

**Response (`200 OK`):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "System Administrator",
      "email": "admin@example.com",
      "role": "admin",
      "is_active": true,
      "created_at": "2026-10-14T08:00:00Z",
      "updated_at": "2026-10-14T08:00:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

---

### Update User Role
`PATCH /api/v1/users/{user_id}/role`

**Request Body:**
```json
{
  "role": "analyst"
}
```

**Response (`200 OK`):** Returns updated `UserResponse`.

---

### Toggle User Active Status
`PATCH /api/v1/users/{user_id}/status`

**Request Body:**
```json
{
  "is_active": false
}
```

**Response (`200 OK`):** Returns updated `UserResponse`.

---

### Delete User Account
`DELETE /api/v1/users/{user_id}`

**Response (`200 OK`):**
```json
{
  "status": "success",
  "message": "User 3 successfully deleted."
}
```

---

## 3. Feedback Operations (`/api/v1/feedback`)

### Submit Feedback
`POST /api/v1/feedback`
*Requires Analyst or Admin role.*

**Request Body:**
```json
{
  "source": "Web Form",
  "customer_identifier": "cust_842",
  "feedback_text": "The checkout workflow was simple, and delivery arrived 2 days earlier than expected!"
}
```

**Response (`201 Created`):**
```json
{
  "id": 14,
  "source": "Web Form",
  "customer_identifier": "cust_842",
  "feedback_text": "The checkout workflow was simple, and delivery arrived 2 days earlier than expected!",
  "category": null,
  "sentiment": null,
  "sentiment_score": null,
  "status": "new",
  "created_at": "2026-10-14T08:45:00Z",
  "updated_at": "2026-10-14T08:45:00Z"
}
```

---

### List Feedback Records
`GET /api/v1/feedback`
Supports filtering, full-text substring search, and pagination.

**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 20, max: 100)
- `search` (string, optional)
- `category` (string, optional)
- `sentiment` (string, optional: `positive`, `neutral`, `negative`)
- `source` (string, optional)
- `status` (string, optional: `new`, `reviewed`, `archived`)

**Response (`200 OK`):**
```json
{
  "items": [
    {
      "id": 14,
      "source": "Web Form",
      "customer_identifier": "cust_842",
      "feedback_text": "The checkout workflow was simple, and delivery arrived 2 days earlier than expected!",
      "category": "Delivery",
      "sentiment": "positive",
      "sentiment_score": 0.85,
      "status": "reviewed",
      "created_at": "2026-10-14T08:45:00Z",
      "updated_at": "2026-10-14T08:46:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

---

### Retrieve Feedback Detail
`GET /api/v1/feedback/{feedback_id}`

**Response (`200 OK`):** Returns single `FeedbackResponse`.

---

### Update Feedback Record
`PATCH /api/v1/feedback/{feedback_id}`
*Requires Analyst or Admin role.*

**Request Body:**
```json
{
  "status": "reviewed",
  "category": "Delivery"
}
```

**Response (`200 OK`):** Returns updated `FeedbackResponse`.

---

### Delete Feedback Record
`DELETE /api/v1/feedback/{feedback_id}`
*Requires Admin role.*

**Response (`200 OK`):**
```json
{
  "status": "success",
  "message": "Feedback with id 14 has been deleted."
}
```

---

## 4. AI & NLP Intelligence Endpoints

### Synchronous Single Analysis
`POST /api/v1/feedback/{feedback_id}/analyze`
Immediately cleans text, computes sentiment score, and classifies category.

**Response (`200 OK`):**
```json
{
  "id": 14,
  "source": "Web Form",
  "customer_identifier": "cust_842",
  "feedback_text": "The checkout workflow was simple, and delivery arrived 2 days earlier than expected!",
  "category": "Delivery",
  "sentiment": "positive",
  "sentiment_score": 0.85,
  "status": "reviewed",
  "created_at": "2026-10-14T08:45:00Z",
  "updated_at": "2026-10-14T08:46:00Z"
}
```

---

### Synchronous Batch Analysis
`POST /api/v1/feedback/batch-analyze?limit=50`
Processes up to `limit` unanalyzed records in the database.

**Response (`200 OK`):**
```json
{
  "status": "success",
  "message": "Batch analysis completed successfully.",
  "processed_count": 12,
  "errors_count": 0
}
```

---

### Asynchronous Single Analysis (Celery / Background)
`POST /api/v1/feedback/{feedback_id}/analyze-async`
Dispatches job to Celery worker queue.

**Response (`202 Accepted`):**
```json
{
  "status": "accepted",
  "message": "Feedback analysis task queued.",
  "task_id": "9a38f322-1d54-4f92-a16e-44dd6c2a4c11",
  "feedback_id": 14
}
```

---

### Asynchronous Batch Analysis
`POST /api/v1/feedback/batch-analyze-async?limit=100`

**Response (`202 Accepted`):**
```json
{
  "status": "accepted",
  "message": "Batch analysis task queued.",
  "task_id": "4b6e8284-fa12-426b-95eb-92c2f2e519c3"
}
```

---

## 5. Background Task Polling (`/api/v1/tasks`)

### Check Background Task Status
`GET /api/v1/tasks/{task_id}`

**Response (`200 OK`):**
```json
{
  "task_id": "9a38f322-1d54-4f92-a16e-44dd6c2a4c11",
  "status": "SUCCESS",
  "ready": true,
  "result": {
    "feedback_id": 14,
    "sentiment": "positive",
    "sentiment_score": 0.85,
    "category": "Delivery",
    "status": "completed"
  }
}
```

---

## 6. Analytics & Intelligence Reporting (`/api/v1/analytics`)

### Overview Metrics
`GET /api/v1/analytics/overview`

**Response (`200 OK`):**
```json
{
  "total_feedback": 150,
  "positive_count": 92,
  "negative_count": 31,
  "neutral_count": 27,
  "analyzed_count": 145,
  "pending_count": 5,
  "sentiment_distribution": {
    "positive": 63.4,
    "neutral": 18.6,
    "negative": 21.4
  }
}
```

---

### Sentiment Distribution
`GET /api/v1/analytics/sentiment`

**Response (`200 OK`):**
```json
{
  "total": 150,
  "positive": 92,
  "negative": 31,
  "neutral": 27,
  "percentages": {
    "positive": 63.4,
    "neutral": 18.6,
    "negative": 21.4
  },
  "average_sentiment_score": 0.68
}
```

---

### Category Distribution
`GET /api/v1/analytics/categories`

**Response (`200 OK`):**
```json
{
  "categories": {
    "Product Quality": 45,
    "Customer Support": 35,
    "Delivery": 25,
    "User Experience": 20,
    "Pricing": 15,
    "Feature Request": 8,
    "Other": 2
  },
  "total": 150,
  "percentages": {
    "Product Quality": 30.0,
    "Customer Support": 23.3,
    "Delivery": 16.7,
    "User Experience": 13.3,
    "Pricing": 10.0,
    "Feature Request": 5.3,
    "Other": 1.3
  },
  "uncategorized": 0
}
```

---

### Trends, Spike Detection & Actionable Recommendations
`GET /api/v1/analytics/trends?days=30`

**Response (`200 OK`):**
```json
{
  "start_date": "2026-09-14",
  "end_date": "2026-10-14",
  "total_volume": 150,
  "negative_spike_detected": false,
  "spike_message": null,
  "data_points": [
    {
      "date": "2026-10-13",
      "count": 14,
      "positive_count": 10,
      "negative_count": 2,
      "neutral_count": 2
    },
    {
      "date": "2026-10-14",
      "count": 18,
      "positive_count": 13,
      "negative_count": 3,
      "neutral_count": 2
    }
  ],
  "summary": "Customer sentiment across 150 records is overwhelmingly positive (63.4%), with primary operational volume centered around Product Quality and Customer Support.",
  "recommendations": [
    "Prioritize resolution of recurring questions in Customer Support to sustain positive response velocity.",
    "Monitor delivery packaging quality to prevent spikes in negative transit reports.",
    "Amplify positive testimonials from Product Quality in upcoming marketing campaigns."
  ]
}
```

---

## 7. Health & Infrastructure Probes

### Liveness Probe
`GET /health`
Validates that the web server process is alive and responsive.

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### Readiness Probe
`GET /ready`
Validates active connectivity to PostgreSQL database and Redis broker.

**Response (`200 OK`):**
```json
{
  "status": "ready",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2026-10-14T08:45:00Z"
}
```
