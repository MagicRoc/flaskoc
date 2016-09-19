#-*- coding: utf-8 -*-
import os
#__file__文件的目录  包含文件名
#os.path.dirname  此文件的当前目录  不包含文件名
#os.path.abspath  此目录的绝对路径
#os.path.join   将多个路径组合后返回
basedir = os.path.abspath(os.path.dirname(__file__))   #获取文件绝对路径

class Config:
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = True  #警告
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.163.com'  #邮箱服务器
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = '15518997683@163.com'  #用户邮箱
    MAIL_PASSWORD = 'hh3312594852'  #邮箱密码
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <15518997683@163.com>'  #邮箱发件人
    FLASKY_ADMIN = '917086506@qq.com'
    FLASKY_POSTS_PER_PAGE = 10

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):  #默认default
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):  #单元测试使用
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-tests.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}