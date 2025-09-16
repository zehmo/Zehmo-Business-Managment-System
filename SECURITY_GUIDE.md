# Security Best Practices Guide

Comprehensive security guide for your Zehmo Business Management System in production.

## 🔐 Environment Variables Security

### Secret Key Management
```bash
# ✅ GOOD: Strong, randomly generated secret key
SECRET_KEY=dZlitGXRwFyM-_FgM7gBWPIhnOsxUmAJNOnbjB4b5yM

# ❌ BAD: Weak or default secret keys
SECRET_KEY=mysecretkey
SECRET_KEY=dev
SECRET_KEY=123456
```

### Environment Variable Rules
1. **Never commit `.env` files to git**
2. **Use different secrets for each environment**
3. **Rotate secrets regularly (every 90 days)**
4. **Use strong, random values**
5. **Document required variables**

### Generating Secure Secrets
```python
# Generate new SECRET_KEY
import secrets
print(secrets.token_urlsafe(32))

# Generate database passwords
import secrets
import string
chars = string.ascii_letters + string.digits + '!@#$%^&*'
password = ''.join(secrets.choice(chars) for _ in range(16))
print(password)
```

## 🗄️ Database Security

### Connection Security
```bash
# ✅ GOOD: SSL enabled, specific user
DATABASE_URL=postgresql://zehmo_user:strong_password@host:5432/zehmo_db?sslmode=require

# ❌ BAD: No SSL, root user
DATABASE_URL=postgresql://root:123@host:5432/db?sslmode=disable
```

### Database Best Practices
1. **Create dedicated database user** (not root/admin)
2. **Grant minimal required permissions**
3. **Enable SSL/TLS connections**
4. **Use strong passwords (16+ characters)**
5. **Enable database backups**
6. **Monitor access logs**
7. **Keep database software updated**

### User Permissions
```sql
-- Create dedicated user with limited permissions
CREATE USER 'zehmo_user'@'%' IDENTIFIED BY 'strong_random_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON zehmo_db.* TO 'zehmo_user'@'%';
FLUSH PRIVILEGES;
```

## 🌐 Application Security

### Flask Security Configuration
```python
# In your app.py or config
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY'),
    SESSION_COOKIE_SECURE=True,      # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,    # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),  # Session timeout
    WTF_CSRF_ENABLED=True,           # CSRF protection
    WTF_CSRF_TIME_LIMIT=3600,        # CSRF token timeout
)
```

### Password Security
```python
# Strong password requirements
MIN_PASSWORD_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_NUMBERS = True
REQUIRE_SPECIAL_CHARS = True

# Password hashing (already implemented in your app)
from werkzeug.security import generate_password_hash, check_password_hash

# Hash passwords before storing
hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
```

### Input Validation
```python
# Validate all user inputs
from wtforms.validators import DataRequired, Length, Email, Regexp

class UserForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20),
        Regexp(r'^[a-zA-Z0-9_]+$', message='Only letters, numbers, and underscores allowed')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
```

## 🔒 Authentication & Authorization

### Session Management
```python
# Secure session configuration
from datetime import timedelta

app.config.update(
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    SESSION_REFRESH_EACH_REQUEST=True,
)

# Logout on browser close
@app.before_request
def make_session_permanent():
    session.permanent = True
```

### Role-Based Access Control
```python
# Implement proper authorization checks
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# Use on sensitive routes
@app.route('/admin/users')
@login_required
@admin_required
def manage_users():
    # Admin-only functionality
    pass
```

### Failed Login Protection
```python
# Implement rate limiting for login attempts
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic with rate limiting
    pass
```

## 🌍 Production Environment Security

### HTTPS Configuration
```bash
# Render automatically provides HTTPS
# For custom domains, ensure SSL certificate is valid

# Force HTTPS redirects
app.config['PREFERRED_URL_SCHEME'] = 'https'
```

### Security Headers
```python
# Add security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

### Error Handling
```python
# Don't expose sensitive information in errors
app.config['DEBUG'] = False
app.config['TESTING'] = False

@app.errorhandler(500)
def internal_error(error):
    # Log error details securely
    app.logger.error(f'Server Error: {error}')
    # Return generic error message to user
    return render_template('errors/500.html'), 500
```

## 📊 Logging & Monitoring

### Security Logging
```python
import logging
from logging.handlers import RotatingFileHandler

# Configure secure logging
if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

# Log security events
@app.route('/login', methods=['POST'])
def login():
    if login_successful:
        app.logger.info(f'Successful login for user: {username}')
    else:
        app.logger.warning(f'Failed login attempt for user: {username} from IP: {request.remote_addr}')
```

### Monitor for Suspicious Activity
```python
# Track failed login attempts
failed_attempts = {}

@app.before_request
def track_failed_logins():
    ip = request.remote_addr
    if request.endpoint == 'login' and request.method == 'POST':
        if ip in failed_attempts:
            if failed_attempts[ip] > 5:
                app.logger.warning(f'Multiple failed login attempts from IP: {ip}')
                abort(429)  # Too Many Requests
```

## 🔄 Regular Security Maintenance

### Monthly Tasks
- [ ] Review access logs for suspicious activity
- [ ] Update dependencies to latest secure versions
- [ ] Check for security advisories
- [ ] Review user permissions and roles
- [ ] Test backup and recovery procedures

### Quarterly Tasks
- [ ] Rotate SECRET_KEY and database passwords
- [ ] Security audit of code changes
- [ ] Penetration testing (if applicable)
- [ ] Review and update security policies
- [ ] Update SSL certificates (if custom)

### Dependency Security
```bash
# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies regularly
pip list --outdated
pip install --upgrade package_name

# Use specific versions in requirements.txt
Flask==2.3.3
SQLAlchemy==2.0.21
```

## 🚨 Incident Response

### Security Breach Response
1. **Immediate Actions**:
   - Change all passwords and secret keys
   - Review access logs
   - Disable compromised accounts
   - Document the incident

2. **Investigation**:
   - Identify attack vector
   - Assess data exposure
   - Check for ongoing threats
   - Preserve evidence

3. **Recovery**:
   - Patch vulnerabilities
   - Restore from clean backups
   - Monitor for continued attacks
   - Update security measures

### Emergency Contacts
- **Hosting Provider**: Render support
- **Database Provider**: Provider support
- **Domain Registrar**: Registrar support
- **Security Team**: Internal contacts

## 📋 Security Checklist

### Pre-Deployment
- [ ] Strong SECRET_KEY generated
- [ ] Database user with minimal permissions
- [ ] SSL/TLS enabled for database
- [ ] Debug mode disabled
- [ ] Error handling configured
- [ ] Security headers implemented
- [ ] Input validation in place
- [ ] Rate limiting configured
- [ ] Logging configured

### Post-Deployment
- [ ] HTTPS working correctly
- [ ] Security headers present
- [ ] Login rate limiting working
- [ ] Error pages don't expose sensitive info
- [ ] Logs are being generated
- [ ] Database backups enabled
- [ ] Monitoring alerts configured

### Ongoing
- [ ] Regular dependency updates
- [ ] Log review and analysis
- [ ] Security training for team
- [ ] Incident response plan tested
- [ ] Regular security assessments

---

## 🛡️ Security Resources

- **OWASP Top 10**: [owasp.org/www-project-top-ten](https://owasp.org/www-project-top-ten/)
- **Flask Security**: [flask.palletsprojects.com/security](https://flask.palletsprojects.com/security/)
- **Python Security**: [python.org/dev/security](https://python.org/dev/security/)
- **Database Security**: Provider-specific documentation

**Remember: Security is an ongoing process, not a one-time setup!**