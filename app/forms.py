from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import (BooleanField, FloatField, IntegerField, PasswordField,
                     SelectField, StringField, SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length, Optional,
                                ValidationError)
from app.models import User


class LoginForm(FlaskForm):
    username    = StringField('用户名', validators=[DataRequired()])
    password    = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit      = SubmitField('登录')


class RegistrationForm(FlaskForm):
    username  = StringField('用户名', validators=[DataRequired()])
    email     = StringField('电子邮箱', validators=[DataRequired(), Email()])
    password  = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('重复密码', \
        validators=[DataRequired(), EqualTo('password', message='两次输入的密码不一致')])
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
    name      = TextAreaField('姓名', validators=[DataRequired(), Length(min=1, max=64)])
    member_id = IntegerField('人员编号', validators=[DataRequired()])
    age       = IntegerField('年龄', validators=[DataRequired()])
    height    = FloatField("身高(cm)", validators=[DataRequired()])
    weight    = FloatField("体重(kg)", validators=[DataRequired()])
    submit    = SubmitField('提交')


class RecordForm(FlaskForm):
    unit_id = SelectField('人员', coerce=int)
    submit  = SubmitField('提交')


class ChangePasswordForm(FlaskForm):
    password      = PasswordField('当前密码', validators=[DataRequired()])
    new_password  = PasswordField('新密码', validators=[DataRequired()])
    new_password2 = PasswordField('确认新密码', \
        validators=[DataRequired(), EqualTo('new_password', message='两次输入的密码不一致')])
    submit        = SubmitField('修改')

    def validate_password(self, field):
        if check_password_hash(current_user.password_hash, field.data) is False:
            raise ValidationError('当前密码错误')


class ResetPasswordRequestForm(FlaskForm):
    email  = StringField('电子邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField('发送重置密码邮件')


class ResetPasswordForm(FlaskForm):
    password  = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('重复密码', \
        validators=[DataRequired(), EqualTo('password', message='两次输入的密码不一致')])
    submit    = SubmitField('重置密码')


class EvaluateForm(FlaskForm):
    record_id = SelectField('记录', coerce=int)
    submit = SubmitField('提交')
