from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, RadioField
from wtforms.validators import InputRequired, Email, Length, Regexp, EqualTo, Optional

class SignUpForm(FlaskForm):
    """Form that signup users"""

    first_name = StringField("First Name", validators=[InputRequired()])
    
    last_name = StringField("Last Name", validators=[InputRequired()])
    
    email = StringField("E-Mail", validators=[InputRequired(), Email()])

    department = SelectField("Department", validators=[InputRequired()], choices=[("Hardlines", "hardlines"), ("Freeze", "freezer"), 
                                            ("Receiving", "receiving"), ("Sundries","sundries")])

    password = PasswordField("Password", validators=[InputRequired(), EqualTo("confirm", message="Passwords must match"), 
                                        Regexp("^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})"
                                                ,flags=0,
                                                message=
                                                """Password must be 8 characters or greater long, 
                                                password must contain at least 1 capital letter, 
                                                password must contain at least 1 number,
                                                password must contain at least 1 special character""")])
                                                                    
    confirm = PasswordField("Repeat Password")

    image_url = StringField("Image", validators=[Optional()])

    user_type = RadioField("Are you a...", validators=[InputRequired()], choices=[("Stocker", "stocker"), ("Forklift Driver", "driver")])
