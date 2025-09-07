# Deployment Guide

## 🚀 Production Deployment Instructions

This guide provides comprehensive instructions for deploying the RAG Analytics system in production environments.

## 📋 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended), Windows Server, or macOS
- **Python**: Version 3.9 or higher
- **Node.js**: Version 16 or higher
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 20GB free space
- **Network**: Stable internet connection for API calls

### Required Accounts
- **Google Gemini API**: Production API key
- **Domain/Server**: For hosting the application
- **SSL Certificate**: For HTTPS (recommended)

## 🏗️ Architecture Overview

### Production Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │────│   Web Server    │────│   Application   │
│   (Nginx)       │    │   (Nginx)       │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Frontend      │
                       │   (React)       │
                       └─────────────────┘
```

### Component Deployment
- **Frontend**: Static files served by Nginx
- **Backend**: FastAPI application with Uvicorn
- **Database**: PostgreSQL/MySQL (optional)
- **Reverse Proxy**: Nginx for load balancing and SSL

## 🔧 Backend Deployment

### 1. Server Setup

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3.9 python3.9-pip python3.9-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Nginx
sudo apt install nginx -y

# Install system dependencies
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y
```

#### CentOS/RHEL
```bash
# Update system
sudo yum update -y

# Install Python
sudo yum install python39 python39-pip -y

# Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install nodejs -y

# Install Nginx
sudo yum install nginx -y
```

### 2. Application Setup

#### Create Application Directory
```bash
# Create application directory
sudo mkdir -p /opt/rag-analytics
sudo chown $USER:$USER /opt/rag-analytics
cd /opt/rag-analytics

# Clone repository
git clone <repository-url> .

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Environment Configuration
```bash
# Create production environment file
cp .env.example .env.production

# Edit environment file
nano .env.production
```

**Production Environment Variables:**
```env
# API Configuration
GOOGLE_API_KEY=your_production_google_api_key
HOST=0.0.0.0
PORT=8000
DEBUG=false
RELOAD=false

# Database Configuration (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/rag_analytics
REDIS_URL=redis://localhost:6379

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
MAX_FILE_SIZE_MB=50
EXECUTION_TIMEOUT_SECONDS=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Feature Flags
ENABLE_LLM_AGENT=true
ENABLE_EMBEDDINGS=true
ENABLE_DATABASE=true
ENABLE_VISUALIZATION=true
ENABLE_BACKGROUND_INDEXING=true

# Resource Limits
MAX_ROWS_INDEXABLE=10000
MAX_TOKENS_LLM=4000
TOP_K=5
MAX_CONTEXT_LENGTH=2000

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
FAISS_DIM=384
HUGGINGFACE_CACHE_DIR=/opt/rag-analytics/cache/huggingface
```

### 3. Systemd Service Configuration

#### Create Service File
```bash
sudo nano /etc/systemd/system/rag-analytics.service
```

**Service Configuration:**
```ini
[Unit]
Description=RAG Analytics FastAPI Application
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/rag-analytics
Environment=PATH=/opt/rag-analytics/venv/bin
EnvironmentFile=/opt/rag-analytics/.env.production
ExecStart=/opt/rag-analytics/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable rag-analytics

# Start service
sudo systemctl start rag-analytics

# Check status
sudo systemctl status rag-analytics
```

### 4. Logging Configuration

#### Create Log Directory
```bash
sudo mkdir -p /var/log/rag-analytics
sudo chown www-data:www-data /var/log/rag-analytics
```

#### Log Rotation
```bash
sudo nano /etc/logrotate.d/rag-analytics
```

**Log Rotation Configuration:**
```
/var/log/rag-analytics/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload rag-analytics
    endscript
}
```

## 🎨 Frontend Deployment

### 1. Build Production Version

#### Install Dependencies
```bash
cd /opt/rag-analytics/src
npm install
```

#### Build Application
```bash
# Create production build
npm run build

# The build will be created in the 'build' directory
```

### 2. Nginx Configuration

#### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/rag-analytics
```

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Frontend (React App)
    location / {
        root /opt/rag-analytics/src/build;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin $http_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
        add_header Access-Control-Expose-Headers "Content-Length,Content-Range" always;
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin $http_origin;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
            add_header Access-Control-Max-Age 1728000;
            add_header Content-Type 'text/plain; charset=utf-8';
            add_header Content-Length 0;
            return 204;
        }
    }
    
    # File upload size limit
    client_max_body_size 50M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
}
```

#### Enable Site
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rag-analytics /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## 🔒 Security Configuration

### 1. Firewall Setup

#### UFW (Ubuntu)
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Check status
sudo ufw status
```

#### Firewalld (CentOS/RHEL)
```bash
# Start and enable firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

# Allow HTTP and HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Reload firewall
sudo firewall-cmd --reload
```

### 2. SSL Certificate

#### Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Manual SSL Certificate
```bash
# Place certificate files
sudo cp your-certificate.crt /etc/ssl/certs/
sudo cp your-private.key /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/your-private.key
```

### 3. Application Security

#### Environment Security
```bash
# Secure environment file
sudo chmod 600 /opt/rag-analytics/.env.production
sudo chown www-data:www-data /opt/rag-analytics/.env.production
```

#### File Permissions
```bash
# Set proper permissions
sudo chown -R www-data:www-data /opt/rag-analytics
sudo chmod -R 755 /opt/rag-analytics
sudo chmod 600 /opt/rag-analytics/.env.production
```

## 📊 Monitoring and Logging

### 1. Application Monitoring

#### Health Check Endpoint
```bash
# Test health endpoint
curl https://yourdomain.com/api/health

# Expected response
{
  "status": "healthy",
  "message": "RAG Analytics API is running",
  "version": "1.0.0",
  "features": {
    "excel_upload": true,
    "llm_queries": true,
    "embeddings": true,
    "database_connections": true,
    "visualizations": true,
    "ai_processing": true
  },
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

#### System Monitoring
```bash
# Monitor service status
sudo systemctl status rag-analytics

# View logs
sudo journalctl -u rag-analytics -f

# Monitor resource usage
htop
```

### 2. Log Management

#### Application Logs
```bash
# View application logs
tail -f /var/log/rag-analytics/app.log

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

#### Log Analysis
```bash
# Install log analysis tools
sudo apt install logwatch -y

# Configure logwatch
sudo nano /etc/logwatch/conf/logwatch.conf
```

## 🔄 Backup and Recovery

### 1. Application Backup

#### Backup Script
```bash
sudo nano /opt/rag-analytics/backup.sh
```

**Backup Script:**
```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/rag-analytics"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/rag-analytics"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz -C $APP_DIR .

# Backup configuration files
cp /etc/nginx/sites-available/rag-analytics $BACKUP_DIR/nginx_config_$DATE
cp /etc/systemd/system/rag-analytics.service $BACKUP_DIR/service_config_$DATE

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/app_$DATE.tar.gz"
```

#### Schedule Backups
```bash
# Make script executable
sudo chmod +x /opt/rag-analytics/backup.sh

# Add to crontab
sudo crontab -e
# Add: 0 2 * * * /opt/rag-analytics/backup.sh
```

### 2. Recovery Process

#### Restore from Backup
```bash
# Stop services
sudo systemctl stop rag-analytics
sudo systemctl stop nginx

# Restore application
cd /opt/rag-analytics
sudo tar -xzf /opt/backups/rag-analytics/app_YYYYMMDD_HHMMSS.tar.gz

# Restore configuration
sudo cp /opt/backups/rag-analytics/nginx_config_YYYYMMDD /etc/nginx/sites-available/rag-analytics
sudo cp /opt/backups/rag-analytics/service_config_YYYYMMDD /etc/systemd/system/rag-analytics.service

# Restart services
sudo systemctl daemon-reload
sudo systemctl start rag-analytics
sudo systemctl start nginx
```

## 🚀 Performance Optimization

### 1. Application Optimization

#### Gunicorn Configuration
```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn configuration
sudo nano /opt/rag-analytics/gunicorn.conf.py
```

**Gunicorn Configuration:**
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

#### Update Service File
```ini
[Service]
ExecStart=/opt/rag-analytics/venv/bin/gunicorn -c /opt/rag-analytics/gunicorn.conf.py app:app
```

### 2. Database Optimization (if using)

#### PostgreSQL Configuration
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create database
sudo -u postgres createdb rag_analytics

# Create user
sudo -u postgres createuser --interactive
```

#### Database Connection Pooling
```python
# In your application
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

## 🔧 Maintenance

### 1. Regular Maintenance Tasks

#### Update Dependencies
```bash
# Update Python packages
cd /opt/rag-analytics
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Update Node.js packages
cd src
npm update
npm run build
```

#### System Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Restart services
sudo systemctl restart rag-analytics
sudo systemctl restart nginx
```

### 2. Monitoring Commands

#### Service Status
```bash
# Check all services
sudo systemctl status rag-analytics nginx

# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top
```

#### Log Monitoring
```bash
# Monitor application logs
sudo journalctl -u rag-analytics -f

# Monitor Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🆘 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status rag-analytics

# Check logs
sudo journalctl -u rag-analytics -n 50

# Check configuration
sudo nginx -t
```

#### High Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Restart service
sudo systemctl restart rag-analytics
```

#### SSL Certificate Issues
```bash
# Check certificate
sudo certbot certificates

# Renew certificate
sudo certbot renew --dry-run
```

### Emergency Procedures

#### Quick Restart
```bash
# Restart all services
sudo systemctl restart rag-analytics nginx

# Check status
sudo systemctl status rag-analytics nginx
```

#### Rollback
```bash
# Stop services
sudo systemctl stop rag-analytics nginx

# Restore from backup
cd /opt/rag-analytics
sudo tar -xzf /opt/backups/rag-analytics/app_latest.tar.gz

# Restart services
sudo systemctl start rag-analytics nginx
```

---

*This deployment guide provides comprehensive instructions for production deployment. For development setup, see the [Getting Started Guide](../learning/getting-started.md).*
