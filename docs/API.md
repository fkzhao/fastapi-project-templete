# API Reference

Complete API reference for the FastAPI Project Template.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Currently using session-based authentication for admin panel.

### Admin Authentication
- **Endpoint**: `/admin`
- **Username**: `admin`
- **Password**: `123456` (change in production!)

## API Endpoints

### Health Check

#### GET /health
Check if the API is running and healthy.

**Response**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

**Status Codes**
- `200 OK`: Service is healthy

---

## User Endpoints

### Create User

#### POST /user/
Create a new user.

**Request Body**
```json
{
  "name": "John Doe",
  "nick_name": "johndoe",
  "email": "john@example.com"
}
```

**Response**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "nick_name": "johndoe",
    "email": "john@example.com",
    "create_time": "2025-10-28T10:00:00",
    "update_time": "2025-10-28T10:00:00"
  },
  "message": "User created successfully"
}
```

**Status Codes**
- `201 Created`: User created successfully
- `400 Bad Request`: Invalid input data
- `422 Unprocessable Entity`: Validation error

---

### Get User

#### GET /user/{user_id}
Retrieve a user by ID.

**Parameters**
- `user_id` (path, integer, required): User ID

**Response**
```json
{
  "id": 1,
  "name": "John Doe",
  "nick_name": "johndoe",
  "email": "john@example.com",
  "create_time": "2025-10-28T10:00:00",
  "update_time": "2025-10-28T10:00:00"
}
```

**Status Codes**
- `200 OK`: User found
- `404 Not Found`: User not found

---

### Update User

#### PUT /user/{user_id}
Update an existing user.

**Parameters**
- `user_id` (path, integer, required): User ID

**Request Body**
```json
{
  "name": "Jane Doe",
  "nick_name": "janedoe",
  "email": "jane@example.com"
}
```

**Response**
```json
{
  "id": 1,
  "name": "Jane Doe",
  "nick_name": "janedoe",
  "email": "jane@example.com",
  "create_time": "2025-10-28T10:00:00",
  "update_time": "2025-10-28T11:00:00"
}
```

**Status Codes**
- `200 OK`: User updated
- `404 Not Found`: User not found
- `422 Unprocessable Entity`: Validation error

---

### Delete User

#### DELETE /user/{user_id}
Delete a user by ID.

**Parameters**
- `user_id` (path, integer, required): User ID

**Response**
```json
{
  "message": "User 1 deleted successfully",
  "code": 200
}
```

**Status Codes**
- `200 OK`: User deleted
- `404 Not Found`: User not found

---

### List Users

#### GET /user/
Get a paginated list of users.

**Query Parameters**
- `page` (integer, optional, default: 1): Page number
- `page_size` (integer, optional, default: 10): Items per page (max: 100)
- `search` (string, optional): Search keyword

**Response**
```json
{
  "items": [
    {
      "id": 1,
      "name": "John Doe",
      "nick_name": "johndoe",
      "email": "john@example.com",
      "create_time": "2025-10-28T10:00:00",
      "update_time": "2025-10-28T10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

**Status Codes**
- `200 OK`: List retrieved successfully

---

## Product Endpoints

### Create Product

#### POST /product/
Create a new product.

**Request Body**
```json
{
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "stock": 50,
  "category": "Electronics"
}
```

**Response**
```json
{
  "id": 1,
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "stock": 50,
  "category": "Electronics",
  "create_time": "2025-10-28T10:00:00",
  "update_time": "2025-10-28T10:00:00"
}
```

**Status Codes**
- `201 Created`: Product created
- `422 Unprocessable Entity`: Validation error

---

### Get Product

#### GET /product/{product_id}
Retrieve a product by ID.

**Parameters**
- `product_id` (path, integer, required): Product ID

**Response**
```json
{
  "id": 1,
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "stock": 50,
  "category": "Electronics",
  "create_time": "2025-10-28T10:00:00",
  "update_time": "2025-10-28T10:00:00"
}
```

**Status Codes**
- `200 OK`: Product found
- `404 Not Found`: Product not found

---

### Update Product

#### PUT /product/{product_id}
Update an existing product.

**Parameters**
- `product_id` (path, integer, required): Product ID

**Request Body** (all fields optional)
```json
{
  "name": "Gaming Laptop",
  "price": 1299.99,
  "stock": 45
}
```

**Response**
```json
{
  "id": 1,
  "name": "Gaming Laptop",
  "description": "High-performance laptop",
  "price": 1299.99,
  "stock": 45,
  "category": "Electronics",
  "create_time": "2025-10-28T10:00:00",
  "update_time": "2025-10-28T11:00:00"
}
```

**Status Codes**
- `200 OK`: Product updated
- `404 Not Found`: Product not found

---

### Delete Product

#### DELETE /product/{product_id}
Delete a product by ID.

**Parameters**
- `product_id` (path, integer, required): Product ID

**Response**
```json
{
  "message": "Product 1 deleted successfully",
  "code": 200
}
```

**Status Codes**
- `200 OK`: Product deleted
- `404 Not Found`: Product not found

---

### List Products

#### GET /product/
Get a paginated list of products.

**Query Parameters**
- `page` (integer, optional, default: 1): Page number
- `page_size` (integer, optional, default: 10): Items per page (max: 100)
- `category` (string, optional): Filter by category

**Response**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Laptop",
      "description": "High-performance laptop",
      "price": 999.99,
      "stock": 50,
      "category": "Electronics",
      "create_time": "2025-10-28T10:00:00",
      "update_time": "2025-10-28T10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

**Status Codes**
- `200 OK`: List retrieved successfully

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Validation Error Format

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Common Status Codes

- `200 OK`: Request succeeded
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Interactive Documentation

For interactive API documentation with try-it-out features:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Rate Limiting

Currently no rate limiting is implemented.

Consider implementing rate limiting in production:
- User endpoints: 100 requests/minute
- Admin endpoints: 1000 requests/minute

---

## Versioning

API version is included in the response headers:
```
X-API-Version: 0.1.0
```

Future versions may use URL versioning:
- `/v1/user/`
- `/v2/user/`

---

**Last Updated**: October 28, 2025

