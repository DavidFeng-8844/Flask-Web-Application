from flask_wtf import FlaskForm
import re
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField
)

from wtforms.validators import (
    DataRequired,
    Length,
    EqualTo,
    ValidationError,
    Email
)
from flaskapp.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    username = StringField(label='Username', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])
    password = PasswordField(label='Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField(label='Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField(label='Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if ' ' in username.data:
            raise ValidationError("Username cannot contain spaces.")
        if user:
            raise ValidationError("Username is already taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email is already taken.")
        
    def validate_password(self, password):
        if ' ' in password.data:
            raise ValidationError("Password cannot contain spaces.")
        if not re.search(r'[A-Z]', password.data):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password.data):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password.data):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}-|<>]', password.data):
            raise ValidationError("Password must contain at least one special character.")


class UsernameLoginForm(FlaskForm):
    username = StringField(label='Username', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])
    password = PasswordField(label='Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    remember = BooleanField(label='Remember me')
    submit = SubmitField(label='Login')


class EmailLoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField(label='Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    remember = BooleanField(label='Remember me')
    submit = SubmitField(label='Login')


class PostForm(FlaskForm):
    content = TextAreaField(label='Content')
    media = FileField(label='Upload pic', validators=[
        FileAllowed(('jpeg', 'jpg', 'png'))
    ])
    submit = SubmitField(label='Post')


class CommentPostForm(FlaskForm):
    content = TextAreaField(label='Comment')
    submit = SubmitField(label='Post')


class AccountUpdateForm(FlaskForm):
    username = StringField(label='Change Username', validators=[
        DataRequired(),
        Length(min=2, max=20)
    ])
    email = StringField(label='Change Email', validators=[
        DataRequired(),
        Email()
    ])
    picture = FileField(label='Upload new profile pic', validators=[
        FileAllowed(('jpg', 'png'))
    ])
    submit = SubmitField(label='Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if ' ' in username.data:
                raise ValidationError("Username cannot contain spaces.")
            if user:
                raise ValidationError("Username is already take.")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("Email is already taken.")


class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                'There is no account with that email. Please register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(),
                    EqualTo('password')])
    submit = SubmitField('Reset Password')

    def validate_password(self, password):
        if ' ' in password.data:
            raise ValidationError("Password cannot contain spaces.")
        if not re.search(r'[A-Z]', password.data):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password.data):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', password.data):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|-<>]', password.data):
            raise ValidationError("Password must contain at least one special character.")
