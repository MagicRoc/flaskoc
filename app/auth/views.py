#-*-coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetForm, PasswordResetRequestForm
from .. import db
from ..email import send_email
from flask_login import current_user


#  登录函数
@auth.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            #   login_user() 函数的参数是要登录的用户，以及可选的“记住我”布
            #   尔值，“记住我”也在表单中填写。如果值为 False ，那么关闭浏览器后用户会话就过期
            #   了，所以下次用户访问时要重新登录。如果值为 True ，那么会在用户浏览器中写入一个长
            #   期有效的 cookie
            login_user(user, form.remember_me.data)
            #   用户访问未授权的 URL 时会显示登录表单，Flask-Login
            #   会把原地址保存在查询字符串的 next 参数中，这个参数可从
            #   request.args 字典中读取。
            #   如果查询字符串中没有 next 参数，则重定向到首页
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form = form)




#  退出登录
@auth.route('/logout')
@login_required   #  确保只有登录后才可以
def logout():
    #  删除并重设用户会话
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


#  注册函数
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()  #生成令牌
        send_email(user.email, 'Confirm Your Account','auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


#  验证邮箱函数
@auth.route('/confirm/<token>')
@login_required  #确保用户登录才能执行此函数
def confirm(token):
    if current_user.confirmed:  #如果用户已经认证过
        return redirect(url_for('main.index'))
    if current_user.confirm(token):  #如果用户没有经过验证，则执行当前用户的confirm函数
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

#  如果一个用户未验证，怎么能避免此用户进入main蓝本的路由  答案：钩子
#  钩子函数：定义一个函数，在每个请求前执行此函数
#  钩子函数  如果满足此三个条件则重定向到未验证页面
@auth.before_app_request
def before_request():

    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))


#  未验证页面，此页面提示用户验证邮件，或者重新发送验证邮件
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:  #如果用户验证过重定向到主界面
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


#  重新发送邮件函数
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))



#  修改密码
@auth.route('/',methods = ['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form = form)



@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
