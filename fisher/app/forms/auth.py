from wtforms import Form, StringField, IntegerField, PasswordField
from wtforms.validators import NumberRange, Length, DataRequired, Email, ValidationError, EqualTo
from wtforms import Form, StringField, IntegerField
from app.models.user import User


class RegisterForm(Form):
    email = StringField(validators=[DataRequired(), Length(8, 64), Email(message='电子邮箱不符合规范')])
    nickname = StringField('昵称', validators=[
        DataRequired(), Length(2, 10, message='昵称至少需要两个字符，最多10个字符')])

    password = PasswordField('密码', validators=[
        DataRequired(), Length(6, 20)])

    def validate_email(self, filed):
        if User.query.filter_by(email=filed.data).first():
            raise ValidationError('该邮箱已经注册！')

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('昵称已存在')


class EmailForm(Form):
    email = StringField('电子邮件', validators=[DataRequired(), Length(1, 64),
                                            Email(message='电子邮箱不符合规范')])


class LoginForm(EmailForm):
    password = PasswordField('密码', validators=[
        DataRequired(message='密码不可以为空，请输入你的密码')])


class ResetPassWord(Form):
    password1 = PasswordField('新密码', validators=[
        DataRequired(), Length(6, 32, message='密码不可以为空，请输入你的密码'), EqualTo('password2', message='两次密码输入'
                                                                                               '不一致')])
    password2 = PasswordField('确认新密码', validators=[DataRequired(), Length(6, 32)])
