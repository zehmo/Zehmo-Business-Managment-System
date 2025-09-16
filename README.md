# Business Management System

A full-stack web application for recording sales (jobs) and expenditures in your business. Built with Flask, SQLite, and Bootstrap.

## Features

### 🔐 Authentication
- Secure login system with role-based access control
- Admin and Normal user roles
- Password change functionality
- No registration (users added manually to database)

### 💼 Job Management (Sales)
- Add jobs with multiple items per transaction
- Customer name, quantity, description, price tracking
- Auto-calculated totals (Quantity × Price)
- Job status: Completed or Incomplete
- Auto-tracking of date/time and user who created the job
- Modal-based forms for easy data entry

### 💰 Expenditure Management
- Track business expenditures and procurement
- Quantity, description, amount used, and auto-calculated totals
- Sortable and filterable tables
- Admin users can edit/delete entries
- Highlight today's expenditures

### 📊 Dashboard & Analytics
- Overview of jobs completed (today, week, month)
- Track incomplete jobs
- Total expenditure summaries
- Monthly inflow vs outflow charts
- Net balance calculations (Revenue - Expenditures)

### 📈 Reporting Features
- Export jobs and expenditures to Excel/PDF
- Monthly inflow vs outflow summaries
- Visual charts and analytics
- Business performance insights

### 🎨 User Interface
- Modern Bootstrap design
- Responsive layout for all devices
- Highlighted entries (today's entries in light green)
- Incomplete jobs highlighted in red/orange
- Intuitive navigation and user experience

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **Charts**: Chart.js for data visualization
- **Authentication**: Flask-Login
- **Export**: openpyxl (Excel), ReportLab (PDF)

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `password` (Hashed)
- `role` (admin/normal)

### Jobs Table
- `id` (Primary Key)
- `customer_name`
- `status` (Completed/Incomplete)
- `date_time` (Auto-generated)
- `created_by` (Foreign Key to Users)

### Job Items Table
- `id` (Primary Key)
- `job_id` (Foreign Key to Jobs)
- `description`
- `quantity`
- `price`
- `total` (Auto-calculated)

### Expenditures Table
- `id` (Primary Key)
- `description`
- `quantity`
- `amount_used`
- `total` (Auto-calculated)
- `date_time` (Auto-generated)
- `created_by` (Foreign Key to Users)

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone or Download
```bash
# If using git
git clone <repository-url>
cd zehmo

# Or download and extract the ZIP file to c:\xampp\htdocs\zehmo
```

### Step 2: Install Dependencies
```bash
# Navigate to the project directory
cd c:\xampp\htdocs\zehmo

# Install required packages
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
# Start the Flask development server
python app.py
```

The application will be available at: `http://localhost:5000`

### Step 4: Access the Application
Open your web browser and navigate to `http://localhost:5000`

## Demo Login Credentials

### Admin User
- **Username**: `admin`
- **Password**: `admin123`
- **Permissions**: Full access (add, edit, delete jobs and expenditures)

### Normal User
- **Username**: `user`
- **Password**: `user123`
- **Permissions**: Add jobs and expenditures, view lists (no edit/delete)

## Usage Guide

### 1. Login
- Use the demo credentials above to log in
- The system will redirect you to the dashboard after successful login

### 2. Dashboard
- View business statistics and performance metrics
- See monthly revenue vs expenditure charts
- Quick access to add new jobs or expenditures

### 3. Managing Jobs
- Navigate to "All Jobs" from the menu
- Click "Add New Job" to create a job with multiple items
- Use filters to view jobs by period (Today, Week, Month, All)
- Admin users can edit/delete existing jobs

### 4. Managing Expenditures
- Navigate to "Expenditures" from the menu
- Add new expenditures with quantity and cost details
- Filter and sort expenditures by date, user, or amount
- Today's expenditures are highlighted in green

### 5. Reports
- Navigate to "Reports" from the menu
- Export jobs or expenditures to Excel/PDF format
- Generate monthly summaries with visual charts
- View business analytics and trends

### 6. Change Password
- Click "Change Password" in the navigation menu
- Enter current password and new password
- Password strength indicator helps create secure passwords

## File Structure

```
zehmo/
├── app.py                 # Main Flask application
├── routes.py              # Application routes and logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── instance/
│   └── database.db       # SQLite database (created automatically)
└── templates/
    ├── base.html         # Base template with navigation
    ├── login.html        # Login page
    ├── dashboard.html    # Dashboard with statistics
    ├── jobs.html         # Jobs management page
    ├── expenditures.html # Expenditures management page
    ├── reports.html      # Reports and analytics page
    └── change_password.html # Password change page
```

## Features in Detail

### Filtering Options
- **Today**: Show entries from today only
- **This Week**: Show entries from the current week
- **This Month**: Show entries from the current month
- **All**: Show all entries

### Highlighting System
- **Today's Entries**: Light green background
- **Incomplete Jobs**: Red/orange highlighting
- **Completed Jobs**: Normal styling

### Export Formats
- **Excel (.xlsx)**: Structured data with formatting
- **PDF**: Professional reports with charts and summaries

### User Roles
- **Admin**: Full CRUD operations on all data
- **Normal**: Can add new entries and view data (no edit/delete)

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # If port 5000 is busy, specify a different port
   python app.py --port 5001
   ```

2. **Database Issues**
   - Delete `instance/database.db` and restart the application
   - The database will be recreated with demo users

3. **Missing Dependencies**
   ```bash
   # Reinstall all dependencies
   pip install -r requirements.txt --force-reinstall
   ```

4. **Permission Issues**
   - Ensure you have write permissions in the project directory
   - Run command prompt as administrator if needed

### Development Mode
The application runs in debug mode by default, which provides:
- Automatic reloading when files change
- Detailed error messages
- Interactive debugger in the browser

## Security Notes

- Passwords are hashed using Werkzeug's security utilities
- Session management handled by Flask-Login
- CSRF protection should be added for production use
- Change demo passwords before production deployment

## Customization

### Adding New Users
1. Stop the application
2. Delete `instance/database.db`
3. Modify the user creation section in `app.py`
4. Restart the application

### Styling Changes
- Modify Bootstrap classes in HTML templates
- Add custom CSS in the `<style>` sections
- Update color schemes and themes as needed

### Database Changes
- Modify models in `app.py`
- Update routes in `routes.py`
- Adjust templates accordingly

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Flask and Bootstrap documentation
3. Ensure all dependencies are properly installed

## License

This project is provided as-is for business management purposes. Modify and adapt as needed for your specific requirements.