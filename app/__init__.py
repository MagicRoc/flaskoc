# -*-coding: utf-8 -*-
from flask import Flask
from flask import request	#请求上下文
from flask import current_app    #程序上下文
from flask_script import Manager,Shell
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime   #获取当前时间  datetime.utcnow()
from flask_wtf import Form    #web表单都要继承Form
from wtforms import StringField  #表单中的文本字段
from wtforms import SubmitField    #表单中的提交按钮
from wtforms.validators import Required
from flask import session   #用户会话
from flask import url_for  # URL生成函数
from flask import redirect   #生成http重定向的响应
from flask import flash   #提示  给用户信息
from flask_sqlalchemy import SQLAlchemy    #数据库管理
from flask_script import Shell  #继承shell，自动导入
from flask_migrate import Migrate  #数据库迁移框架
from flask_migrate import MigrateCommand  #为数据库迁移命令导入到shell
from flask_mail import Message
from flask_mail import Mail
from threading import Thread  #多线程发送邮件
from config import config
from flask_login import LoginManager  #登录管理

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'  #设置为strong时，flask_login会记录客户端IP和浏览器的用户代理信息
login_manager.login_view = 'auth.login'  #设置登录页面的端点
def create_app(config_name):  #创建app
    app = Flask(__name__)
    app.config.from_object(config[config_name])  #将配置类中的配置导入程序
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint  #导入蓝本main
    app.register_blueprint(main_blueprint)  #在主程序中注册蓝本

    from .auth import auth as auth_blueprint  #同上
    app.register_blueprint(auth_blueprint, url_prefix='/auth')  #此蓝本中定义的路由都会加上此前缀


    return app