from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('ایمیل', validators=[DataRequired(), Email()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    confirm_password = PasswordField('تایید رمز عبور', validators=[DataRequired(), EqualTo('password',
                                                                                           message='رمز عبور و تایید رمز عبور باید مطابقت داشته باشند.')])
    submit = SubmitField('ثبت نام')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('این نام کاربری قبلاً انتخاب شده است. لطفاً نام دیگری انتخاب کنید.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('این ایمیل قبلاً ثبت شده است. لطفاً ایمیل دیگری وارد کنید.')


class LoginForm(FlaskForm):
    email = StringField('ایمیل', validators=[DataRequired(), Email()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    remember = BooleanField('مرا به خاطر بسپار')
    submit = SubmitField('ورود')


class UploadFileForm(FlaskForm):
    file = FileField('انتخاب فایل JSON', validators=[FileAllowed(['json'], 'فقط فایل‌های JSON مجاز هستند!')])
    submit = SubmitField('بارگذاری')
