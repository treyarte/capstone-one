from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, RadioField, IntegerField
from wtforms.validators import InputRequired, Email, Length, Regexp, EqualTo, Optional, NumberRange

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
class LoginForm(FlaskForm):
    """Form for authenticating a user"""
    email = StringField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class DropListForm(FlaskForm):
    notes = TextAreaField("Notes", validators=(Optional(), Length(max=200)))

class LocationForm(FlaskForm):
    """Location form"""
    location = StringField("Location", validators=[InputRequired()])

class ItemForm(FlaskForm):
    """Form for items"""
    row_letter = SelectField("Row", validators=[InputRequired()], choices=[("A", "a"), ("B", "b"), ("C", "c")])
    column_number = IntegerField("Column", validators=[InputRequired(), NumberRange(min=1, max=100)])
    description = StringField("Description")
    location_id = SelectField("Location", validators=[InputRequired()], coerce=int)