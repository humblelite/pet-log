from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, TextAreaField, SelectField
from wtforms.validators import DataRequired


# Form validation for the users signup, users login
# and input for pet name and description
class UserSignup(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(),
                                             validators.Email()])
    password = PasswordField('password', validators=[DataRequired(),
                                                     validators.EqualTo('confirm',
                                                                        message='password must be the same')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('submit')


class UserLogin(FlaskForm):
    username = StringField('Username', validators=[DataRequired('Please enter Username')])
    password = PasswordField('Password', validators=[DataRequired('please enter password')])
    remember = BooleanField('Remember Me', )
    submit = SubmitField('Submit')


class PetForm(FlaskForm):
    animal_type = SelectField('Pet Type', choices=[], coerce=int)
    pet_name = StringField("Pet Name", validators=[DataRequired()])
    pet_desc = TextAreaField("Pet Description", validators=[DataRequired()])
    submit = SubmitField('submit')
