from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, RadioField, IntegerField
from wtforms.fields import FieldList, FormField
from wtforms.validators import InputRequired, Email, Length, Regexp, EqualTo, Optional, NumberRange, DataRequired, URL

class SignUpForm(FlaskForm):
    """Form that signup users"""

    first_name = StringField("Firstname", validators=[DataRequired(message="Firstname cannot be blank")])
    
    last_name = StringField("Lastname", validators=[DataRequired(message="Lastname cannot be blank")])
    
    email = StringField("E-Mail", validators=[InputRequired(), Email()])

    department = SelectField("Department", validators=[InputRequired()], choices=[("hardlines", "Hardlines"), ("freezer", "Freezer"), 
                                            ("receiving", "Receiving"), ("sundries","Sundries")])

    password = PasswordField("Password", validators=[InputRequired(), EqualTo("confirm", message="Passwords must match"), 
                                        Regexp("^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})"
                                                ,flags=0,
                                                message=
                                                """Password must be 8 characters or greater long, 
                                                password must contain at least 1 capital letter, 
                                                password must contain at least 1 number,
                                                password must contain at least 1 special character""")])
                                                                    
    confirm = PasswordField("Confirm Password")

    image_url = StringField("Image Url", validators=[Optional(), URL(message="Image must be an URL")])

    user_role = SelectField("Role", validators=[InputRequired()], choices=[(1, "Stocker"), (2, "Forklift Driver")], coerce=int)

    # user_type = RadioField("Are you a...", validators=[InputRequired()], choices=[("Stocker", "stocker"), ("Forklift Driver", "driver")])

class EditUserForm(FlaskForm):
    """Form that signup users"""

    first_name = StringField("Firstname", validators=[DataRequired(message="Firstname cannot be blank")])
    
    last_name = StringField("Lastname", validators=[DataRequired(message="Lastname cannot be blank")])
    
    email = StringField("E-Mail", validators=[InputRequired(), Email()])

    department = SelectField("Department", validators=[InputRequired()], choices=[("hardlines", "Hardlines"), ("freezer", "Freezer"), 
                                            ("receiving", "Receiving"), ("sundries","Sundries")])

    current_password = PasswordField("Enter Current Password to save settings", validators=[InputRequired()])

    image_url = StringField("Image", validators=[Optional()])

    current_role_id = SelectField("Role", validators=[InputRequired()], choices=[(1, "Stocker"), (2, "Forklift Driver")], coerce=int)

class LoginForm(FlaskForm):
    """Form for authenticating a user"""
    email = StringField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class ItemForm(FlaskForm):
    """Form for items"""
    location_id = SelectField("Location", validators=[InputRequired()], coerce=int)
    row_letter = SelectField("Row", validators=[InputRequired()], choices=[("a", "A"), ("b", "B"), ("c", "C")])
    column_number = IntegerField("Column", validators=[InputRequired(), NumberRange(min=1, max=100)])
    description = StringField("Description")

    def set_choices(self, db, obj):
        self.location_id.choices = db.session.query(obj.id, obj.name).all()

class DropListForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired(message="Description cannot be blank"), Length(min=3, max=100)])

    department = SelectField("Department", validators=[InputRequired()], choices=[("hardlines", "Hardlines"), ("freezer", "Freezer"), 
                                            ("receiving", "Receiving"), ("sundries","Sundries")], coerce=str)
    # forklift_driver_id = SelectField("Forklift Driver", validators=[Optional()], coerce=int)

    def set_choices(self, db, ForkliftDriver, User):
        self.forklift_driver_id.choices = db.session.query(
                                        ForkliftDriver.id, User.first_name +" "+ User.last_name).join(
                                            ForkliftDriver, User.id == ForkliftDriver.user_id).all()

class LocationForm(FlaskForm):
    """Location form"""
    name = StringField("Location", validators=[InputRequired()])

class ItemForm(FlaskForm):
    """Form for items"""
    row_letter = SelectField("Row", validators=[InputRequired()], choices=[("a", "A"), ("b", "B"), ("c", "C")])
    column_number = IntegerField("Column", validators=[InputRequired(), NumberRange(min=1, max=100)])
    description = StringField("Description")
    location_id = SelectField("Location", validators=[InputRequired()], coerce=int)

    def set_choices(self, db, obj):
        self.location_id.choices = db.session.query(obj.id, obj.name).all()