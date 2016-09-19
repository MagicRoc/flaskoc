#-*-coding: utf-8-*-
import unittest
from app import create_app, db
from app.models import User, Role, AnonymousUser, Permission

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)  #测试password_hash不为空

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):  #测试password不可得到
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))  #测试密码验证通过
        self.assertFalse(u.verify_password('dog'))  #测试密码验证不过

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)  #测试同密码的散列值不一样

    def test_roles_and_permissions(self):
        Role.insert_roles()

        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMENTS))

    def test_anonymous_user(self):
        u = AnonymousUser()

        self.assertFalse(u.can(Permission.FOLLOW))