#!/usr/bin/env python
# -*-coding: utf-8 -*-
import os
from app import create_app, db  #导入创建app函数和初始化后的数据库
from app.models import User, Role, Post #导入两个模型 上下文使用
from flask_script import Manager, Shell  #命令解析行  上下文
from flask_migrate import Migrate, MigrateCommand  #数据库迁移  数据库迁移命令与script

app = create_app('default')  #默认方式创建app
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():  #解析行获取上下文，避免频繁导入
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)  #数据库迁移命令与命令行联合


@manager.command  #单元测试
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()
