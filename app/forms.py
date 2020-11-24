from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import (FloatField, IntegerField, PasswordField, SelectField,
                     StringField, SubmitField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)
from app.models import User


dr = DataRequired(message='字段格式不合法')


class LoginForm(FlaskForm):
    username    = StringField('用户名', validators=[dr])
    password    = PasswordField('密码', validators=[dr])
    submit      = SubmitField('登录')


class RegistrationForm(FlaskForm):
    username  = StringField('用户名', validators=[dr])
    email     = StringField('电子邮箱', validators=[dr, Email(message='无效的电子邮箱格式')])
    password  = PasswordField('密码', validators=[dr])
    password2 = PasswordField('重复密码', \
        validators=[dr, EqualTo('password', message='两次输入的密码不一致')])
    submit    = SubmitField('注册')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError('用户名已被注册')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError('电子邮箱已被注册')


class UnitForm(FlaskForm):
    name      = StringField('姓名', validators=[dr, Length(min=1, max=64)])
    member_id = IntegerField('人员编号', validators=[dr])
    age       = IntegerField('年龄', validators=[dr])
    height    = FloatField('身高(cm)', validators=[dr])
    weight    = FloatField('体重(kg)', validators=[dr])
    submit    = SubmitField('提交')


class RecordForm(FlaskForm):
    unit_id = SelectField('人员', coerce=int)
    submit  = SubmitField('提交')


class ChangePasswordForm(FlaskForm):
    password      = PasswordField('当前密码', validators=[dr])
    new_password  = PasswordField('新密码', validators=[dr])
    new_password2 = PasswordField('确认新密码', \
        validators=[dr, EqualTo('new_password', message='两次输入的密码不一致')])
    submit        = SubmitField('修改')

    def validate_password(self, field):
        if check_password_hash(current_user.password_hash, field.data) is False:
            raise ValidationError('当前密码错误')
