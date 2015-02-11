import re
# Third-party imports
from wtforms import (
    Form, StringField, PasswordField, TextAreaField, validators,
    ValidationError, SubmitField)
# Internal project imports
from hashutils import check_against_hash
from model import User

USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


# Custom validators.
def user_exists(form, field):
    if User.by_prop('name', field.data):
        raise ValidationError('User "{}" already exists!'.format(field.data))


def length(min, max):
    def _length(form, field):
        value = len(field.data) if field.data else 0
        if value < min:
            adjective = 'short'
        elif value > max:
            adjective = 'long'
        else:
            return
        message = (
            "{field_name} is too {adjective}! Must be {min} to {max} "
            "characters long".format(
                field_name=field.label.text, adjective=adjective, min=min,
                max=max))
        raise ValidationError(message)

    return _length


class SignupForm(Form):
    username = StringField(
        'Username',
        [user_exists,
         validators.input_required(message='You must specify username!'),
         length(3, 20),
         validators.regexp(
             USERNAME_RE,
             message='Invalid username! May contain only latin letters, '
                     'digits, dash and underscore')]
    )
    password = PasswordField(
        'Password',
        [validators.input_required(message='You must specify password!'),
         length(3, 20)]
    )
    verify = PasswordField(
        'Verify password',
        [validators.equal_to('password', message='Passwords do not match!')]
    )
    email = StringField(
        "Email (optional)",
        [validators.optional(),
         validators.Email(message='Invalid email address!')])
    submit = SubmitField('Create')


class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')
    submit = SubmitField('Sign In')
    _user = None

    # Username validation was put inside because there's not other way (?) to
    # control order in which fields are validated.
    def validate_password(form, field):
        message = 'Something is wrong with your username or password'

        form._user = User.by_prop('name', form.username.data)
        if not form._user:
            raise ValidationError(message)
        pwd_hash = form._user.password_hash
        if not check_against_hash(form.username.data + field.data, pwd_hash):
            raise ValidationError(message)


class EditForm(Form):
    head = StringField(
        'Article head',
        [validators.input_required('Head cannot be empty!'),
         validators.length(
            max=256,
            message="Article head is too long! Must not exceed 256 "
                    "characters")],
        id='wiki-head')
    body = TextAreaField('Article body', id='wiki-body')
    submit = SubmitField('Save')
