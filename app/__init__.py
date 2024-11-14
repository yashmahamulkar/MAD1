from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .main.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .admin.routes import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from .professional.routes import professional as professional_blueprint
    app.register_blueprint(professional_blueprint, url_prefix='/professional')
    
    from .customer.routes import customer as customer_blueprint
    app.register_blueprint(customer_blueprint, url_prefix='/customer')
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import Customer, ServiceProfessional, FakeAdmin  # Import models here to avoid circular import
    # Attempt to load user by role type
    user = Customer.query.get(int(user_id))
    if user:
        return user
    user = ServiceProfessional.query.get(int(user_id))
    if user:
        return user
    # Assuming FakeAdmin user has a unique id; here we use id = 1 for demo
    if int(user_id) == 1:
        return FakeAdmin(id=1, role="admin")  
    return None
