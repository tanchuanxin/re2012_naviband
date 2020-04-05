from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField


class RegisterForm(FlaskForm):
    nric = StringField('NRIC')
    name = StringField('Name')
    age = IntegerField('Age')
    register = SubmitField("Register")


class AppointmentForm(FlaskForm):
    ticket = StringField('Ticket')
    venue = StringField('Venue')
    time = StringField('Time')
    book = SubmitField('Book appointment')
