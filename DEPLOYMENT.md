# Deployment Guide

This guide covers different deployment options for the ATS Resume Scoring Agent.

## Local Development

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps
```bash
# Clone the repository
git clone <repository-url>
cd workspace

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

Access at `http://localhost:8000`

## Production Deployment

### Option 1: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
```

Build and run:
```bash
# Build image
docker build -t ats-resume-scorer .

# Run container
docker run -p 8000:8000 ats-resume-scorer
```

### Option 2: Cloud Platform Deployment

#### Heroku

1. Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

#### Google Cloud Run

1. Create `Dockerfile` (see above)

2. Deploy:
```bash
gcloud run deploy ats-scorer \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### AWS EC2

1. Launch EC2 instance (Ubuntu)
2. SSH into instance
3. Install dependencies:
```bash
sudo apt update
sudo apt install python3 python3-pip
```
4. Clone repository and install
5. Use systemd service for auto-restart

Create `/etc/systemd/system/ats-scorer.service`:
```ini
[Unit]
Description=ATS Resume Scoring Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/workspace
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ats-scorer
sudo systemctl start ats-scorer
```

#### DigitalOcean App Platform

1. Connect your GitHub repository
2. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `python main.py`
3. Deploy automatically on push

### Option 3: Serverless Deployment

#### Vercel

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Create `vercel.json`:
```json
{
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ]
}
```

3. Deploy:
```bash
vercel
```

## Environment Configuration

### Environment Variables

For production, consider using environment variables:

```python
# config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "ATS Resume Scoring Agent"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB
    
settings = Settings()
```

## Reverse Proxy Setup (Nginx)

For production deployments with Nginx:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 10M;
    }
}
```

## SSL/HTTPS Setup

### Using Certbot (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## Performance Optimization

### 1. Use Gunicorn for Production

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 2. Enable Compression

Add to `main.py`:
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 3. Add CORS for API Access

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Monitoring and Logging

### Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### Health Checks

Already implemented at `/api/health`

Monitor with:
```bash
curl http://localhost:8000/api/health
```

## Scaling Considerations

1. **Horizontal Scaling**: Deploy multiple instances behind a load balancer
2. **Caching**: Add Redis for frequently accessed data
3. **CDN**: Use CDN for static assets
4. **Database**: Add PostgreSQL if implementing user accounts
5. **Queue System**: Use Celery/RabbitMQ for async processing

## Security Best Practices

1. **Rate Limiting**: Implement rate limiting for API endpoints
2. **File Size Limits**: Already implemented (configurable)
3. **File Type Validation**: Already implemented
4. **HTTPS**: Always use HTTPS in production
5. **Security Headers**: Add security headers middleware
6. **Input Validation**: Already implemented with Pydantic

## Backup and Maintenance

- **Code Backups**: Use Git version control
- **Dependency Updates**: Regularly update `requirements.txt`
- **Security Patches**: Monitor for security updates
- **Logs**: Implement log rotation

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Dependencies Installation Fails
```bash
# Upgrade pip
pip install --upgrade pip
# Install with verbose output
pip install -v -r requirements.txt
```

### Permission Denied
```bash
# Make start script executable
chmod +x start.sh
```

## Cost Optimization

### Free Tier Options
- **Render**: Free tier with automatic deploys
- **Railway**: Free tier for small projects
- **Fly.io**: Free tier with global deployment
- **Heroku**: Limited free tier

### Paid Options
- **DigitalOcean**: $5/month droplet
- **AWS Lightsail**: $3.50/month instance
- **Google Cloud Run**: Pay per request (very cost-effective)

## Conclusion

Choose the deployment option that best fits your needs:
- **Development**: Local setup with `python main.py`
- **Small Scale**: Docker container on VPS
- **Production**: Cloud platform with auto-scaling
- **Enterprise**: Kubernetes cluster with load balancing

For most use cases, starting with a simple VPS deployment or cloud platform is recommended.
