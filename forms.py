from re import sub
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, SubmitField, FileField, PasswordField, SelectField,DateTimeField,FileField, FloatField, TextAreaField
from wtforms.fields.core import IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from flask_wtf.file import FileAllowed
import datetime

def email_check(form, field):
    data = field.data
    data = data.split('@')
    if (data[1] != '@metu.edu.tr'):
        raise ValidationError('Your mail must be ended with @metu.edu.tr')
    raise ValidationError('Your date is incorrect form.')

class DatabaseConfigForm(FlaskForm):
    host = StringField("Host: ", validators=[DataRequired()])
    user = StringField("User: ", validators=[DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    db = StringField("Database: ", validators=[DataRequired()])
    submit = SubmitField("Register")
    
class UserRegisterForm(FlaskForm):
    name = StringField("Name & Surname: ", validators=[DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    email = EmailField("Email: ", validators=[DataRequired()])
    department = SelectField("Department: ", choices=[('355','CNG'),('500','EEE')], validators=[DataRequired()])
    year = IntegerField("Starting year to METU: ",validators=[NumberRange(min=2002,max=datetime.datetime.now().year)])
    stuID = StringField("Student ID: ", validators=[Length(max=7,min=7)])
    submit = SubmitField("Register")

class UserLoginForm(FlaskForm):
    email = EmailField("Email: " , validators=[DataRequired()])
    password = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("Login")

class ChangePassword(FlaskForm):
    password = PasswordField("Password: ", validators=[DataRequired()])
    submit = SubmitField("Change Password")

class EventCreationForm(FlaskForm):
    event_name = StringField("Event Name: ", validators=[DataRequired()])
    event_date = DateTimeField("Event (dd-mm-yyyy hh:mm:ss): ", validators=[DataRequired()], format='%d-%m-%Y %H:%M:%S')
    description = TextAreaField("Description of the Event: ")
    poster = FileField("Poster: ", validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    guest_name = StringField("Guest Name(s) (split with ',' if more than one): ", validators=[DataRequired()])
    submit = SubmitField("Create")

class CreateSocietyForm(FlaskForm): #Advisor oluşturma formu, 
    email = EmailField("Society Email: ", validators=[DataRequired()])
    name = StringField("Society Name: ",validators=[DataRequired()])
    logo = FileField("Logo: ", validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    password = PasswordField("Password: ", validators=[DataRequired()])
    budget = FloatField("Budget: ", validators=[DataRequired()])
    description = TextAreaField("Describe the Society: ")
    advisor_email = EmailField("Advisor Email: ", validators=[DataRequired()])
    submit = SubmitField("Create")

class CreateAdvisor(FlaskForm):
    email = EmailField("Email: ", validators=[DataRequired()])
    name = StringField("Name - Surname: ",validators=[DataRequired()] )
    password = PasswordField("Password: ", validators=[DataRequired()])
    department = SelectField("Department: ", choices=[('355','CNG'),('500','EEE')], validators=[DataRequired()])
    submit = SubmitField("Create")

