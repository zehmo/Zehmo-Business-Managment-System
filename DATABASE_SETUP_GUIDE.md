# Database Setup Guide for Production

This guide will help you set up a remote database for your Zehmo Business Management System.

## 🎯 Quick Start - Recommended Options

### 1. **Render (Easiest - Same Platform)**
- **PostgreSQL**: Free tier available, easy integration
- **Steps**:
  1. Go to [Render Dashboard](https://dashboard.render.com)
  2. Click "New" → "PostgreSQL"
  3. Choose your plan (Free tier: 1GB storage)
  4. Copy the **External Database URL**
  5. Add to your `.env`: `DATABASE_URL=postgresql://...`

### 2. **PlanetScale (MySQL - Recommended)**
- **MySQL**: Serverless, generous free tier
- **Steps**:
  1. Sign up at [PlanetScale](https://planetscale.com)
  2. Create new database
  3. Go to "Connect" → "General" → "Connect with: Prisma"
  4. Copy the connection string
  5. Convert format: `mysql+pymysql://username:password@host/database?sslmode=require`

### 3. **Railway (PostgreSQL/MySQL)**
- **Both options available**: PostgreSQL or MySQL
- **Steps**:
  1. Sign up at [Railway](https://railway.app)
  2. Create new project → Add PostgreSQL/MySQL
  3. Go to database service → "Connect" tab
  4. Copy the connection URL
  5. Add to `.env`: `DATABASE_URL=postgresql://...` or `DATABASE_URL=mysql+pymysql://...`

## 📋 Detailed Setup Instructions

### Option A: Render PostgreSQL (Recommended for Render deployment)

```bash
# 1. Create PostgreSQL database on Render
# 2. Get connection details from Render dashboard
# 3. Format: postgresql://username:password@hostname:port/database

# Example:
DATABASE_URL=postgresql://zehmo_user:abc123@dpg-xyz.oregon-postgres.render.com:5432/zehmo_db
```

### Option B: PlanetScale MySQL (Best Performance)

```bash
# 1. Create database on PlanetScale
# 2. Get connection string from "Connect" section
# 3. Format: mysql+pymysql://username:password@hostname:port/database?sslmode=require

# Example:
DATABASE_URL=mysql+pymysql://abc123:pscale_pw_xyz@aws.connect.psdb.cloud:3306/zehmo?sslmode=require
```

### Option C: Railway Database

```bash
# PostgreSQL Example:
DATABASE_URL=postgresql://postgres:password123@containers-us-west-xyz.railway.app:5432/railway

# MySQL Example:
DATABASE_URL=mysql+pymysql://root:password123@containers-us-west-xyz.railway.app:3306/railway
```

## 🔧 Configuration Steps

### Step 1: Choose Your Database Provider
Pick one from the options above based on your needs:
- **Render**: If deploying on Render (same ecosystem)
- **PlanetScale**: Best for MySQL, excellent performance
- **Railway**: Good all-around option

### Step 2: Update Your .env File
```bash
# Open your .env file and uncomment/update the DATABASE_URL
# Replace with your actual connection string
DATABASE_URL=your_database_url_here
```

### Step 3: Install Database Dependencies
Your `requirements.txt` already includes:
```
PyMySQL==1.1.0        # For MySQL connections
mysqlclient==2.2.0    # MySQL client
psycopg2-binary       # Add this for PostgreSQL
```

### Step 4: Initialize Database
```bash
# Run the setup script to create tables
python setup_database.py
```

## 🚀 Provider-Specific Instructions

### Render PostgreSQL Setup
1. **Create Database**:
   - Dashboard → New → PostgreSQL
   - Name: `zehmo-database`
   - Region: Choose closest to your app
   - Plan: Free (1GB) or Starter ($7/month)

2. **Get Connection URL**:
   - Go to your database dashboard
   - Copy "External Database URL"
   - Format: `postgresql://user:pass@host:port/db`

3. **Security**: Render handles SSL automatically

### PlanetScale MySQL Setup
1. **Create Database**:
   - New Database → Name: `zehmo`
   - Region: Choose closest region
   - Plan: Hobby (Free) or Scaler Pro

2. **Get Connection String**:
   - Database → Connect → General
   - Select "Prisma" format
   - Copy and modify for SQLAlchemy format

3. **Branch Management**: Use `main` branch for production

### Railway Setup
1. **Create Project**:
   - New Project → Deploy from GitHub
   - Add Database → PostgreSQL or MySQL

2. **Get Variables**:
   - Database service → Variables tab
   - Copy `DATABASE_URL` or construct from individual vars

3. **Networking**: Railway handles internal networking

## 🔒 Security Best Practices

### Environment Variables
- Never commit `.env` to git
- Use different credentials for dev/staging/prod
- Rotate passwords regularly

### Connection Security
- Always use SSL/TLS connections
- Use connection pooling for better performance
- Set connection timeouts

### Database Security
- Create dedicated database user (not root/admin)
- Grant only necessary permissions
- Enable database backups
- Monitor database access logs

## 🛠️ Troubleshooting

### Common Issues

**Connection Refused**:
```bash
# Check if DATABASE_URL is correctly formatted
# Verify database is running and accessible
# Check firewall/security group settings
```

**SSL Certificate Issues**:
```bash
# For MySQL, add SSL parameters:
DATABASE_URL=mysql+pymysql://user:pass@host:port/db?ssl_ca=&ssl_disabled=False

# For PostgreSQL, add SSL mode:
DATABASE_URL=postgresql://user:pass@host:port/db?sslmode=require
```

**Authentication Failed**:
- Double-check username and password
- Ensure database user has proper permissions
- Check if IP whitelist is configured correctly

### Testing Connection
```python
# Test your database connection
python -c "from app import app, db; app.app_context().push(); print('Database connected successfully!' if db.engine.connect() else 'Connection failed')"
```

## 📞 Support Resources

- **Render**: [Render Docs](https://render.com/docs/databases)
- **PlanetScale**: [PlanetScale Docs](https://planetscale.com/docs)
- **Railway**: [Railway Docs](https://docs.railway.app/databases)
- **Flask-SQLAlchemy**: [SQLAlchemy Docs](https://flask-sqlalchemy.palletsprojects.com/)

---

**Next Steps**: After setting up your database, run `python setup_database.py` to initialize tables and create your admin user.