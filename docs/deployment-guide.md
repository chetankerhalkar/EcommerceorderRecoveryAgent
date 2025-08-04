# AICK Studio Abandoned Cart Recovery Agent - Deployment Guide

## Quick Start Guide

This guide provides step-by-step instructions for deploying the AICK Studio Abandoned Cart Recovery Agent in both development and production environments.

## Prerequisites

Before deploying the application, ensure you have:

- **Node.js 20+** and **npm/pnpm** installed
- **Python 3.11+** and **pip** installed
- **Git** for version control
- **API Keys** for:
  - Shopify Admin API
  - OpenAI GPT-4
  - SendGrid (or alternative email service)

## Development Deployment

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd aick-abandoned-cart-agent

# Copy environment configuration
cp .env.example .env
```

### 2. Configure Environment Variables

Edit the `.env` file with your actual API keys:

```env
# Shopify Configuration
SHOPIFY_SHOP_URL=your-shop.myshopify.com
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
SHOPIFY_API_VERSION=2023-04

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4

# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@aickstudio.com
SENDGRID_FROM_NAME=AICK Studio

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
FRONTEND_URL=http://localhost:5173
CART_ABANDONMENT_MINUTES=15
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

### 4. Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd frontend/aick-cart-dashboard

# Install dependencies
npm install
# or
pnpm install

# Start development server
npm run dev --host
# or
pnpm dev --host
```

The frontend dashboard will be available at:
- **Dashboard**: http://localhost:5173

### 5. Verify Installation

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","service":"AICK Studio Abandoned Cart Recovery Agent","version":"1.0.0"}`

2. **Frontend Access**: Open http://localhost:5173 in your browser
3. **API Documentation**: Open http://localhost:8000/api/docs

## Production Deployment

### Option 1: Docker Deployment

#### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
FROM node:20-alpine as builder

WORKDIR /app
COPY frontend/aick-cart-dashboard/package*.json ./
RUN npm ci

COPY frontend/aick-cart-dashboard/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - SHOPIFY_SHOP_URL=${SHOPIFY_SHOP_URL}
      - SHOPIFY_ACCESS_TOKEN=${SHOPIFY_ACCESS_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
    volumes:
      - ./logs:/app/logs

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

### Option 2: Cloud Platform Deployment

#### Heroku Deployment

**Backend (Heroku)**:
1. Create `Procfile` in backend directory:
   ```
   web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```

2. Deploy:
   ```bash
   heroku create aick-cart-recovery-api
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set SENDGRID_API_KEY=your_key
   # ... set other environment variables
   git subtree push --prefix backend heroku main
   ```

**Frontend (Vercel)**:
1. Connect your GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Deploy automatically on git push

#### AWS Deployment

**Backend (AWS Lambda + API Gateway)**:
```python
# lambda_handler.py
from mangum import Mangum
from api.main import app

handler = Mangum(app)
```

**Frontend (AWS S3 + CloudFront)**:
```bash
# Build and deploy
npm run build
aws s3 sync dist/ s3://your-bucket-name
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

### Option 3: VPS/Server Deployment

#### Using Nginx + Gunicorn

**Backend Setup**:
```bash
# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/aick-cart-recovery.service
```

```ini
[Unit]
Description=AICK Cart Recovery API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/aick-cart-recovery/backend
Environment="PATH=/var/www/aick-cart-recovery/backend/venv/bin"
ExecStart=/var/www/aick-cart-recovery/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/aick-cart-recovery/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## Environment-Specific Configuration

### Development Environment
```env
DEBUG=true
LOG_LEVEL=DEBUG
USE_MOCK_DATA=true
CORS_ORIGINS=["http://localhost:5173"]
```

### Staging Environment
```env
DEBUG=false
LOG_LEVEL=INFO
USE_MOCK_DATA=false
CORS_ORIGINS=["https://staging.aickstudio.com"]
```

### Production Environment
```env
DEBUG=false
LOG_LEVEL=WARNING
USE_MOCK_DATA=false
CORS_ORIGINS=["https://app.aickstudio.com"]
RATE_LIMIT_ENABLED=true
```

## Security Configuration

### API Security
```python
# In production, add authentication middleware
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Security(security)):
    # Implement token verification logic
    if not verify_api_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token
```

### HTTPS Configuration
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
}
```

## Monitoring and Logging

### Application Monitoring
```python
# Add to main.py
import logging
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
    return response
```

### Health Monitoring
```bash
# Add to crontab for health checks
*/5 * * * * curl -f http://localhost:8000/health || echo "API is down" | mail -s "AICK API Alert" admin@aickstudio.com
```

## Backup and Recovery

### Database Backup (if using persistent storage)
```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump aick_cart_recovery > backup_$DATE.sql
aws s3 cp backup_$DATE.sql s3://aick-backups/
```

### Configuration Backup
```bash
# Backup environment and configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env nginx.conf docker-compose.yml
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Find and kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

2. **Permission Denied**:
   ```bash
   # Fix file permissions
   chmod +x scripts/deploy.sh
   chown -R www-data:www-data /var/www/aick-cart-recovery
   ```

3. **CORS Errors**:
   ```python
   # Update CORS settings in main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend-domain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Memory Issues**:
   ```bash
   # Monitor memory usage
   htop
   # Increase swap if needed
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Log Analysis
```bash
# View application logs
tail -f /var/log/aick-cart-recovery/app.log

# Check system logs
journalctl -u aick-cart-recovery.service -f

# Monitor API requests
tail -f /var/log/nginx/access.log | grep "/api/"
```

## Performance Optimization

### Backend Optimization
```python
# Add caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="aick-cache")
```

### Frontend Optimization
```javascript
// Enable code splitting
const Dashboard = lazy(() => import('./components/Dashboard'));
const Analytics = lazy(() => import('./components/Analytics'));
```

### Database Optimization
```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_cart_abandoned_at ON carts(abandoned_at);
CREATE INDEX idx_customer_email ON customers(email);
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (Nginx, HAProxy, or cloud load balancer)
- Deploy multiple backend instances
- Implement session storage (Redis)
- Use CDN for frontend assets

### Vertical Scaling
- Monitor CPU and memory usage
- Optimize database queries
- Implement caching strategies
- Use async processing for heavy tasks

This deployment guide provides comprehensive instructions for deploying the AICK Studio Abandoned Cart Recovery Agent across different environments and platforms. Choose the deployment method that best fits your infrastructure and requirements.

