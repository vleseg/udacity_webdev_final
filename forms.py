import re
# Project-specific imports
from model import User
from wtforms import (
    Form, StringField, PasswordField, TextAreaField, validators,
    ValidationError)

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


# Custom validators.
def user_exists(form, field):
    if User.by_prop('name', field.data):
        raise ValidationError('User "{}" already exists!'.format(field.data))


class SignupForm(Form):
    username = StringField(
        'Username',
        [validators.input_required(message='You must specify username!'),
         validators.length(
            min=3,
            message='Username is too short! Must be 3 to 20 characters long'),
         validators.length(
            max=20,
            message='Username is too long! Must be 3 to 20 characters long'),
         validators.regexp(
            USERNAME_RE,
            message='Invalid username! May contain only latin letters, '
                    'digits, dash and underscore'),
         user_exists]
    )
    password = PasswordField(
        'Password',
        [validators.input_required(message='You must specify password!'),
         validators.length(
            min=3,
            message='Password is too short! Must be 3 to 20 characters long'),
         validators.length(
            max=20,
            message='Password is too long! Must be 3 to 20 characters long')]
    )
    verify = PasswordField(
        'Verify password',
        [validators.equal_to('password', message='Passwords do not match!')]
    )
    email = StringField(
        "Email (optional)",
        [validators.optional(),
         validators.Email(message='Invalid email address!')])


class EditForm(Form):
    title = StringField('Page title')
    body = TextAreaField('Page body')