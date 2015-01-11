import re
# Project-specific imports
from wtforms import Form, StringField, PasswordField, validators

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


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
                    'digits, dash and underscore')]
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
        "Email (optional)", [validators.optional(), validators.Email()])