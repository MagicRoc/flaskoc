#-*-coding: utf-8-*-
import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
    def setUp(self):  #测试前执行
        self.app = create_app('testing')
        self.app_context = self.app.app_context()  #激活程序上下文
        self.app_context.push()
        db.create_all()  #创建数据库

    def tearDown(self):  #测试后执行
        db.session.remove()
        db.drop_all()
        self.app_context.pop()  #删除程序上下文

    def test_app_exists(self):
        self.assertFalse(current_app is None)  #测试确保程序实例存在

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])  #测试确保程序在测试配置中运行
