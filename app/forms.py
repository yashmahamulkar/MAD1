from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField,FloatField,IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from .models import Service
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
class ProfessionalRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    pincode = StringField('Pincode', validators=[DataRequired()])
    experience = IntegerField('Experience (in years)', validators=[DataRequired()])
    rate = FloatField('Rate (per hour)', validators=[DataRequired()])
    time_required = StringField('Time Required', validators=[DataRequired()])  # Add time_required field

    # Dynamic dropdown for services
    service = SelectField('Service', coerce=int, validators=[DataRequired()])
    
    # Initialize the service dropdown dynamically
    def __init__(self, *args, **kwargs):
        super(ProfessionalRegistrationForm, self).__init__(*args, **kwargs)
        # Fetch services from the database and populate the service dropdown
        self.service.choices = [(service.id, service.service_name) for service in Service.query.all()]


class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
