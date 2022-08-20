from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from pbook.models import Stores


class RegisterForm(FlaskForm):
    storeName = StringField('Store Name',
                            validators=[DataRequired(), Length(min=2, max=20)])

    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, storeName):
        user = Stores.query.filter_by(username=storeName.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    storeName = StringField('Store Name',
                            validators=[DataRequired(), Length(min=2, max=10)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class SettingForm(FlaskForm):
    g1 = StringField('Girl One', validators=[Length(min=1, max=6)])
    g2 = StringField('Girl Two', validators=[Length(min=1, max=6)])
    g3 = StringField('Girl Thr', validators=[Length(min=1, max=6)])
    g4 = StringField('Girl For', validators=[Length(min=1, max=6)])

    t130 = IntegerField(validators=[Length(min=1, max=3)])
    t160 = IntegerField(validators=[Length(min=1, max=3)])
    t170 = IntegerField(validators=[Length(min=1, max=3)])
    t190 = IntegerField(validators=[Length(min=1, max=3)])
    t1120 = IntegerField(validators=[Length(min=1, max=4)])

    t230 = IntegerField(validators=[Length(min=1, max=3)])
    t260 = IntegerField(validators=[Length(min=1, max=3)])
    t270 = IntegerField(validators=[Length(min=1, max=3)])
    t290 = IntegerField(validators=[Length(min=1, max=3)])
    t2120 = IntegerField(validators=[Length(min=1, max=4)])

    t130Comp = IntegerField(validators=[Length(min=1, max=3)])
    t160Comp = IntegerField(validators=[Length(min=1, max=3)])
    t170Comp = IntegerField(validators=[Length(min=1, max=3)])
    t190Comp = IntegerField(validators=[Length(min=1, max=3)])
    t1120Comp = IntegerField(validators=[Length(min=1, max=4)])

    t230Comp = IntegerField(validators=[Length(min=1, max=3)])
    t260Comp = IntegerField(validators=[Length(min=1, max=3)])
    t270Comp = IntegerField(validators=[Length(min=1, max=3)])
    t290Comp = IntegerField(validators=[Length(min=1, max=3)])
    t2120Comp = IntegerField(validators=[Length(min=1, max=4)])

    d1 = StringField('Girl One', validators=[Length(min=1, max=6)])
    d2 = StringField('Girl Two', validators=[Length(min=1, max=6)])
    d3 = StringField('Girl Thr', validators=[Length(min=1, max=6)])
    d4 = StringField('Girl For', validators=[Length(min=1, max=6)])

    submit = SubmitField('保存')
