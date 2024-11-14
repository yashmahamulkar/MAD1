from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db

def get_db():
    from . import db  # Import db here to avoid circular import
    return db

class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class ServiceProfessional(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=False)  # Add time_required field
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    service = db.relationship('Service', backref='professionals')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(100), nullable=False)
    service_description = db.Column(db.Text, nullable=True)
    base_price = db.Column(db.Float, nullable=False)  # Base price of the service
    time_required = db.Column(db.String(50), nullable=True)  # Time required for the service (e.g., '1 hour')

    def __repr__(self):
        return f"<Service {self.service_name}>"


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'))
    date_of_request = db.Column(db.DateTime, nullable=False)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="requested")
    remarks = db.Column(db.Text, nullable=True)
    
    service = db.relationship('Service', backref='service_requests')
    customer = db.relationship('Customer', backref='service_requests')
    professional = db.relationship('ServiceProfessional', backref='service_requests')
    
    def mark_as_completed(self):
        self.status = 'completed'
        self.date_of_completion = db.func.now()
        db.session.commit()

    def __repr__(self):
        return f"<ServiceRequest {self.id} - {self.status}>"
    

class FakeAdmin(UserMixin):
    id = 1
    is_authenticated = True
    is_active = True
    is_anonymous = False

    def get_id(self):
        return str(self.id)  # Return the ID as a string



class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(50), default='admin')  # Admin role

    def set_password(self, password):
        self.password = password  # Implement a proper hash function
    
    def check_password(self, password):
        return self.password == password