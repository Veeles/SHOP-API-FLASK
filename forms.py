from flask import Flask, render_template, request 
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField 
from wtforms import DecimalField, RadioField, SelectField, TextAreaField, FileField , EmailField, validators
from wtforms.validators import InputRequired, EqualTo

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()] )
    password = PasswordField('Password', validators=[InputRequired(), EqualTo('confirm', message = 'Password must match')] )
    confirm = PasswordField('Repeat Password')
    email = EmailField('Email',[validators.DataRequired(), validators.Email()])

class LoginForm(FlaskForm):
    email = EmailField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', validators=[InputRequired()])