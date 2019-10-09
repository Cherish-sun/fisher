from . import web
from flask import render_template, request, redirect, url_for, flash
from app.forms.auth import RegisterForm, LoginForm, EmailForm, ResetPassWord
from app.models.user import User
from app.models.base import db
from flask_login import logout_user, login_user, current_user
from app.libs.email import send_email


@web.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        with db.auto_commit():
            user = User()
            user.set_attrs(form.data)
            db.session.add(user)
            return redirect(url_for('web.login'))
    return render_template('auth/register.html', form=form)


@web.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.cheack_password(form.password.data):
            # 实质是把用户的票据信息写入cookie中
            # 用户身份 get_id
            # cookie 默认 一次性的
            # remember=True 免登录 默认365
            # 可以设置cookie的过期时间
            login_user(user, remember=True)
            next = request.args.get('next')
            if not next or not next.startswith('/'):
                next = url_for('web.index')
            return redirect(next)
        else:
            flash('用户名或密码错误！')
    return render_template('auth/login.html', form=form)


@web.route('/reset/password', methods=['GET', 'POST'])
def forget_password_request():
    form = EmailForm(request.form)
    if request.method == 'POST':
        if form.validate():
            account_email = form.email.data
            user = User.query.filter_by(email=account_email).first_or_404()
            # if not user:
            #     raise Exception()
            send_email(form.email.data, '重置你的密码',
                       'email/reset_password', user=user,
                       token=user.generate_token())
            flash('一封邮件已发送到邮箱' + account_email + '，请及时查收')
            return redirect(url_for('web.login'))
    return render_template('auth/forget_password_request.html', form=form)


# @web.route('/reset/password/<token>', methods=['GET', 'POST'])
# def forget_password(token):
#     form = ResetPassWord(request.form)
#     if request.method == 'POST' and form.validate():
#         new_password = form.password2.data
#         result = User.update_pasword_by_token(token, new_password)
#         if result:
#             flash('你的密码已更新,请使用新密码登录')
#             return redirect(url_for('web.login'))
#         else:
#             return redirect(url_for('web.index'))
#     return render_template('auth/forget_password.html')

@web.route('/reset/password/<token>', methods=['GET', 'POST'])
def forget_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('web.index'))
    form = ResetPassWord(request.form)
    if request.method == 'POST' and form.validate():
        result = User.update_pasword_by_token(token, form.password1.data)
        if result:
            flash('你的密码已更新,请使用新密码登录')
            return redirect(url_for('web.login'))
        else:
            flash('密码重置失败')
            return redirect(url_for('web.index'))
    return render_template('auth/forget_password.html')


@web.route('/change/password', methods=['GET', 'POST'])
def change_password():
    pass


@web.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('web.index'))
