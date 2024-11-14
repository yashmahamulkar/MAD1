from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from ..models import Customer, ServiceProfessional, db, Service, ServiceRequest,FraudulentCustomer,DisabledCustomer,DisabledServiceProfessional
from datetime import datetime
admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
def dashboard():
    try:
        customer_count = Customer.query.count()
        professional_count = ServiceProfessional.query.count()
        completed_services = ServiceRequest.query.filter_by(status='completed').count()
        pending_services = ServiceRequest.query.filter_by(status='requested').count()
        print(customer_count, professional_count, completed_services, pending_services)
    except Exception as e:
        flash(f"An error occurred while fetching data: {str(e)}", 'danger')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('dashboard_status.html', customer_count=customer_count,
                           professional_count=professional_count,
                           completed_services=completed_services,
                           pending_services=pending_services)

@admin.route('/view_customers')
@login_required
def view_customers():
    try:
        customers = Customer.query.all()  
    except Exception as e:
        flash(f"An error occurred while fetching customers: {str(e)}", 'danger')
        return redirect(url_for('admin.dashboard'))

    return render_template('view_customers.html', customers=customers)

@admin.route('/view_service_professionals')
@login_required
def view_service_professionals():
    try:
        professionals = ServiceProfessional.query.all()  # Fetch all service professionals
    except Exception as e:
        flash(f"An error occurred while fetching service professionals: {str(e)}", 'danger')
        return redirect(url_for('admin.dashboard'))

    return render_template('view_service_professionals.html', professionals=professionals)

@admin.route('/delete_customer/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash('Customer account deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting customer: {str(e)}", 'danger')
    return redirect(url_for('admin.view_customers'))

@admin.route('/delete_service_professional/<int:professional_id>', methods=['POST'])
@login_required
def delete_service_professional(professional_id):
    try:
        # Find the service professional
        professional = ServiceProfessional.query.get_or_404(professional_id)
        
        # Create a DisabledServiceProfessional entry with the relevant data
        disabled_professional = DisabledServiceProfessional(
            name=professional.name,
            email=professional.email,
            password_hash=professional.password_hash
            # Add any other fields you want to preserve here
        )
        
        # Add to the DisabledServiceProfessional table
        db.session.add(disabled_professional)
        
        # Delete the original professional from ServiceProfessional table
        db.session.delete(professional)
        
        # Commit the transaction
        db.session.commit()
        
        flash('Service Professional account disabled successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while disabling the service professional: {str(e)}", 'danger')
    
    return redirect(url_for('admin.view_service_professionals'))

@admin.route('/create_service', methods=['GET', 'POST'])
@login_required
def create_service():
    if request.method == 'POST':
        try:
            service_name = request.form['service_name']
            service_description = request.form['service_description']
            base_price = float(request.form['base_price'])
            time_required = request.form['time_required']

            new_service = Service(
                service_name=service_name,
                service_description=service_description,
                base_price=base_price,
                time_required=time_required
            )

            db.session.add(new_service)
            db.session.commit()
            flash('Service created successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while creating service: {str(e)}", 'danger')
            return redirect(url_for('admin.create_service'))
        
        return redirect(url_for('admin.view_services'))

    return render_template('create_service.html')

@admin.route('/update_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def update_service(service_id):
    service = Service.query.get_or_404(service_id)

    if request.method == 'POST':
        try:
            service.service_name = request.form['service_name']
            service.service_description = request.form['service_description']
            service.base_price = float(request.form['base_price'])
            service.time_required = request.form['time_required']
            db.session.commit()
            flash('Service updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while updating service: {str(e)}", 'danger')
            return redirect(url_for('admin.update_service', service_id=service.id))
        
        return redirect(url_for('admin.view_services'))

    return render_template('update_service.html', service=service)

@admin.route('/delete_service/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    try:
        service = Service.query.get_or_404(service_id)
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting service: {str(e)}", 'danger')
    return redirect(url_for('admin.view_services'))

@admin.route('/view_services')
@login_required
def view_services():
    try:
        services = Service.query.all()  # Fetch all services
    except Exception as e:
        flash(f"An error occurred while fetching services: {str(e)}", 'danger')
        return redirect(url_for('admin.dashboard'))

    return render_template('view_services.html', services=services)

@admin.route('/view_customer_services/<int:customer_id>')
@login_required
def view_customer_services(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        customer_services = ServiceRequest.query.filter_by(customer_id=customer.id).all()
    except Exception as e:
        flash(f"An error occurred while fetching customer services: {str(e)}", 'danger')
        return redirect(url_for('admin.view_customers'))

    return render_template('view_customer_services.html', customer=customer, customer_services=customer_services)

@admin.route('/dashboard_stats')
@login_required
def dashboard_stats():
    try:
        customer_count = Customer.query.count()
        professional_count = ServiceProfessional.query.count()
        completed_services = ServiceRequest.query.filter_by(status='completed').count()
        pending_services = ServiceRequest.query.filter_by(status='requested').count()
        print(customer_count, professional_count, completed_services, pending_services)
    except Exception as e:
        flash(f"An error occurred while fetching dashboard stats: {str(e)}", 'danger')
        return redirect(url_for('admin.dashboard'))

    return render_template('dashboard_stats.html', 
                           customer_count=customer_count,
                           professional_count=professional_count,
                           completed_services=completed_services,
                           pending_services=pending_services)


@admin.route('/fraud_customers')
@login_required
def fraud_customers():
    try:
        # Fetch all customers whose service requests have a 'fraudulent' status
        fraudulent_requests = ServiceRequest.query.filter_by(status='fraudulent').all()
        # Get the unique customers who have fraudulent service requests
        fraud_customers = set(request.customer for request in fraudulent_requests)
    except Exception as e:
        flash(f"An error occurred while fetching fraudulent customers: {str(e)}", 'danger')
        return redirect(url_for('admin.dashboard'))

    return render_template('view_fraud_customers.html', fraud_customers=fraud_customers)

@admin.route('/view_fraud_customers')
@login_required
def view_fraud_customers():

    try:
        # Your query logic here...
        fraud_reports = db.session.query(FraudulentCustomer, Customer, ServiceRequest).join(
            Customer, FraudulentCustomer.customer_id == Customer.id).join(
            ServiceRequest, FraudulentCustomer.service_request_id == ServiceRequest.id).all()
        
        fraud_customers = [{
            'customer': fraud_report[1],
            'service_request': fraud_report[2],
            'report_date': fraud_report[0].report_date
        } for fraud_report in fraud_reports]
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('admin.dashboard'))

    return render_template('view_fraud_customers.html', fraud_customers=fraud_customers)

@admin.route('/disable_customer/<int:customer_id>', methods=['POST'])
@login_required
def disable_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        
        # Move the customer data to DisabledCustomer
        disabled_customer = DisabledCustomer(
            name=customer.name,
            email=customer.email,
            password_hash=customer.password_hash  # Make sure to transfer the password hash
        )
        
        # Add the record to DisabledCustomer
        db.session.add(disabled_customer)
        
        # Delete the original customer
        db.session.delete(customer)
        
        # Commit the changes
        db.session.commit()

        flash(f"Customer account '{customer.name}' has been disabled successfully.", 'success')
    except Exception as e:
        flash(f"An error occurred while disabling the customer: {str(e)}", 'danger')
        db.session.rollback()

    return redirect(url_for('admin.view_customers'))

@admin.route('/view_fraud_professionals')
@login_required
def view_fraud_professionals():
    try:
        print("Inside view_fraud_professionals route")
        # Query ServiceRequest table for fraudulent professionals (remark contains 'fraudulent')
        fraud_reports = db.session.query(ServiceRequest, ServiceProfessional).join(
            ServiceProfessional, ServiceRequest.professional_id == ServiceProfessional.id
        ).filter(ServiceRequest.remark == 'fraudulent').all()

        fraud_professionals = [{
            'professional': fraud_report[1],
            'service_request': fraud_report[0],
            'report_date': fraud_report[0].report_date
        } for fraud_report in fraud_reports]
        
    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('admin.dashboard'))

    print("Returning template")
    return render_template('view_fraud_professionals.html', fraud_professionals=fraud_professionals)


@admin.route('/disable_professional/<int:professional_id>', methods=['POST'])
@login_required
def disable_professional(professional_id):
    try:
        professional = ServiceProfessional.query.get_or_404(professional_id)
        
        # Move the professional data to DisabledProfessional
        disabled_professional = DisabledServiceProfessional(
            name=professional.name,
            email=professional.email,
            phone=professional.phone,  # Add any other fields needed
            password_hash=professional.password_hash  # Ensure to transfer the password hash
        )
        
        # Add the record to DisabledProfessional
        db.session.add(disabled_professional)
        
        # Delete the original professional
        db.session.delete(professional)
        
        # Commit the changes
        db.session.commit()

        flash(f"Service Professional '{professional.name}' has been disabled successfully.", 'success')
    except Exception as e:
        flash(f"An error occurred while disabling the service professional: {str(e)}", 'danger')
        db.session.rollback()

    return redirect(url_for('admin.view_service_professionals'))
