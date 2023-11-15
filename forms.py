from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, DateField, StringField, PasswordField, SelectField, IntegerField
from wtforms.validators import InputRequired, EqualTo


class registerForm(FlaskForm):
    user_id = StringField("User id:", validators = [InputRequired()])
    password = PasswordField("Password:", validators = [InputRequired()])
    confirm_password = PasswordField("Confirm password:", validators = [InputRequired(), EqualTo("password")])
    register = SubmitField("Register")

class loginForm(FlaskForm):
    user_id = StringField("User id:", validators = [InputRequired()])
    password = PasswordField("Password:", validators = [InputRequired()])
    login = SubmitField("Login")

class transactionForm(FlaskForm):
    category = SelectField("Category",choices = ["Groceries", "Healthcare", "Restaurants", "Beauty", "Transport", "Other"], 
                           validators = [InputRequired()])
    date = DateField("Date of the transaction:", validators = [InputRequired()])
    amount = FloatField("Amount:", validators = [InputRequired()])
    add = SubmitField("Add")
