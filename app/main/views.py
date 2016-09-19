
# -*-coding: utf-8 -*-
from .forms import NameForm
from ..models import User
from flask import session
from flask import current_app, request
from flask import url_for
from flask import render_template
from flask import redirect
from datetime import datetime
from . import main
from .. import db
from ..email import send_email
from flask import flash
from flask import abort
from flask import render_template, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import Role, User, Post
from ..decorators import admin_required
from ..models import Permission

# @main.route('/',methods = ['POST','GET'])   #请求方式不管是post还是get都执行这个视图函数
# def index():
#     form = NameForm()  #表单实例
#     if form.validate_on_submit():   #提交按钮是否成功点击
#          # 从数据库中查找和表单数据一样的数据，如果有，取第一个数据
#         user = User.query.filter_by(username = form.name.data).first()
#         if user is None:   #如果数据库中没有对应的数据
#             user = User(username = form.name.data)  #在数据库中对应的表中创建数据
#             db.session.add(user)  #加入到用户会话，以便数据库进行提交
#             session['known'] = False  #这是一个新用户
#             if current_app.config['FLASKY_ADMIN']:  #如果收件人已经定义，则调用发送邮件函数
#                 send_email(current_app.config['FLASKY_ADMIN'],'New User','mail/new_user',user = user)
#                 flash('The mail has been sent out')
#         else:
#             session['known'] = True  #这是一个老用户
#         session['name'] = form.name.data   #从表单获取数据
#         return redirect(url_for('.index'))
#     return render_template('index.html',current_time = datetime.utcnow(),
#                            form = form,name=session.get('name'),known = session.get('known'))


#  处理文章路由
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    #  发博客
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)  #保存到数据库
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)  #渲染第几页，默认第一页
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination)




@main.route('/user/<username>')  #显示用户信息
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)
#  普通用户编辑资料路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


#  管理员编辑资料路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


