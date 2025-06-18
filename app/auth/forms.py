# forms module for flask-wtf. 
# This will be used to prevent CSRF attacks on the login page or any add'l forms as needed.

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

    # TODO: 
    # 1) import this form into auth.py and set up the login page
    # 2) update the login.html template to use flask-wtf field rendering and form.hidden_tag()