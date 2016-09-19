#-*-coding: utf-8 -*-
from flask import Blueprint
auth = Blueprint('auth', __name__)  #创建auth蓝本，此蓝本下定义用户用户认证系统相关的路由
from . import views