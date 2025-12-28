# Elite Soccer Player AI Coach - Deployment Guide

## Production Deployment Instructions

This guide covers deploying the complete Elite Soccer Player AI Coach application with all advanced features.

## System Requirements

### Minimum Requirements
- **CPU**: 2 vCPUs
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Docker-compatible environment

### Recommended Requirements
- **CPU**: 4 vCPUs
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS

## Quick Deployment Options

### Option 1: Docker Compose (Recommended)

1. **Clone and Setup**
```bash
git clone <your-repo-url>
cd app/backend
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env file with your configurations
nano .env
```

3. **Set Required Environment Variables**
```bash
export EMERGENT_LLM_KEY="your_actual_emergent_key"
export CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
```

4. **Deploy with Docker Compose**
```bash
docker-compose up -d
```

5. **Verify Deployment**
```bash
curl http://localhost:8001/health
```

### Option 2: Manual Installation

1. **Install Dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv mongodb-server nginx

# CentOS/RHEL
sudo yum install -y python3.11 mongodb-server nginx
```

2. **Setup MongoDB**
```bash
sudo systemctl start mongod
sudo systemctl enable mongod

# Initialize database
mongo soccer_training_db < init-mongo.js
```

3. **Setup Python Environment**
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install emergentintegrations
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

4. **Configure Environment Variables**
```bash
export MONGO_URL="mongodb://localhost:27017"
export EMERGENT_LLM_KEY="your_actual_key"
export ENVIRONMENT="production"
```

5. **Run Application**
```bash
# Development
chmod +x startup.sh
./startup.sh

# Production with systemd
sudo cp soccer-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start soccer-backend
sudo systemctl enable soccer-backend
```

## Environment Variables

### Required Variables
```bash
EMERGENT_LLM_KEY=your_emergent_llm_key          # For AI training program generation
MONGO_URL=mongodb://localhost:27017             # MongoDB connection string
```

### Optional Variables
```bash
DB_NAME=soccer_training_db                      # Database name (default: soccer_training_db)
PORT=8001                                       # Server port (default: 8001)
ENVIRONMENT=production                          # Environment (development/production)
CORS_ORIGINS=https://yourdomain.com             # Allowed origins for CORS
LOG_LEVEL=INFO                                  # Logging level
WORKERS=4                                       # Number of worker processes
```

## Cloud Platform Deployment

### AWS (Amazon Web Services)

1. **EC2 Instance Setup**
```bash
# Launch EC2 instance (t3.medium recommended)
# Security Group: Allow ports 80, 443, 8001

sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose nginx certbot python3-certbot-nginx
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

2. **Deploy Application**
```bash
git clone <your-repo>
cd app/backend
export EMERGENT_LLM_KEY="your_key"
export CORS_ORIGINS="https://yourdomain.com"
docker-compose up -d
```

3. **Setup SSL with Let's Encrypt**
```bash
sudo certbot --nginx -d yourdomain.com
```

### Google Cloud Platform (GCP)

1. **Compute Engine Setup**
```bash
# Create VM instance
gcloud compute instances create soccer-backend \
  --machine-type=e2-medium \
  --zone=us-central1-a \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB
```

2. **Deploy with Cloud Run (Alternative)**
```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/soccer-backend

# Deploy to Cloud Run
gcloud run deploy soccer-backend \
  --image gcr.io/PROJECT_ID/soccer-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars EMERGENT_LLM_KEY=your_key
```

### Digital Ocean

1. **Droplet Setup**
```bash
# Create $20/month droplet (4GB RAM)
# SSH into droplet
ssh root@your_droplet_ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Deploy application
git clone <your-repo>
cd app/backend
export EMERGENT_LLM_KEY="your_key"
docker-compose up -d
```

### Heroku

1. **Heroku Setup**
```bash
# Install Heroku CLI and login
heroku login

# Create application
heroku create soccer-backend-app

# Add MongoDB addon
heroku addons:create mongolab:sandbox

# Set environment variables
heroku config:set EMERGENT_LLM_KEY=your_key
heroku config:set ENVIRONMENT=production

# Deploy
git push heroku main
```

## Database Configuration

### MongoDB Atlas (Cloud)

1. **Setup MongoDB Atlas**
   - Create account at mongodb.com/atlas
   - Create new cluster (M0 free tier for testing)
   - Create database user
   - Whitelist IP addresses

2. **Configure Connection**
```bash
export MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/soccer_training_db"
```

### Local MongoDB

1. **Install MongoDB**
```bash
# Ubuntu
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

2. **Initialize Database**
```bash
mongo soccer_training_db < init-mongo.js
```

## API Endpoints

Once deployed, your API will be available at `http://your-domain:8001` with these endpoints:

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Assessment System
- `POST /api/assessments` - Create player assessment
- `GET /api/assessments` - Get all assessments
- `GET /api/assessments/player/{player_name}` - Get player assessments
- `GET /api/assessments/player/{player_name}/analysis` - Get player analysis

### VO2 Max System
- `POST /api/vo2/benchmarks` - Save VO2 benchmark
- `GET /api/vo2/benchmarks/{player_id}` - Get player VO2 benchmarks
- `GET /api/vo2/calculate` - Calculate VO2 Max using ACSM formulas

### Training System
- `POST /api/training/periodized-programs` - Create periodized program
- `GET /api/training/current-routine/{player_id}` - Get current training routine
- `GET /api/training/programs/{player_id}` - Get training programs

### Progress Tracking
- `POST /api/progress/daily` - Log daily progress
- `GET /api/progress/daily/{player_id}` - Get daily progress
- `GET /api/progress/metrics/{player_id}` - Get performance metrics

## Monitoring & Maintenance

### Health Monitoring

1. **Setup Health Checks**
```bash
# Create health check script
cat > health_check.sh << EOF
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health)
if [ $response -eq 200 ]; then
    echo "$(date): Backend healthy"
else
    echo "$(date): Backend unhealthy (HTTP $response)"
    # Restart service or send alert
fi
EOF

chmod +x health_check.sh

# Add to crontab for every 5 minutes
echo "*/5 * * * * /path/to/health_check.sh >> /var/log/health_check.log" | crontab -
```

### Backup Strategy

1. **MongoDB Backup**
```bash
# Create backup script
cat > backup_mongodb.sh << EOF
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mongodump --uri="$MONGO_URL" --out="/backups/mongodb_$DATE"
# Upload to cloud storage (AWS S3, Google Cloud Storage, etc.)
EOF

# Schedule daily backups
echo "0 2 * * * /path/to/backup_mongodb.sh" | crontab -
```

### Log Management

1. **Setup Log Rotation**
```bash
sudo tee /etc/logrotate.d/soccer-backend << EOF
/var/log/soccer-backend/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    create 0644 appuser appuser
    postrotate
        systemctl reload soccer-backend
    endscript
}
EOF
```

## Security Considerations

### 1. Environment Security
```bash
# Secure environment variables
chmod 600 .env

# Use secrets management in production
export EMERGENT_LLM_KEY=$(cat /run/secrets/emergent_key)
```

### 2. Database Security
```bash
# Enable MongoDB authentication
mongo
> use admin
> db.createUser({user: "admin", pwd: "secure_password", roles: ["root"]})
> exit

# Update MongoDB config
sudo nano /etc/mongod.conf
# Add: security.authorization: enabled
```

### 3. Network Security
```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8001/tcp
sudo ufw enable
```

## Performance Optimization

### 1. Database Indexing
The `init-mongo.js` script creates optimal indexes for all collections.

### 2. Caching
```python
# Add Redis caching for frequent queries
pip install redis

# In your application:
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
```

### 3. Load Balancing
```bash
# Nginx configuration for load balancing
upstream soccer_backend {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location /api/ {
        proxy_pass http://soccer_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check logs
sudo tail -f /var/log/mongodb/mongod.log

# Test connection
mongo --eval "db.adminCommand('ping')"
```

2. **Emergent LLM Key Issues**
```bash
# Verify key is set
echo $EMERGENT_LLM_KEY

# Test LLM integration
curl -X POST http://localhost:8001/api/training/programs \
  -H "Content-Type: application/json" \
  -d '{"player_id":"test","program_type":"AI_Generated"}'
```

3. **Memory Issues**
```bash
# Monitor memory usage
free -h
htop

# Optimize MongoDB memory usage
# Add to /etc/mongod.conf:
# storage.wiredTiger.engineConfig.cacheSizeGB: 2
```

### Logs Location
- Application logs: `/var/log/soccer-backend/`
- MongoDB logs: `/var/log/mongodb/mongod.log`
- Nginx logs: `/var/log/nginx/`
- System logs: `journalctl -u soccer-backend`

## Support

For deployment support:
1. Check the logs first
2. Verify all environment variables are set
3. Test MongoDB connectivity
4. Ensure all ports are accessible
5. Check system resources (CPU, RAM, disk)

## Production Checklist

- [ ] Environment variables configured
- [ ] MongoDB indexes created
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Health monitoring setup
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Performance monitoring enabled
- [ ] Error tracking setup
- [ ] Documentation updated

Your Elite Soccer Player AI Coach backend is now ready for production deployment! 🚀⚽