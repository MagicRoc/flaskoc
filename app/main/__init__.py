# -*-coding: utf-8 -*-

from flask import Blueprint
main = Blueprint('main',__name__)  #两个参数，蓝本名字和蓝本所在的包或者模块
from . import views,errors
from ..models import Permission
@main.app_context_processor  #在模板中也需要验证权限，将Permission设为模板上下文，避免每次传参
def inject_permissions():
    return dict(Permission=Permission)