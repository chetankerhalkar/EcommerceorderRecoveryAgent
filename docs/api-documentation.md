# AICK Studio Abandoned Cart Recovery Agent - API Documentation

## Overview

The AICK Studio Abandoned Cart Recovery Agent provides a comprehensive REST API built with FastAPI, offering endpoints for agent management, dashboard data retrieval, and webhook processing. This documentation covers all available endpoints, request/response formats, authentication requirements, and integration examples.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

Currently, the API operates without authentication for development purposes. Production deployments should implement appropriate authentication mechanisms such as API keys, JWT tokens, or OAuth 2.0.

## API Endpoints

### Health Check

#### GET /health

Returns the current health status of the API service.

**Response:**
```json
{
    "status": "healthy",
    "service": "AICK Studio Abandoned Cart Recovery Agent",
    "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK`: Service is healthy and operational

---

## Agent Management Endpoints

### Start Recovery Workflow

#### POST /api/agent/start-recovery

Initiates the abandoned cart recovery workflow using the LangGraph agent.

**Request Body:**
```json
{
    "use_mock": false,
    "config": {
        "abandonment_minutes": 15,
        "max_attempts": 3
    }
}
```

**Parameters:**
- `use_mock` (boolean, optional): Whether to use mock data for testing. Default: `false`
- `config` (object, optional): Configuration parameters for the workflow

**Response:**
```json
{
    "success": true,
    "message": "Recovery workflow started",
    "mock_mode": false
}
```

**Status Codes:**
- `200 OK`: Workflow started successfully
- `500 Internal Server Error`: Failed to start workflow

**Example:**
```bash
curl -X POST "http://localhost:8000/api/agent/start-recovery" \
     -H "Content-Type: application/json" \
     -d '{
         "use_mock": true,
         "config": {
             "abandonment_minutes": 10
         }
     }'
```

### Recover Specific Cart

#### POST /api/agent/recover-cart

Triggers recovery for a specific abandoned cart with provided cart and customer data.

**Request Body:**
```json
{
    "cart": {
        "id": "cart_123",
        "token": "abc123",
        "line_items": [
            {
                "id": 1,
                "variant_id": 123,
                "title": "Premium Headphones",
                "quantity": 1,
                "price": "199.99",
                "line_price": "199.99",
                "image": "https://example.com/image.jpg",
                "url": "/products/headphones",
                "sku": "HP001",
                "vendor": "AudioTech"
            }
        ],
        "total_price": 19999,
        "currency": "USD",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:45:00Z",
        "item_count": 1
    },
    "customer": {
        "id": 456,
        "email": "customer@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "orders_count": 2,
        "total_spent": "450.00",
        "accepts_marketing": true,
        "tags": "vip"
    },
    "use_mock": false
}
```

**Response:**
```json
{
    "success": true,
    "recovery_successful": false,
    "cart_id": "cart_123",
    "customer_email": "customer@example.com",
    "email_sent": true,
    "email_subject": "Don't miss out, John! Your cart is waiting",
    "recovery_message": "Hi John, we noticed you left some amazing items..."
}
```

**Status Codes:**
- `200 OK`: Recovery process completed
- `500 Internal Server Error`: Recovery process failed

### Get Workflow Status

#### GET /api/agent/status/{thread_id}

Retrieves the current status of a specific workflow thread.

**Path Parameters:**
- `thread_id` (string): Unique identifier for the workflow thread

**Response:**
```json
{
    "status": "completed",
    "cart_id": "cart_123",
    "customer_email": "customer@example.com",
    "recovery_attempts": 1,
    "recovery_successful": true,
    "error_message": null
}
```

**Status Values:**
- `not_found`: Thread ID not found
- `active`: Workflow is currently running
- `completed`: Workflow has finished
- `error`: Workflow encountered an error

#### GET /api/agent/status

Retrieves the status of the default workflow thread.

**Response:** Same format as above

### Test Email Functionality

#### POST /api/agent/test-email

Sends a test email to verify SendGrid configuration.

**Query Parameters:**
- `email` (string, required): Recipient email address

**Response:**
```json
{
    "success": true,
    "message": "Test email sent successfully",
    "recipient": "test@example.com"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/agent/test-email?email=test@example.com"
```

### Get Mock Data

#### GET /api/agent/mock-data

Returns mock cart and customer data for testing purposes.

**Response:**
```json
{
    "success": true,
    "data": {
        "cart": { /* cart object */ },
        "customer": { /* customer object */ },
        "abandonment_info": { /* abandonment details */ }
    }
}
```

### Generate Recovery Message

#### POST /api/agent/generate-message

Generates a recovery message preview without sending an email.

**Request Body:** Same as `/api/agent/recover-cart`

**Response:**
```json
{
    "success": true,
    "email_subject": "Complete your purchase, John!",
    "recovery_message": "Hi John, we noticed...",
    "email_html_content": "<html>...</html>",
    "error_message": null
}
```

---

## Dashboard Endpoints

### Get Dashboard Statistics

#### GET /api/dashboard/stats

Retrieves comprehensive dashboard statistics for the specified time period.

**Query Parameters:**
- `days` (integer, optional): Number of days to analyze. Default: `30`

**Response:**
```json
{
    "total_abandoned_carts": 150,
    "recovery_attempts": 120,
    "successful_recoveries": 18,
    "recovery_rate": 15.0,
    "total_revenue_recovered": 2450.75,
    "email_open_rate": 24.5,
    "email_click_rate": 8.3
}
```

### Get Abandoned Carts

#### GET /api/dashboard/carts

Retrieves a list of abandoned carts with filtering options.

**Query Parameters:**
- `limit` (integer, optional): Number of carts to return. Default: `20`
- `status` (string, optional): Filter by status (`all`, `pending`, `recovered`, `failed`). Default: `all`

**Response:**
```json
[
    {
        "cart_id": "cart_001",
        "customer_name": "John Doe",
        "customer_email": "john.doe@example.com",
        "total_value": 299.99,
        "currency": "USD",
        "abandoned_at": "2024-01-15T14:30:00Z",
        "recovery_status": "recovered",
        "email_sent": true,
        "email_opened": true,
        "email_clicked": true,
        "returned_to_cart": true,
        "checkout_completed": true
    }
]
```

### Get Recent Activity

#### GET /api/dashboard/activity

Retrieves recent recovery activity events.

**Query Parameters:**
- `limit` (integer, optional): Number of activities to return. Default: `10`

**Response:**
```json
[
    {
        "timestamp": "2024-01-15T16:30:00Z",
        "activity_type": "email_sent",
        "description": "Recovery email sent for cart_001",
        "cart_id": "cart_001",
        "customer_email": "john.doe@example.com"
    }
]
```

### Get Cart Details

#### GET /api/dashboard/cart/{cart_id}

Retrieves detailed information about a specific cart.

**Path Parameters:**
- `cart_id` (string): Cart identifier

**Response:**
```json
{
    "cart": { /* detailed cart object */ },
    "customer": { /* customer object */ },
    "recovery_attempts": [ /* array of recovery attempts */ ],
    "abandonment_info": { /* abandonment details */ }
}
```

### Trigger Cart Recovery

#### POST /api/dashboard/cart/{cart_id}/recover

Manually triggers recovery for a specific cart.

**Path Parameters:**
- `cart_id` (string): Cart identifier

**Response:**
```json
{
    "success": true,
    "message": "Recovery triggered for cart cart_001",
    "result": { /* recovery result object */ }
}
```

### Get Recovery Rate Analytics

#### GET /api/dashboard/analytics/recovery-rate

Retrieves recovery rate analytics over time.

**Query Parameters:**
- `days` (integer, optional): Number of days to analyze. Default: `30`

**Response:**
```json
{
    "period_days": 30,
    "daily_stats": [
        {
            "date": "2024-01-15",
            "abandoned_carts": 8,
            "recovered_carts": 2,
            "recovery_rate": 25.0
        }
    ],
    "summary": {
        "average_recovery_rate": 15.2,
        "best_day_rate": 22.5,
        "worst_day_rate": 8.1,
        "trend": "improving"
    }
}
```

---

## Webhook Endpoints

### Shopify Cart Update Webhook

#### POST /api/webhooks/shopify/cart-update

Handles incoming Shopify cart update webhooks.

**Headers:**
- `X-Shopify-Hmac-Sha256`: Shopify signature for verification
- `X-Shopify-Topic`: Webhook topic (e.g., `carts/update`)

**Request Body:** Shopify cart data (varies by webhook topic)

**Response:**
```json
{
    "status": "success",
    "message": "Webhook processed"
}
```

**Status Codes:**
- `200 OK`: Webhook processed successfully
- `401 Unauthorized`: Invalid signature
- `500 Internal Server Error`: Processing failed

### SendGrid Event Webhook

#### POST /api/webhooks/sendgrid/events

Handles SendGrid email event webhooks for tracking email engagement.

**Request Body:**
```json
[
    {
        "event": "open",
        "email": "customer@example.com",
        "timestamp": 1642262400,
        "cart_id": "cart_123",
        "customer_id": "456",
        "recovery_attempt": "1"
    }
]
```

**Response:**
```json
{
    "status": "success",
    "message": "Processed 1 events"
}
```

### Test Webhook Endpoints

#### POST /api/webhooks/test/shopify

Test endpoint for Shopify webhook development.

#### POST /api/webhooks/test/sendgrid

Test endpoint for SendGrid webhook development.

---

## Error Handling

### Standard Error Response Format

All API endpoints return errors in a consistent format:

```json
{
    "detail": "Error description",
    "error_code": "SPECIFIC_ERROR_CODE",
    "timestamp": "2024-01-15T16:30:00Z"
}
```

### Common Error Codes

- `INVALID_REQUEST`: Request validation failed
- `CART_NOT_FOUND`: Specified cart does not exist
- `CUSTOMER_NOT_FOUND`: Customer information unavailable
- `EMAIL_DELIVERY_FAILED`: Email could not be sent
- `EXTERNAL_API_ERROR`: External service (Shopify/SendGrid) error
- `WORKFLOW_ERROR`: LangGraph workflow execution failed

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: External service unavailable
- `503 Service Unavailable`: Service temporarily unavailable

---

## Rate Limiting

The API implements rate limiting to ensure fair usage and system stability:

- **Default Limit**: 100 requests per minute per IP address
- **Webhook Endpoints**: 1000 requests per minute (higher limit for external services)
- **Headers**: Rate limit information included in response headers
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Window reset time (Unix timestamp)

---

## SDK and Integration Examples

### Python Integration

```python
import requests
import json

class AICKCartRecoveryClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def start_recovery(self, use_mock=False, config=None):
        url = f"{self.base_url}/api/agent/start-recovery"
        payload = {
            "use_mock": use_mock,
            "config": config or {}
        }
        response = requests.post(url, json=payload)
        return response.json()
    
    def get_dashboard_stats(self, days=30):
        url = f"{self.base_url}/api/dashboard/stats"
        params = {"days": days}
        response = requests.get(url, params=params)
        return response.json()

# Usage example
client = AICKCartRecoveryClient()
stats = client.get_dashboard_stats(days=7)
print(f"Recovery rate: {stats['recovery_rate']}%")
```

### JavaScript Integration

```javascript
class AICKCartRecoveryAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async startRecovery(useMock = false, config = {}) {
        const response = await fetch(`${this.baseUrl}/api/agent/start-recovery`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                use_mock: useMock,
                config: config
            })
        });
        return response.json();
    }
    
    async getDashboardStats(days = 30) {
        const response = await fetch(
            `${this.baseUrl}/api/dashboard/stats?days=${days}`
        );
        return response.json();
    }
}

// Usage example
const api = new AICKCartRecoveryAPI();
const stats = await api.getDashboardStats(7);
console.log(`Recovery rate: ${stats.recovery_rate}%`);
```

---

## OpenAPI Specification

The complete OpenAPI specification is available at:
- **Interactive Documentation**: `http://localhost:8000/api/docs`
- **ReDoc Documentation**: `http://localhost:8000/api/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

This specification can be used to generate client SDKs in various programming languages using tools like OpenAPI Generator.

---

## Versioning

The API follows semantic versioning principles:
- **Current Version**: v1.0.0
- **Version Header**: `X-API-Version: 1.0.0`
- **Backward Compatibility**: Maintained for minor version updates
- **Deprecation Policy**: 6-month notice for breaking changes

---

## Support and Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the FastAPI server is running on the correct port
2. **CORS Errors**: Check CORS configuration for frontend integration
3. **Webhook Verification Failed**: Verify webhook secret configuration
4. **Rate Limit Exceeded**: Implement exponential backoff in client code

### Debug Mode

Enable debug mode by setting `LOG_LEVEL=DEBUG` in environment variables for detailed request/response logging.

### Health Monitoring

Monitor API health using the `/health` endpoint in your monitoring systems. The endpoint provides service status and version information for operational visibility.

