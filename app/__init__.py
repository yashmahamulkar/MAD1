from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    try:
        db.init_app(app)
        login_manager.init_app(app)
    except Exception as e:
        flash(f"Error initializing app components: {e}", 'error')

    # Register blueprints
    try:
        from .main.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
    except Exception as e:
        flash(f"Error registering main blueprint: {e}", 'error')

    try:
        from .admin.routes import admin as admin_blueprint
        app.register_blueprint(admin_blueprint, url_prefix='/admin')
    except Exception as e:
        flash(f"Error registering admin blueprint: {e}", 'error')

    try:
        from .professional.routes import professional as professional_blueprint
        app.register_blueprint(professional_blueprint, url_prefix='/professional')
    except Exception as e:
        flash(f"Error registering professional blueprint: {e}", 'error')

    try:
        from .customer.routes import customer as customer_blueprint
        app.register_blueprint(customer_blueprint, url_prefix='/customer')
    except Exception as e:
        flash(f"Error registering customer blueprint: {e}", 'error')

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import Customer, ServiceProfessional, FakeAdmin  
    try:
        user = Customer.query.get(int(user_id))
        if user:
            return user
    except Exception as e:
        flash(f"Error loading customer user: {e}", 'error')

    try:
        user = ServiceProfessional.query.get(int(user_id))
        if user:
            return user
    except Exception as e:
        flash(f"Error loading service professional user: {e}", 'error')

    try:
        if int(user_id) == 1:
            return FakeAdmin(id=1, role="admin")
    except Exception as e:
        flash(f"Error loading fake admin: {e}", 'error')

    return None
