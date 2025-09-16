# Render Deployment Guide

Complete guide for deploying your Zehmo Business Management System on Render.

## 🚀 Quick Deployment Steps

### 1. **Prepare Your Repository**
✅ Your repository is already configured with:
- `requirements.txt` with all dependencies
- `Procfile` for deployment
- `runtime.txt` for Python version
- `.env` template for configuration

### 2. **Create Render Account**
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub (recommended)
3. Connect your GitHub account

### 3. **Deploy Web Service**
1. **Create New Web Service**:
   - Dashboard → "New" → "Web Service"
   - Connect your GitHub repository: `zehmo/Zehmo-Business-Managment-System`
   - Branch: `main`

2. **Configure Service**:
   ```
   Name: zehmo-business-system
   Environment: Python 3
   Region: Choose closest to your users
   Branch: main
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

3. **Choose Plan**:
   - **Free Tier**: $0/month (sleeps after 15min inactivity)
   - **Starter**: $7/month (always on, custom domains)
   - **Standard**: $25/month (more resources)

## 🔧 Environment Variables Setup

### Required Environment Variables
In Render Dashboard → Your Service → Environment:

```bash
# Flask Configuration
SECRET_KEY=dZlitGXRwFyM-_FgM7gBWPIhnOsxUmAJNOnbjB4b5yM
FLASK_ENV=production

# Database (choose one option below)
# Option 1: Render PostgreSQL
DATABASE_URL=postgresql://username:password@hostname:port/database

# Option 2: External MySQL (PlanetScale/Railway)
# DATABASE_URL=mysql+pymysql://username:password@hostname:port/database

# Server Configuration
PORT=10000

# Optional: Admin User (for initial setup)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your_secure_admin_password
```

### How to Add Environment Variables
1. Go to your service dashboard
2. Click "Environment" tab
3. Click "Add Environment Variable"
4. Add each variable one by one:
   - Key: `SECRET_KEY`
   - Value: `dZlitGXRwFyM-_FgM7gBWPIhnOsxUmAJNOnbjB4b5yM`
   - Click "Save Changes"

## 🗄️ Database Setup Options

### Option A: Render PostgreSQL (Recommended)

1. **Create PostgreSQL Database**:
   - Dashboard → "New" → "PostgreSQL"
   - Name: `zehmo-database`
   - Database Name: `zehmo`
   - User: `zehmo_user`
   - Region: Same as your web service
   - Plan: Free (1GB) or Starter ($7/month)

2. **Get Connection Details**:
   - Go to database dashboard
   - Copy "External Database URL"
   - Add to environment variables as `DATABASE_URL`

3. **Update requirements.txt** (add if missing):
   ```
   psycopg2-binary==2.9.7
   ```

### Option B: External Database (PlanetScale/Railway)

If using external database, just add the `DATABASE_URL` to environment variables.

## 🔄 Deployment Process

### Automatic Deployment
Render automatically deploys when you push to your `main` branch:

```bash
# Make changes to your code
git add .
git commit -m "Update for production"
git push origin main

# Render will automatically:
# 1. Pull latest code
# 2. Run build command
# 3. Start your application
```

### Manual Deployment
1. Go to your service dashboard
2. Click "Manual Deploy" → "Deploy latest commit"
3. Monitor build logs for any issues

## 🛠️ Post-Deployment Setup

### 1. Initialize Database
After first deployment, initialize your database:

**Option A: Using Render Shell**
1. Service Dashboard → "Shell" tab
2. Run: `python setup_database.py`

**Option B: Using Local Script**
1. Set `DATABASE_URL` in your local `.env`
2. Run: `python setup_database.py`

### 2. Create Admin User
The setup script will create an admin user with credentials from environment variables.

### 3. Test Your Application
1. Visit your Render URL: `https://your-service-name.onrender.com`
2. Login with admin credentials
3. Test all functionality

## 🔒 Security Configuration

### SSL/HTTPS
- Render provides free SSL certificates
- All traffic is automatically encrypted
- Custom domains supported on paid plans

### Environment Security
```bash
# Production security settings
FLASK_ENV=production
FLASK_DEBUG=False

# Database security
# Use strong passwords
# Enable SSL connections
```

### Secrets Management
- Never commit secrets to git
- Use Render's environment variables
- Rotate secrets regularly
- Use different secrets for different environments

## 📊 Monitoring & Logs

### View Logs
1. Service Dashboard → "Logs" tab
2. Real-time log streaming
3. Filter by log level

### Monitor Performance
1. Service Dashboard → "Metrics" tab
2. CPU, Memory, Response time
3. Request volume and errors

### Health Checks
Render automatically monitors your app:
- HTTP health checks on `/`
- Automatic restarts on failures
- Email notifications on issues

## 🚨 Troubleshooting

### Common Issues

**Build Failures**:
```bash
# Check build logs for:
# - Missing dependencies in requirements.txt
# - Python version compatibility
# - Build command errors
```

**Application Won't Start**:
```bash
# Check logs for:
# - Missing environment variables
# - Database connection issues
# - Import errors
```

**Database Connection Issues**:
```bash
# Verify:
# - DATABASE_URL format is correct
# - Database is running and accessible
# - Credentials are valid
```

### Debug Commands
```bash
# Test database connection
python -c "from app import db; print('DB Connected!' if db.engine.connect() else 'DB Failed!')"

# Check environment variables
python -c "import os; print('SECRET_KEY:', 'SET' if os.getenv('SECRET_KEY') else 'MISSING')"

# Test Flask app
python -c "from app import app; print('App created successfully!')"
```

## 🔄 Updates & Maintenance

### Regular Updates
1. **Code Updates**: Push to main branch
2. **Dependencies**: Update requirements.txt
3. **Database**: Run migrations as needed
4. **Environment**: Update variables in dashboard

### Backup Strategy
- **Database**: Render PostgreSQL includes automatic backups
- **Code**: GitHub repository serves as backup
- **Environment**: Document all environment variables

### Scaling
- **Vertical**: Upgrade to higher tier plans
- **Horizontal**: Use Render's load balancing
- **Database**: Upgrade database plan as needed

## 📞 Support & Resources

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Community**: [Render Community](https://community.render.com)
- **Status**: [status.render.com](https://status.render.com)
- **Support**: Available on paid plans

---

## 🎉 Success Checklist

- [ ] Repository connected to Render
- [ ] Environment variables configured
- [ ] Database created and connected
- [ ] Application deployed successfully
- [ ] Database initialized with tables
- [ ] Admin user created
- [ ] Application accessible via URL
- [ ] All features working correctly

**Your Zehmo Business Management System is now live! 🚀**