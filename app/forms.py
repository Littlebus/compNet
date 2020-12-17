from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import (FloatField, IntegerField, PasswordField, StringField,
                     SubmitField)
from wtforms.validators import (DataRequired, EqualTo, Length, NumberRange,
                                ValidationError)


dr = DataRequired(message='字段格式不合法')


class LoginForm(FlaskForm):
    username    = StringField('用户名')
    password    = PasswordField('密码')
    submit      = SubmitField('登录')


class SignupForm(FlaskForm):
    username  = StringField('用户名')
    password  = PasswordField('密码')
    password2 = PasswordField('重复密码')
    submit    = SubmitField('注册')


class PasswdForm(FlaskForm):
    password      = PasswordField('当前密码')
    new_password  = PasswordField('新密码')
    new_password2 = PasswordField('确认新密码')
    submit        = SubmitField('修改')


class RecordForm(FlaskForm):
    name   = StringField('姓名', validators=[dr, Length(min=1, max=64)])
    age    = IntegerField('年龄', validators=[dr])
    height = FloatField('身高(cm)', validators=[dr])
    weight = FloatField('体重(kg)', validators=[dr])
    submit = SubmitField('提交')


class EvaluateForm(FlaskForm):
    vrci   = FloatField('VRCI', validators=[dr, NumberRange(min=0, max=20)])
    submit = SubmitField('预测')
