from flask import render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from app import app, db, User, Job, JobItem, Expenditure, admin_required

# Authentication Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')

# User Management Routes (Admin Only)
@app.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    
    # Validate input
    if not username or not password:
        flash('Username and password are required.', 'error')
        return redirect(url_for('users'))
    
    if len(password) < 6:
        flash('Password must be at least 6 characters long.', 'error')
        return redirect(url_for('users'))
    
    if role not in ['admin', 'normal']:
        flash('Invalid role selected.', 'error')
        return redirect(url_for('users'))
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'error')
        return redirect(url_for('users'))
    
    try:
        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f'User "{username}" created successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error creating user. Please try again.', 'error')
    
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/role', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form['role']
    
    if new_role not in ['admin', 'normal']:
        flash('Invalid role selected.', 'error')
        return redirect(url_for('users'))
    
    # Prevent admin from demoting themselves
    if user.id == current_user.id and new_role != 'admin':
        flash('You cannot change your own admin role.', 'error')
        return redirect(url_for('users'))
    
    try:
        user.role = new_role
        db.session.commit()
        flash(f'User "{user.username}" role updated to {new_role}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating user role. Please try again.', 'error')
    
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.username}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user. Please try again.', 'error')
    
    return redirect(url_for('users'))

# Dashboard Route
@app.route('/dashboard')
@login_required
def dashboard():
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    
    # Jobs statistics
    jobs_today = Job.query.filter(
        db.func.date(Job.date_time) == today
    ).count()
    
    jobs_today_completed = Job.query.filter(
        db.func.date(Job.date_time) == today,
        Job.status == 'Completed'
    ).count()
    
    jobs_week = Job.query.filter(
        db.func.date(Job.date_time) >= week_start,
        Job.status == 'Completed'
    ).count()
    
    jobs_month = Job.query.filter(
        db.func.date(Job.date_time) >= month_start,
        Job.status == 'Completed'
    ).count()
    
    incomplete_jobs = Job.query.filter(Job.status == 'Incomplete').count()
    
    # Expenditure statistics
    expenditures_today = db.session.query(db.func.sum(Expenditure.total)).filter(
        db.func.date(Expenditure.date_time) == today
    ).scalar() or 0
    
    expenditures_month = db.session.query(db.func.sum(Expenditure.total)).filter(
        db.func.date(Expenditure.date_time) >= month_start
    ).scalar() or 0
    
    # Revenue statistics
    revenue_month = db.session.query(db.func.sum(JobItem.total)).join(Job).filter(
        db.func.date(Job.date_time) >= month_start,
        Job.status == 'Completed'
    ).scalar() or 0
    
    net_balance = revenue_month - expenditures_month
    
    # Generate monthly chart
    chart_data = generate_monthly_chart()
    
    return render_template('dashboard.html', 
                         jobs_today=jobs_today,
                         jobs_today_completed=jobs_today_completed,
                         jobs_week=jobs_week,
                         jobs_month=jobs_month,
                         incomplete_jobs=incomplete_jobs,
                         expenditures_today=expenditures_today,
                         expenditures_month=expenditures_month,
                         revenue_month=revenue_month,
                         net_balance=net_balance,
                         chart_data=chart_data,
                         datetime=datetime)

# Jobs Routes
@app.route('/jobs')
@login_required
def jobs():
    filter_type = request.args.get('filter', 'today')
    today = datetime.now().date()
    
    query = Job.query
    
    if filter_type == 'today':
        query = query.filter(db.func.date(Job.date_time) == today)
    elif filter_type == 'week':
        week_start = today - timedelta(days=today.weekday())
        query = query.filter(db.func.date(Job.date_time) >= week_start)
    elif filter_type == 'month':
        month_start = today.replace(day=1)
        query = query.filter(db.func.date(Job.date_time) >= month_start)
    
    jobs = query.order_by(Job.date_time.desc()).all()
    
    return render_template('jobs.html', jobs=jobs, filter_type=filter_type, today=today)

@app.route('/add_job', methods=['POST'])
@login_required
def add_job():
    try:
        customer_name = request.form['customer_name']
        status = request.form['status']
        payment_method = request.form['payment_method']
        
        # Server-side validation for payment method
        if payment_method not in ['Cash', 'Transfer']:
            flash('Invalid payment method selected', 'error')
            return redirect(url_for('jobs'))
        
        job = Job(
            customer_name=customer_name,
            status=status,
            payment_method=payment_method,
            created_by=current_user.id
        )
        db.session.add(job)
        db.session.flush()  # Get the job ID
        
        # Add job items
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        for desc, qty, price in zip(descriptions, quantities, prices):
            if desc and qty and price:
                quantity = float(qty)
                unit_price = float(price)
                total = quantity * unit_price
                
                item = JobItem(
                    job_id=job.id,
                    description=desc,
                    quantity=quantity,
                    price=unit_price,
                    total=total
                )
                db.session.add(item)
        
        db.session.commit()
        flash('Job added successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding job: {str(e)}', 'error')
    
    return redirect(url_for('jobs'))

@app.route('/edit_job/<int:job_id>', methods=['POST'])
@login_required
@admin_required
def edit_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        
        payment_method = request.form['payment_method']
        
        # Server-side validation for payment method
        if payment_method not in ['Cash', 'Transfer']:
            flash('Invalid payment method selected', 'error')
            return redirect(url_for('jobs'))
        
        job.customer_name = request.form['customer_name']
        job.status = request.form['status']
        job.payment_method = payment_method
        
        # Delete existing items
        JobItem.query.filter_by(job_id=job.id).delete()
        
        # Add new items
        descriptions = request.form.getlist('description[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        for desc, qty, price in zip(descriptions, quantities, prices):
            if desc and qty and price:
                quantity = float(qty)
                unit_price = float(price)
                total = quantity * unit_price
                
                item = JobItem(
                    job_id=job.id,
                    description=desc,
                    quantity=quantity,
                    price=unit_price,
                    total=total
                )
                db.session.add(item)
        
        db.session.commit()
        flash('Job updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating job: {str(e)}', 'error')
    
    return redirect(url_for('jobs'))

@app.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
@admin_required
def delete_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        flash('Job deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting job: {str(e)}', 'error')
    
    return redirect(url_for('jobs'))

@app.route('/get_job/<int:job_id>')
@login_required
def get_job(job_id):
    job = Job.query.get_or_404(job_id)
    return jsonify({
        'id': job.id,
        'customer_name': job.customer_name,
        'status': job.status,
        'payment_method': job.payment_method,
        'items': [{
            'description': item.description,
            'quantity': item.quantity,
            'price': item.price,
            'total': item.total
        } for item in job.items]
    })

# Expenditures Routes
@app.route('/expenditures')
@login_required
def expenditures():
    filter_type = request.args.get('filter', 'today')
    today = datetime.now().date()
    
    query = Expenditure.query
    
    if filter_type == 'today':
        query = query.filter(db.func.date(Expenditure.date_time) == today)
    elif filter_type == 'week':
        week_start = today - timedelta(days=today.weekday())
        query = query.filter(db.func.date(Expenditure.date_time) >= week_start)
    elif filter_type == 'month':
        month_start = today.replace(day=1)
        query = query.filter(db.func.date(Expenditure.date_time) >= month_start)
    
    expenditures = query.order_by(Expenditure.date_time.desc()).all()
    
    return render_template('expenditures.html', expenditures=expenditures, filter_type=filter_type, today=today)

@app.route('/add_expenditure', methods=['POST'])
@login_required
def add_expenditure():
    try:
        description = request.form['description']
        quantity = float(request.form['quantity'])
        amount_used = float(request.form['amount_used'])
        total = quantity * amount_used
        
        expenditure = Expenditure(
            description=description,
            quantity=quantity,
            amount_used=amount_used,
            total=total,
            created_by=current_user.id
        )
        
        db.session.add(expenditure)
        db.session.commit()
        flash('Expenditure added successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding expenditure: {str(e)}', 'error')
    
    return redirect(url_for('expenditures'))

@app.route('/edit_expenditure/<int:expenditure_id>', methods=['POST'])
@login_required
@admin_required
def edit_expenditure(expenditure_id):
    try:
        expenditure = Expenditure.query.get_or_404(expenditure_id)
        
        expenditure.description = request.form['description']
        expenditure.quantity = float(request.form['quantity'])
        expenditure.amount_used = float(request.form['amount_used'])
        expenditure.total = expenditure.quantity * expenditure.amount_used
        
        db.session.commit()
        flash('Expenditure updated successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating expenditure: {str(e)}', 'error')
    
    return redirect(url_for('expenditures'))

@app.route('/delete_expenditure/<int:expenditure_id>', methods=['POST'])
@login_required
@admin_required
def delete_expenditure(expenditure_id):
    try:
        expenditure = Expenditure.query.get_or_404(expenditure_id)
        db.session.delete(expenditure)
        db.session.commit()
        flash('Expenditure deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting expenditure: {str(e)}', 'error')
    
    return redirect(url_for('expenditures'))

@app.route('/get_expenditure/<int:expenditure_id>')
@login_required
def get_expenditure(expenditure_id):
    expenditure = Expenditure.query.get_or_404(expenditure_id)
    return jsonify({
        'id': expenditure.id,
        'description': expenditure.description,
        'quantity': expenditure.quantity,
        'amount_used': expenditure.amount_used,
        'total': expenditure.total
    })

# Reports Routes
@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/export_jobs')
@login_required
def export_jobs():
    filter_type = request.args.get('filter', 'all')
    format_type = request.args.get('format', 'excel')
    
    today = datetime.now().date()
    query = Job.query
    
    if filter_type == 'today':
        query = query.filter(db.func.date(Job.date_time) == today)
    elif filter_type == 'week':
        week_start = today - timedelta(days=today.weekday())
        query = query.filter(db.func.date(Job.date_time) >= week_start)
    elif filter_type == 'month':
        month_start = today.replace(day=1)
        query = query.filter(db.func.date(Job.date_time) >= month_start)
    
    jobs = query.order_by(Job.date_time.desc()).all()
    
    if format_type == 'excel':
        return export_jobs_excel(jobs, filter_type)
    else:
        return export_jobs_pdf(jobs, filter_type)

@app.route('/export_expenditures')
@login_required
def export_expenditures():
    filter_type = request.args.get('filter', 'all')
    format_type = request.args.get('format', 'excel')
    
    today = datetime.now().date()
    query = Expenditure.query
    
    if filter_type == 'today':
        query = query.filter(db.func.date(Expenditure.date_time) == today)
    elif filter_type == 'week':
        week_start = today - timedelta(days=today.weekday())
        query = query.filter(db.func.date(Expenditure.date_time) >= week_start)
    elif filter_type == 'month':
        month_start = today.replace(day=1)
        query = query.filter(db.func.date(Expenditure.date_time) >= month_start)
    
    expenditures = query.order_by(Expenditure.date_time.desc()).all()
    
    if format_type == 'excel':
        return export_expenditures_excel(expenditures, filter_type)
    else:
        return export_expenditures_pdf(expenditures, filter_type)

# Helper Functions
def generate_monthly_chart():
    # Generate data for the last 6 months
    months = []
    revenues = []
    expenditures = []
    
    for i in range(5, -1, -1):
        month_date = datetime.now().replace(day=1) - timedelta(days=30*i)
        next_month = (month_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        
        # Revenue for completed jobs
        revenue = db.session.query(db.func.sum(JobItem.total)).join(Job).filter(
            Job.date_time >= month_date,
            Job.date_time < next_month,
            Job.status == 'Completed'
        ).scalar() or 0
        
        # Expenditures
        expenditure = db.session.query(db.func.sum(Expenditure.total)).filter(
            Expenditure.date_time >= month_date,
            Expenditure.date_time < next_month
        ).scalar() or 0
        
        months.append(month_date.strftime('%b %Y'))
        revenues.append(float(revenue))
        expenditures.append(float(expenditure))
    
    # Create chart
    plt.figure(figsize=(10, 6))
    x = range(len(months))
    width = 0.35
    
    plt.bar([i - width/2 for i in x], revenues, width, label='Revenue', color='#28a745')
    plt.bar([i + width/2 for i in x], expenditures, width, label='Expenditures', color='#dc3545')
    
    plt.xlabel('Month')
    plt.ylabel('Amount')
    plt.title('Monthly Revenue vs Expenditures')
    plt.xticks(x, months, rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Convert to base64
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return chart_url

def export_jobs_excel(jobs, filter_type):
    data = []
    for job in jobs:
        for item in job.items:
            data.append({
                'Job ID': job.id,
                'Customer': job.customer_name,
                'Description': item.description,
                'Quantity': item.quantity,
                'Price': item.price,
                'Total': item.total,
                'Status': job.status,
                'Date': job.date_time.strftime('%Y-%m-%d %I:%M %p'),
                'Created By': job.creator.username
            })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Jobs', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'jobs_{filter_type}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

def export_expenditures_excel(expenditures, filter_type):
    data = []
    for exp in expenditures:
        data.append({
            'ID': exp.id,
            'Description': exp.description,
            'Quantity': exp.quantity,
            'Amount Used': exp.amount_used,
            'Total': exp.total,
            'Date': exp.date_time.strftime('%Y-%m-%d %I:%M %p'),
            'Created By': exp.creator.username
        })
    
    df = pd.DataFrame(data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Expenditures', index=False)
    
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'expenditures_{filter_type}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    )

def export_jobs_pdf(jobs, filter_type):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Jobs Report - {filter_type.title()}")
    
    # Headers
    y = height - 100
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Customer")
    p.drawString(150, y, "Description")
    p.drawString(300, y, "Qty")
    p.drawString(350, y, "Price")
    p.drawString(400, y, "Total")
    p.drawString(450, y, "Status")
    p.drawString(500, y, "Date")
    
    # Data
    y -= 20
    p.setFont("Helvetica", 8)
    
    for job in jobs:
        for item in job.items:
            if y < 50:
                p.showPage()
                y = height - 50
            
            p.drawString(50, y, job.customer_name[:15])
            p.drawString(150, y, item.description[:20])
            p.drawString(300, y, str(item.quantity))
            p.drawString(350, y, f"₦{item.price:.2f}")
            p.drawString(400, y, f"₦{item.total:.2f}")
            p.drawString(450, y, job.status)
            p.drawString(500, y, job.date_time.strftime('%m/%d/%Y'))
            y -= 15
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'jobs_{filter_type}_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

def export_expenditures_pdf(expenditures, filter_type):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Expenditures Report - {filter_type.title()}")
    
    # Headers
    y = height - 100
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Description")
    p.drawString(200, y, "Quantity")
    p.drawString(300, y, "Amount Used")
    p.drawString(400, y, "Total")
    p.drawString(500, y, "Date")
    
    # Data
    y -= 20
    p.setFont("Helvetica", 8)
    
    for exp in expenditures:
        if y < 50:
            p.showPage()
            y = height - 50
        
        p.drawString(50, y, exp.description[:25])
        p.drawString(200, y, str(exp.quantity))
        p.drawString(300, y, f"₦{exp.amount_used:.2f}")
        p.drawString(400, y, f"₦{exp.total:.2f}")
        p.drawString(500, y, exp.date_time.strftime('%m/%d/%Y'))
        y -= 15
    
    p.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'expenditures_{filter_type}_{datetime.now().strftime("%Y%m%d")}.pdf'
    )