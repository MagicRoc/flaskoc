 # -*- coding: utf-8 -*- 
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
import os
app = Flask(__name__)

app.config['SECRET_KEY'] = 'Hard to guess string'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['MAIL_SERVER'] = 'smtp.163.com'  #邮箱服务器
app.config['PORT'] = 587  #使用端口号
app.config['MAIL_USE_TLS'] = False  #是否使用这个
app.config['MAIL_USERNAME'] = '15518997683@163.com'  #用户邮箱
app.config['MAIL_PASSWORD'] = 'hh3312594852'  #邮箱密码
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[flasky]'  #邮箱主题
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <15518997683@163.com>'  #邮箱发件人
app.config['FLASKY_ADMIN'] = '917086506@qq.com'

#__file__文件的目录  包含文件名
#os.path.dirname  此文件的当前目录  不包含文件名
#os.path.abspath  此目录的绝对路径
#os.path.join   将多个路径组合后返回
basedir = os.path.abspath(os.path.dirname(__file__))   #获取文件绝对路径
app.config['SQLALCHEMY_DATABASE_URI'] = \
'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')    #使用的数据库URL保存到flask配置对象
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True    #每次请求结束都会自动提交数据库中的变动

bootstrap = Bootstrap(app)	#渲染
moment = Moment(app)       #时间
manager = Manager(app)    #script   命令行解析器
mail = Mail(app)

db = SQLAlchemy(app)   #db表示程序使用的数据库  并获得了flask-sqlalchemy的所有功能
migrate = Migrate(app,db)  #初始化Migrate
    #Flask-Migrate 提供一个MigtareCommand，可以把数据库迁移命令附加到manager对象上
manager.add_command('db',MigrateCommand)  #导出数据库迁移命令

class Role(db.Model):
    __tablename__ = 'roles' #定义在数据库中使用的表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy = 'dynamic')
    def __repr__(self):      #返回一个可读性的字符串表示模型
        return '<roc de data Role %r>' %self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)  #index为此列创建索引
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    def __repr__(self):      #返回一个可读性的字符串表示模型
        return ' <roc de data User %r>' %self.username



#使用flask-wtf时每个web表单都继承Form
#validators 是一个由验证函数组成的列表，在接受用户提交的数据之前验证数据
#验证函数Required 确保提交的字段不为空
class NameForm(Form):
    name = StringField('what is you name?',validators = [Required()])
    submit = SubmitField('Submit')


def send_async_email(app,msg):  #子线程发送邮件函数
    with app.app_context():  #创建程序上下文
        mail.send(msg)  #发送邮件

def send_email(to, subject, template, **kwargs):
     # Message(主题，发件人，收件人)
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
     # target：函数名   args：函数参数列表
    thr = Thread(target=send_async_email, args=[app, msg])  #创建发送邮件的子线程
    thr.start()  #子线程启动
    #return thr

@app.route('/',methods = ['POST','GET'])   #请求方式不管是post还是get都执行这个视图函数
def index():
    form = NameForm()  #表单实例
    if form.validate_on_submit():   #提交按钮是否成功点击
         # 从数据库中查找和表单数据一样的数据，如果有，取第一个数据
        user = User.query.filter_by(username = form.name.data).first()
        if user is None:   #如果数据库中没有对应的数据
            user = User(username = form.name.data)  #在数据库中对应的表中创建数据
            db.session.add(user)  #加入到用户会话，以便数据库进行提交
            session['known'] = False  #这是一个新用户
            if app.config['FLASKY_ADMIN']:  #如果收件人已经定义，则调用发送邮件函数
                send_email(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user = user)
                flash('The mail has been sent out')
        else:
            session['known'] = True  #这是一个老用户
        session['name'] = form.name.data   #从表单获取数据
        return redirect(url_for('index'))
    return render_template('index.html',current_time = datetime.utcnow(),
                           form = form,name=session.get('name'),known = session.get('known'))

@app.route('/user/<name>')
def name(name):
    return render_template('user.html',name = name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.errorhandler(500)  
def internal_sever_error(e):
    return render_template('500.html')


def make_shell_context():  #注册一个回调函数，自动把对象导入shell
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == '__main__':
    app.run()
