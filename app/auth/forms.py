# forms module for flask-wtf. 
# CSRF protection initialized globally in __init__.py.
# Forms created here are to be imported into their respective routes.
# Templates are to be updated to use flask-wtf fields.

# purpose of implementing flask-wtf:
# - make login form dynamic and more secure
# - validate the input fields server-side
# - ensure that the form is always properly rendered in the template
# - have added security with CSRF token
# - scalable forms

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
import re

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class ChangePasswordForm(FlaskForm):
    current_password= PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password')

    def validate_new_password(self, field):
        password = field.data
        if len(password) < 12:
            raise ValidationError('Password must be at least 12 characters long.')
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-\\/\[\]=+;~`]', password):
            raise ValidationError('Password must contain at least one symbol.')
