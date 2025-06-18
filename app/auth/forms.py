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
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
