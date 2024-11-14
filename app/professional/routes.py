from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user, logout_user
from ..models import ServiceProfessional, ServiceRequest
from datetime import datetime

professional = Blueprint('professional', __name__)

@professional.route('/dashboard')
@login_required
def dashboard():
    try:
        user_id = session.get('user_id')
        user_name = session.get('user_name')
        user_email = session.get('user_email')

        # Count pending services
        pending_services_count = ServiceRequest.query.filter_by(professional_id=current_user.id, status='requested').count()

        # Count completed services
        completed_services_count = ServiceRequest.query.filter_by(professional_id=current_user.id, status='completed').count()

        # Pass the counts to the template
        return render_template('progress.html', user_name=user_name, user_email=user_email,
                               pending_services_count=pending_services_count,
                               completed_services_count=completed_services_count)
    except Exception as e:
        flash(f'An error occurred while fetching the dashboard data: {e}', 'danger')
        return redirect(url_for('main.index'))

@professional.route('/profile')
@login_required
def profile():
    try:
        # Fetch the professional's data from the database
        professional_data = ServiceProfessional.query.filter_by(id=current_user.id).first()
        if professional_data:
            return render_template('professional_profile.html', professional=professional_data)
        else:
            flash('Professional data not found.', 'warning')
            return redirect(url_for('professional.dashboard'))
    except Exception as e:
        flash(f'An error occurred while fetching the profile data: {e}', 'danger')
        return redirect(url_for('professional.dashboard'))

@professional.route('/pending_services')
@login_required
def pending_services():
    try:
        # Get all pending service requests for the logged-in professional
        pending_services = ServiceRequest.query.filter_by(professional_id=current_user.id, status='requested').all()
        return render_template('pending_services.html', pending_services=pending_services)
    except Exception as e:
        flash(f'An error occurred while fetching the pending services: {e}', 'danger')
        return redirect(url_for('professional.dashboard'))

@professional.route('/completed_services')
@login_required
def completed_services():
    try:
        # Get all completed service requests for the logged-in professional
        completed_services = ServiceRequest.query.filter_by(professional_id=current_user.id, status='completed').all()
        return render_template('completed_services.html', completed_services=completed_services)
    except Exception as e:
        flash(f'An error occurred while fetching the completed services: {e}', 'danger')
        return redirect(url_for('professional.dashboard'))

@professional.route('/logout')
@login_required
def logout():
    try:
        logout_user()  # Use logout_user to log out the current user
        flash('You have been logged out.', 'info')
        return redirect(url_for('main.index'))
    except Exception as e:
        flash(f'An error occurred while logging out: {e}', 'danger')
        return redirect(url_for('professional.dashboard'))
