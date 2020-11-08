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
    age       = IntegerField('年龄', validators=[Optional()])
    height    = FloatField("身高(cm)", validators=[Optional()])
    weight    = FloatField("体重(kg)", validators=[Optional()])
    submit    = SubmitField('提交')


class RecordForm(FlaskForm):
    unit_id = SelectField('人员', coerce=int)
    AGE = FloatField("年龄", validators=[DataRequired()])
    HEIGHT = FloatField("身高", validators=[DataRequired()])
    WEIGHT = FloatField("体重", validators=[DataRequired()])
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
    gender = SelectField("性别", coerce=int, choices=[(0, '男'), (1, "女")])
    age = IntegerField('年龄', validators=[DataRequired()])
    contact_history = SelectField("是否接触过COVID-19感染者", coerce=int, choices=[(0, '否'), (1, "是")])
    acid_test = SelectField("核酸检测结果", coerce=int, choices=[(0, '阴性'), (1, '阳性')])
    x_ray = SelectField("X光检测结果", coerce=int, choices=[(0, '阴性'), (1, '阳性')])
    wbc = FloatField("WBC(白细胞数量)", validators=[DataRequired()])
    rbc = FloatField("RBC(红细胞数量)", validators=[DataRequired()])
    hgb = FloatField("HGB(血红蛋白数量)", validators=[DataRequired()])
    continent = StringField('洲', validators=[DataRequired()])
    country = StringField('国家', validators=[DataRequired()])
    submit = SubmitField('提交')
