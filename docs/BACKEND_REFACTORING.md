# Backend Architecture Refactoring

## Overview

The backend has been refactored from a monolithic route-based structure to a clean, layered architecture following Domain-Driven Design (DDD) and Clean Architecture principles.

---

## New Folder Layout

```
backend/
├── domain/                 # Domain layer - business entities
│   ├── __init__.py
│   └── models/            # Domain models with validation
│       ├── __init__.py
│       ├── user.py
│       ├── assessment.py
│       └── report.py
├── repositories/          # Data access layer
│   ├── __init__.py
│   ├── base.py           # BaseRepository with CRUD
│   ├── user_repository.py
│   ├── assessment_repository.py
│   └── report_repository.py
├── services/             # Business logic layer
│   ├── __init__.py
│   └── auth_service.py   # Authentication business logic
├── api/                  # API layer - thin HTTP handlers
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       └── auth.py       # Auth HTTP endpoints
├── routes/               # [LEGACY] Old route files (to be migrated)
├── models.py             # [LEGACY] Old models (still used by old routes)
├── server.py             # FastAPI application setup
└── utils/                # Shared utilities
    └── database.py
```

---

## Architecture Layers

### 1. Domain Layer (`domain/`)

**Purpose**: Define business entities, value objects, and domain rules.

**Responsibilities**:
- Define data models with Pydantic
- Enforce business rules and invariants
- Validate data at domain level
- No database or HTTP dependencies

**Example**:
```python
# domain/models/user.py
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v
```

**Key Files**:
- `domain/models/user.py` - User entities and value objects
- `domain/models/assessment.py` - Assessment domain models
- `domain/models/report.py` - Report domain models

---

### 2. Repository Layer (`repositories/`)

**Purpose**: Abstract data access and provide a clean interface for persistence.

**Responsibilities**:
- CRUD operations on database collections
- Query building and execution
- Data transformation (MongoDB ↔ Python dicts)
- No business logic

**Example**:
```python
# repositories/user_repository.py
class UserRepository(BaseRepository):
    async def find_by_email(self, email: str) -> Optional[dict]:
        return await self.find_one({"email": email})
    
    async def is_email_taken(self, email: str) -> bool:
        count = await self.count({"email": email})
        return count > 0
```

**Key Files**:
- `repositories/base.py` - Generic CRUD operations
- `repositories/user_repository.py` - User data access
- `repositories/assessment_repository.py` - Assessment data access
- `repositories/report_repository.py` - Report data access

**Benefits**:
- Easy to test (mock repositories)
- Database-agnostic (can swap MongoDB for PostgreSQL)
- Centralized data access logic

---

### 3. Service Layer (`services/`)

**Purpose**: Implement business logic and orchestrate operations.

**Responsibilities**:
- Business rule enforcement
- Transaction coordination
- Complex operations spanning multiple entities
- Validation beyond simple field checks
- No HTTP concerns (status codes, headers, etc.)

**Example**:
```python
# services/auth_service.py
class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()
        self.profile_repo = UserProfileRepository()
    
    async def register_user(self, user_data: UserCreate) -> Tuple[User, str]:
        # Check uniqueness
        if await self.user_repo.is_email_taken(user_data.email):
            raise HTTPException(...)
        
        # Hash password
        hashed = self.hash_password(user_data.password)
        
        # Create user
        user = await self.user_repo.create({...})
        
        # Create profile
        await self.profile_repo.create_default_profile(user['id'])
        
        # Generate token
        token = self.create_access_token(user['id'], user['username'])
        
        return user, token
```

**Key Files**:
- `services/auth_service.py` - Authentication & user management

**Benefits**:
- Testable without HTTP layer
- Reusable across different interfaces (REST, GraphQL, CLI)
- Clear separation of concerns

---

### 4. API Layer (`api/routes/`)

**Purpose**: Handle HTTP requests and responses.

**Responsibilities**:
- HTTP endpoint definitions
- Request/response serialization
- Status code management
- Authentication middleware
- Minimal logic (delegate to services)

**Example**:
```python
# api/routes/auth.py
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    try:
        user, token = await auth_service.register_user(user_data)
        
        return {
            "user": user.dict(exclude={'hashed_password'}),
            "token": token,
            "message": "User registered successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )
```

**Key Files**:
- `api/routes/auth.py` - Authentication endpoints

**Benefits**:
- Thin controllers (easy to understand)
- Easy to add new endpoints
- Clear error handling

---

## Complete Example: Auth Module Refactoring

### Before (routes/auth_routes.py - 1022 lines)

```python
# Everything in one file
@router.post("/register")
async def register(user_data: UserCreate):
    # Validation
    if await db.users.find_one({"email": user_data.email}):
        raise HTTPException(...)
    
    # Password hashing
    hashed = hashlib.sha256(user_data.password.encode()).hexdigest()
    
    # Database operations
    user = {...}
    await db.users.insert_one(prepare_for_mongo(user))
    
    # Profile creation
    profile = {...}
    await db.user_profiles.insert_one(profile)
    
    # Relationship handling
    if user_data.parent_email:
        parent = await db.users.find_one({"email": user_data.parent_email})
        if parent:
            relationship = {...}
            await db.parent_player_relationships.insert_one(relationship)
    
    # Token generation
    token = jwt.encode({...}, JWT_SECRET)
    
    return {"user": user, "token": token}
```

### After (Separated)

```python
# domain/models/user.py
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password too short')
        return v

# repositories/user_repository.py
class UserRepository(BaseRepository):
    async def find_by_email(self, email: str):
        return await self.find_one({"email": email})
    
    async def is_email_taken(self, email: str):
        return await self.count({"email": email}) > 0

# services/auth_service.py
class AuthService:
    async def register_user(self, user_data: UserCreate):
        if await self.user_repo.is_email_taken(user_data.email):
            raise HTTPException(...)
        
        hashed = self.hash_password(user_data.password)
        user = await self.user_repo.create({...})
        await self.profile_repo.create_default_profile(user['id'])
        
        if user_data.parent_email:
            await self._create_parent_relationship(user['id'], user_data.parent_email)
        
        token = self.create_access_token(user['id'], user['username'])
        return user, token

# api/routes/auth.py
@router.post("/register")
async def register(user_data: UserCreate):
    user, token = await auth_service.register_user(user_data)
    return {"user": user.dict(), "token": token}
```

---

## Migration Progress

### ✅ Completed

**Auth Module** (routes/auth_routes.py → api/routes/auth.py)
- **Lines**: 1022 → ~180 (82% reduction in route file)
- **Domain Models**: User, UserCreate, UserLogin, UserProfile
- **Repositories**: UserRepository, UserProfileRepository, RelationshipRepository, InvitationRepository
- **Services**: AuthService with full business logic
- **Routes**: Thin HTTP handlers

**Endpoints Migrated**:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User authentication
- `GET /api/auth/profile` - Get user profile
- `GET /api/auth/benchmarks` - Get user benchmarks
- `GET /api/auth/saved-reports` - Get saved reports
- `GET /api/auth/health` - Health check

---

## Pattern to Apply to Other Routes

### Step 1: Identify Domain Models

Extract Pydantic models to `domain/models/`:
```python
# domain/models/assessment.py
class AssessmentCreate(BaseModel):
    player_name: str
    age: int
    # ... fields with validators
```

### Step 2: Create Repository

Create data access methods in `repositories/`:
```python
# repositories/assessment_repository.py
class AssessmentRepository(BaseRepository):
    async def find_by_user(self, user_id: str):
        return await self.find_many({"user_id": user_id})
    
    async def find_latest(self, user_id: str):
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1).limit(1)
        docs = await cursor.to_list(length=1)
        return docs[0] if docs else None
```

### Step 3: Create Service

Move business logic to `services/`:
```python
# services/assessment_service.py
class AssessmentService:
    def __init__(self):
        self.assessment_repo = AssessmentRepository()
    
    async def create_assessment(self, data: AssessmentCreate, user_id: str):
        # Validation
        # Business rules
        # Orchestration
        assessment = await self.assessment_repo.create({...})
        return assessment
```

### Step 4: Create Thin Route

Create HTTP endpoint in `api/routes/`:
```python
# api/routes/assessments.py
assessment_service = AssessmentService()

@router.post("/assessments")
async def create_assessment(
    data: AssessmentCreate,
    current_user: dict = Depends(verify_token)
):
    assessment = await assessment_service.create_assessment(data, current_user['user_id'])
    return {"assessment": assessment}
```

### Step 5: Update Server

Import new routes in `server.py`:
```python
from api.routes import auth
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
```

---

## Benefits of This Architecture

### 1. **Testability**
- **Unit tests**: Test services with mocked repositories
- **Integration tests**: Test repositories with real database
- **API tests**: Test routes with mocked services

### 2. **Maintainability**
- **Single Responsibility**: Each layer has one job
- **Easy to find code**: Clear structure
- **Smaller files**: Easier to understand

### 3. **Flexibility**
- **Swap databases**: Change repositories, services unchanged
- **Add GraphQL**: Reuse services with GraphQL resolvers
- **Add CLI**: Reuse services in command-line tools

### 4. **Scalability**
- **Parallel development**: Teams work on different layers
- **Microservices ready**: Extract services to separate apps
- **Clear boundaries**: Easy to optimize bottlenecks

---

## Next Steps

### Routes to Migrate

Priority order (by size and complexity):

1. ✅ **auth_routes.py** (1022 lines) - COMPLETE
2. **report_generation_routes.py** (1021 lines) - Next
3. **ai_coach_routes.py** (589 lines)
4. **messaging_routes.py** (475 lines)
5. **club_routes.py** (464 lines)
6. **dynamic_training_routes.py** (446 lines)
7. **assessment_routes.py** (445 lines)
8. **elite_training_routes.py** (368 lines)
9. **club_routes_ai.py** (343 lines)
10. **admin_routes.py** (341 lines)
11. **training_routes.py** (331 lines)
12. **notification_routes.py** (309 lines)
13. **progress_routes.py** (301 lines)
14. **relationships_routes.py** (268 lines)

### Verification Checklist

For each migrated route:
- [ ] Domain models created with validators
- [ ] Repository methods implemented
- [ ] Service methods with business logic
- [ ] Thin route handlers
- [ ] Import paths updated in server.py
- [ ] Backward compatibility maintained
- [ ] Error handling consistent
- [ ] Logging added
- [ ] Tests updated (if any)

---

## Backward Compatibility

### During Migration

Both old and new routes can coexist:

```python
# server.py
# Old routes (legacy)
from routes import auth_routes as auth_routes_legacy

# New routes (refactored)
from api.routes import auth

# Include both
app.include_router(auth_routes_legacy.router, prefix="/api/auth-legacy", tags=["auth-legacy"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
```

### After Migration

Once all routes are migrated and tested:
1. Remove old routes
2. Delete legacy `routes/` directory
3. Update `models.py` usage
4. Clean up imports

---

## Testing Strategy

### Unit Tests
```python
# tests/unit/test_auth_service.py
async def test_register_user():
    # Mock repositories
    user_repo = Mock(UserRepository)
    user_repo.is_email_taken.return_value = False
    
    service = AuthService()
    service.user_repo = user_repo
    
    user, token = await service.register_user(user_data)
    
    assert user.email == user_data.email
    assert token is not None
```

### Integration Tests
```python
# tests/integration/test_user_repository.py
async def test_find_by_email():
    repo = UserRepository()
    
    # Create test user
    await repo.create({"email": "test@example.com", ...})
    
    # Find user
    user = await repo.find_by_email("test@example.com")
    
    assert user is not None
    assert user['email'] == "test@example.com"
```

### API Tests
```python
# tests/e2e/test_auth_api.py
async def test_register_endpoint(client):
    response = await client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "role": "player"
    })
    
    assert response.status_code == 201
    assert "token" in response.json()
```

---

## References

- **Clean Architecture**: Robert C. Martin
- **Domain-Driven Design**: Eric Evans
- **FastAPI Best Practices**: https://fastapi.tiangolo.com/tutorial/
- **Repository Pattern**: Martin Fowler

---

**Last Updated**: November 2024  
**Status**: Auth module complete, ready to apply pattern to remaining routes
