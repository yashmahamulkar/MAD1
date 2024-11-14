from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import LoginForm, RegistrationForm, ProfessionalRegistrationForm, AdminLoginForm
from ..models import Customer, ServiceProfessional, db, FakeAdmin

# Blueprints for each user role
main = Blueprint('main', __name__)
customer_bp = Blueprint('customer', __name__)
professional_bp = Blueprint('professional', __name__)
admin_bp = Blueprint('admin', __name__)

# Hardcoded admin credentials (use a hashed password in production)
ADMIN_EMAIL = 'admin@gmail.com'
ADMIN_PASSWORD = '123456'

# Home page (public)
@main.route('/')
def index():
    return render_template('index.html')

# Customer registration
@main.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Customer(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.')
        return redirect(url_for('main.customer_login'))
    return render_template('registration.html', form=form)

# Service Professional registration
@main.route('/professional/register', methods=['GET', 'POST'])
def professional_register():
    if current_user.is_authenticated:
        return redirect(url_for('professional.dashboard'))
    form = ProfessionalRegistrationForm()
    if form.validate_on_submit():
        # Get the form data
        service_professional = ServiceProfessional(
            name=form.name.data,
            email=form.email.data,
            city=form.city.data,
            pincode=form.pincode.data,
            experience=form.experience.data,
            rate=form.rate.data,
            time_required=form.time_required.data,  # Save the time required
            service_id=form.service.data  # Link the selected service
        )
        
        # Set the password for the professional
        service_professional.set_password(form.password.data)
        
        # Add the service professional to the database
        db.session.add(service_professional)
        db.session.commit()
        
        # Flash a success message and redirect to login page
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.professional_login'))
    
    return render_template('professional_registration.html', form=form)

# Customer login route
@main.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    if current_user.is_authenticated:
        return redirect(url_for('customer.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            session['role'] = 'customer'  # Store role in session
            flash('Customer login successful.')
            return redirect(url_for('customer.dashboard'))
        else:
            flash('Invalid email or password.')
    return render_template('customer_login.html', form=form)

# Service Professional login route
@main.route('/professional/login', methods=['GET', 'POST'])
def professional_login():
    if current_user.is_authenticated:
        return redirect(url_for('professional.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = ServiceProfessional.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            session['role'] = 'professional'
            session['user_id'] = user.id  # Store user ID in session
            session['user_name'] = user.name  # Store user name in session
            session['user_email'] = user.email  # Store user email in session# Store role in session
            flash('Service Professional login successful.')
            return redirect(url_for('professional.dashboard'))
        else:
            flash('Invalid email or password.')
    return render_template('professional_login.html', form=form)

# Admin login route (Hardcoded admin credentials)
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = AdminLoginForm()
    if form.validate_on_submit():
        if form.email.data == ADMIN_EMAIL and form.password.data == ADMIN_PASSWORD:
            login_user(FakeAdmin())  # Log in the mock admin user
            session['role'] = 'admin'  # Store role in session
            flash('Admin login successful.')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid email or password.')
    return render_template('admin_login.html', form=form)

# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('role', None)  # Remove the role from session
    flash('You have been logged out.')
    return redirect(url_for('main.index'))  # Or to the login page depending on role

# Dashboard route, role-based redirection

#### Customer Blueprint
@customer_bp.route('/dashboard')
@login_required
def customer_dashboard():
    if session.get('role') == 'customer' and isinstance(current_user, Customer):
        return render_template('customer_dashboard.html')
    flash('Access denied.')
    return redirect(url_for('main.index'))

#### Service Professional Blueprint
@professional_bp.route('/dashboard')
@login_required
def professional_dashboard():
    if session.get('role') == 'professional' and isinstance(current_user, ServiceProfessional):
        return render_template('professional_dashboard.html')
    flash('Access denied.')
    return redirect(url_for('main.index'))

#### Admin Blueprint
@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if session.get('role') == 'admin' and current_user.id == 1:
        return render_template('admin_dashboard.html')
    flash('Access denied.')
    return redirect(url_for('main.index'))
