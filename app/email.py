# -*-coding: utf-8 -*-
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail





def send_async_email(app,msg):  #子线程发送邮件函数
    with app.app_context():  #创建程序上下文
        mail.send(msg)  #发送邮件

def send_email(to, subject, template, **kwargs):
     # Message(主题，发件人，收件人)
    app = current_app._get_current_object()  #!!!!!!!!!!!!!!!???????????
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
     # target：函数名   args：函数参数列表
    thr = Thread(target=send_async_email, args=[app, msg])  #创建发送邮件的子线程
    thr.start()  #子线程启动
    #return thr