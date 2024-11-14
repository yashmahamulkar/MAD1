from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import Service, ServiceProfessional, ServiceRequest, db
from datetime import datetime

customer = Blueprint('customer', __name__)

@customer.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    services = []
    service_providers = []
    selected_service = None
    selected_city = None
    selected_pincode = None

    try:
        services = Service.query.all()
    except Exception as e:
        flash(f"Error retrieving services: {e}", 'error')

    # Handle form submission
    if request.method == 'POST':
        selected_service = request.form.get('service')
        selected_city = request.form.get('city')
        selected_pincode = request.form.get('pincode')

        try:
            service_providers = ServiceProfessional.query.all()
        except Exception as e:
            flash(f"Error retrieving service providers: {e}", 'error')

        if selected_service:
            service_providers = [provider for provider in service_providers if provider.service_id == int(selected_service)]
        if selected_city:
            service_providers = [provider for provider in service_providers if provider.city == selected_city]
        if selected_pincode:
            service_providers = [provider for provider in service_providers if provider.pincode == selected_pincode]

        # Handle the service request
        if request.form.get('request_service'):
            professional_id = request.form.get('professional_id')
            service_id = request.form.get('service')
            try:
                service_provider = ServiceProfessional.query.get(professional_id)
                service = Service.query.get(service_id)

                existing_request = ServiceRequest.query.filter_by(
                    customer_id=current_user.id, service_id=service.id, professional_id=professional_id).first()

                if existing_request:
                    # If the request already exists, update it
                    existing_request.status = 'requested'
                    existing_request.date_of_request = db.func.now()
                    existing_request.remarks = "Request updated"
                    db.session.commit()
                else:
                    # Create a new request if not already exists
                    new_request = ServiceRequest(
                        service_id=service.id,
                        customer_id=current_user.id,  # Use current_user.id for the logged-in customer
                        professional_id=professional_id,
                        date_of_request=db.func.now()
                    )
                    db.session.add(new_request)
                    db.session.commit()

                return redirect(url_for('customer.dashboard'))

            except Exception as e:
                flash(f"Error handling service request: {e}", 'error')
                return redirect(url_for('customer.dashboard'))

    try:
        customer_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    except Exception as e:
        flash(f"Error retrieving customer requests: {e}", 'error')

    return render_template(
        'customer_dashboard.html',
        services=services,
        service_providers=service_providers,  # Pass filtered service providers
        customer_requests=customer_requests,
        selected_service=selected_service,
        selected_city=selected_city,
        selected_pincode=selected_pincode
    )


@customer.route('/request_service', methods=['GET', 'POST'])
@login_required
def request_service():
    service_id = request.args.get('service_id')
    professional_id = request.args.get('professional_id')

    try:
        if request.method == 'POST':
            service = Service.query.get(service_id)
            service_provider = ServiceProfessional.query.get(professional_id)

            new_request = ServiceRequest(
                service_id=service.id,
                customer_id=current_user.id,
                professional_id=service_provider.id,
                date_of_request=db.func.now()
            )
            db.session.add(new_request)
            db.session.commit()

            return redirect(url_for('customer.dashboard'))

    except Exception as e:
        flash(f"Error handling service request: {e}", 'error')

    return render_template('request_service.html', service_id=service_id, professional_id=professional_id)


@customer.route('/requests', methods=['GET'])
@login_required
def view_requests():
    try:
        customer_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    except Exception as e:
        flash(f"Error retrieving customer requests: {e}", 'error')

    return render_template('view_requests.html', customer_requests=customer_requests)


@customer.route('/services', methods=['GET'])
@login_required
def view_services():
    try:
        services = Service.query.all()
    except Exception as e:
        flash(f"Error retrieving services: {e}", 'error')

    return render_template('view_services.html', services=services)


@customer.route('/customer/service_requests')
@login_required
def customer_service_request():
    try:
        customer_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    except Exception as e:
        flash(f"Error retrieving customer service requests: {e}", 'error')

    return render_template('customer_service_request.html', customer_requests=customer_requests)


@customer.route('/customer/service-request/mark-completed/<int:request_id>', methods=['GET', 'POST'])
@login_required
def mark_as_completed(request_id):
    try:
        service_request = ServiceRequest.query.get_or_404(request_id)

        if service_request.customer_id != current_user.id:
            return redirect(url_for('customer.dashboard'))

        if request.method == 'POST':
            remarks = request.form.get('remarks')

            service_request.mark_as_completed()
            service_request.remarks = remarks
            db.session.commit()

            return redirect(url_for('customer.customer_service_request'))

    except Exception as e:
        flash(f"Error marking request as completed: {e}", 'error')

    return render_template('customer/service_request_detail.html', request=service_request)
