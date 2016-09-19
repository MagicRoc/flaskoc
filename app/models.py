# -*-coding: utf-8 -*-
from . import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin  #User继承这个类。此类含有四种方法的默认实现
from flask_login import AnonymousUserMixin
from . import login_manager  #实现回调函数
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from datetime import datetime
import hashlib
# generate_password_hash(password, method= •  pbkdf2:sha1, salt_length=8) ：这个函数将
# 原始密码作为输入，以字符串形式输出密码的散列值，输出的值可保存在用户数据库中。
# method 和 salt_length 的默认值就能满足大多数需求。
# check_password_hash(hash, password) •  ：这个函数的参数是从数据库中取回的密码散列
# 值和用户输入的密码。返回值为 True 表明密码正确

class Role(db.Model):  #用户角色表示（用来演示一对多）
    __tablename__ = 'roles' #定义在数据库中使用的表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)  #是否是默认用户
    permissions = db.Column(db.Integer)  #所拥有权限
    users = db.relationship('User', backref='role', lazy = 'dynamic')

    @staticmethod  #此函数在数据库中创建角色，（将角色分配给各用户）
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Permission:  #权限常量
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


    def __repr__(self):      #返回一个可读性的字符串表示模型
        return '<roc de data Role %r>' %self.name

class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)  #index为此列创建索引
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))  #密码散列值
    email = db.Column(db.String(64), unique=True, index=True)  #使用邮箱进行登录
    confirmed = db.Column(db.Boolean, default=False)  #邮箱验证 如果验证成功，则值为True

    name = db.Column(db.String(64))  #真实姓名
    location = db.Column(db.String(64))  #地址
    about_me = db.Column(db.Text())  #我的介绍
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  #注册日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  #最后一次登录信息

    posts = db.relationship('Post', backref='author', lazy='dynamic')  #用户与文章的一对多

    def __init__(self, **kwargs):  #定义默认的用户角色（通过保存在配置文件中的电子邮件）
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):  #检查用户是否拥有此权限
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):  #检查用户是否是管理员
        return self.can(Permission.ADMINISTER)


    @property  #property 将方法设置为属性
    def password(self):  #如果get密码将返回错误
        raise AttributeError('password is not a readable attribute')

    @password.setter  #设置密码散列值
    def password(self, password):  #通过genrate_password_hash()函数将密码转化为散列值保存在数据库
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):  #通过check_password_hash函数接受password和password_hash两个参数，一致返回True
        return check_password_hash(self.password_hash, password)


    def __repr__(self):      #返回一个可读性的字符串表示模型
        return ' <roc de data User %r>' %self.username

    #  生成一个令牌 ，有效期为一小时
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    #  验证令牌 ， 验证成功则把confirm设为True
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def ping(self):  #刷新用户的最后一次访问时间
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=256, default='wavatar', rating='x'):  #用户头像
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


    #  生成虚拟用户
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()




#  这个对象继承自 Flask-Login 中的 AnonymousUserMixin 类，并将其设为用户未登录时
#  current_user 的值。这样程序不用先检查用户是否登录，就能自由调用 current_user.can() 和
#  current_user.is_administrator()
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


    # Flask-Login 要求程序实现一个回调函数，使用指定的标识符加载用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):  #博客文章对应的表
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


    #生成虚拟博客
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()