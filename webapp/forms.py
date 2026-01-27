from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,IntegerField
from wtforms.validators import DataRequired,Length,Email,Regexp,EqualTo,ValidationError,NumberRange
from webapp.models import User




class RegistrationForm(FlaskForm):
    fname = StringField('First Name',validators=[DataRequired(),Length(min=2,max=25)])
    lname = StringField('Last Name',validators=[DataRequired(),Length(min=2,max=25)])
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=25)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Regexp(
               r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,32}$",
               message="Password must be 8-32 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character."
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit_btn = SubmitField("Sign Up")

    def validate_username(self, username):
   
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already exists! Please choose a different one"
            )

    def validate_email(self, email):
        # with app.app_context():
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already exists! Please choose a different one")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
        ],
    )
    remember = BooleanField("Remember Me")
    submit_btn = SubmitField("Log In")

