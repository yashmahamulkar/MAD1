from functools import wraps
from flask import redirect, url_for, flash,session
from flask_login import current_user


def roles_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                flash("Access denied.")
                print("Access denied")
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
