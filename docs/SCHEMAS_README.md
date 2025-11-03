# Pydantic Schemas Module Planning

## 📁 Directory Structure

```
src/
├── schemas/                    # Pydantic schemas (HTTP request/response models)
│   ├── __init__.py            # Export all schemas
│   ├── base.py                # Base schema classes and common response models
│   ├── user.py                # User-related schemas
│   └── product.py             # Product-related schemas
├── models/                    # SQLAlchemy ORM models (database models)
│   ├── base.py               # BaseModel and TimestampMixin
│   └── user.py               # User ORM model
├── router/                    # FastAPI routers
│   ├── user.py               # User routes
│   └── product.py            # Product routes
└── services/                  # Business logic layer (optional)
```

## 🎯 Design Principles

### 1. **Separation of Concerns**
- **models/**: SQLAlchemy ORM models - Define database table structure
- **schemas/**: Pydantic models - Define API input/output format
- **router/**: API routers - Define API endpoints
- **services/**: Business logic - Handle complex business rules

### 2. **Naming Conventions**

#### Request Schemas
- `{Resource}CreateRequest` - Create resource
- `{Resource}UpdateRequest` - Update resource
- `{Resource}QueryParams` - Query parameters

#### Response Schemas
- `{Resource}Response` - Complete resource response
- `{Resource}BriefResponse` - Simplified resource response (for lists)
- `{Resource}ListResponse` - List response (with pagination)

### 3. **Schema Hierarchy**

```python
# auth.py - Base classes
├── BaseResponse              # Base response class
├── TimestampSchema          # Timestamp Mixin
├── MessageResponse          # Simple message response
├── APIResponse[T]           # Generic API response wrapper
└── PaginatedResponse[T]     # Paginated response wrapper

# user.py - User-related
├── UserCreateRequest        # Create user request
├── UserUpdateRequest        # Update user request
├── UserQueryParams          # Query parameters
├── UserResponse             # User response
├── UserBriefResponse        # Brief user response
└── UserListResponse         # User list response
```

## 📝 Usage Examples

### 1. Define Request Schema

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreateRequest(BaseModel):
    """Request model for creating a user"""
    name: str = Field(..., min_length=1, max_length=100)
    nick_name: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "nick_name": "johndoe",
                "email": "john@example.com"
            }
        }
    )
```

### 2. Define Response Schema

```python
from .base import BaseResponse, TimestampSchema

class UserResponse(BaseResponse, TimestampSchema):
    """User response model"""
    id: int
    name: str
    nick_name: str
    email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)  # Allow conversion from ORM models
```

### 3. Use in Routes

```python
from fastapi import APIRouter
from schemas.user import UserCreateRequest, UserResponse

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user(user_data: UserCreateRequest):
    # FastAPI automatically validates user_data
    # Returned data will be automatically serialized to UserResponse format
    return UserResponse(
        id=1,
        name=user_data.name,
        nick_name=user_data.nick_name,
        email=user_data.email,
        create_time=datetime.now(),
        update_time=datetime.now()
    )
```

### 4. Use Generic Response Wrapper

```python
from schemas.base import APIResponse

@router.post("/", response_model=APIResponse[UserResponse])
async def create_user(user_data: UserCreateRequest):
    user = create_user_in_db(user_data)
    return APIResponse(
        success=True,
        data=user,
        message="User created successfully",
        code=201
    )
```

### 5. Convert from ORM Model

```python
from models.user import User  # SQLAlchemy model
from schemas.user import UserResponse  # Pydantic schema

# Query from database
db_user = session.query(User).first()

# Automatically convert to Pydantic schema
response = UserResponse.model_validate(db_user)

# Or return ORM object directly in route (FastAPI will auto-convert)
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    db_user = session.query(User).filter(User.id == user_id).first()
    return db_user  # FastAPI automatically converts to UserResponse
```

## ✨ Key Features

### 1. **Automatic Validation**
```python
class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr  # Automatically validates email format
    age: int = Field(..., ge=0, le=150)  # Age between 0-150
```

### 2. **Optional Fields and Default Values**
```python
class UserUpdateRequest(BaseModel):
    name: Optional[str] = None  # Optional field
    age: int = Field(default=18)  # Default value
```

### 3. **Nested Models**
```python
class AddressSchema(BaseModel):
    street: str
    city: str

class UserResponse(BaseModel):
    id: int
    name: str
    address: Optional[AddressSchema] = None  # Nested model
```

### 4. **Generic Responses**
```python
# Can be used for any data type
APIResponse[UserResponse]
APIResponse[ProductResponse]
APIResponse[List[UserResponse]]
```

### 5. **Automatic Documentation**
All Field descriptions and examples automatically appear in FastAPI's Swagger UI.

## 🚀 Best Practices

1. **Always use Field** to add descriptions and validation rules
2. **Provide examples for each schema** for better API documentation
3. **Separate Request and Response**, even if fields are the same
4. **Use Optional** to explicitly mark optional fields
5. **Use ConfigDict** to set model configuration (e.g., `from_attributes=True`)
6. **Layered design**: base schemas → specific schemas → router

## 📊 Schema vs Model Comparison

| Feature | Pydantic Schema (schemas/) | SQLAlchemy Model (models/) |
|---------|---------------------------|---------------------------|
| Purpose | API input/output validation | Database table definition |
| Validation | Automatic data validation | No validation |
| Serialization | JSON serialization | Manual conversion required |
| Inheritance | pydantic.BaseModel | sqlalchemy Base |
| Field Definition | Field() | Column() |

## 🔄 Data Flow

```
Client Request (JSON)
    ↓
[FastAPI] Auto-validation
    ↓
Pydantic Request Schema (UserCreateRequest)
    ↓
[Service Layer] Business logic
    ↓
SQLAlchemy ORM Model (User)
    ↓
[Database] Persistence
    ↓
SQLAlchemy ORM Model (User)
    ↓
Pydantic Response Schema (UserResponse)
    ↓
[FastAPI] Auto-serialization
    ↓
Client Response (JSON)
```

## 🛠️ Extension Suggestions

### 1. Add New Resource
Create new file `schemas/resource.py`, define:
- `{Resource}CreateRequest`
- `{Resource}UpdateRequest`
- `{Resource}Response`
- `{Resource}ListResponse`

### 2. Custom Validators
```python
from pydantic import field_validator

class UserCreateRequest(BaseModel):
    name: str
    
    @field_validator('name')
    def validate_name(cls, v):
        if 'admin' in v.lower():
            raise ValueError('Name cannot contain "admin"')
        return v
```

### 3. Add Common Query Parameters
```python
# schemas/auth.py
class QueryParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = None
    order: str = Field(default="asc", pattern="^(asc|desc)$")
```

---

**Note**: This design follows FastAPI best practices, keeping the code clean, maintainable, and extensible.

