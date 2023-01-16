# encoding: utf-8

"""
@author: lin
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: 739217783@qq.com
@software: Pycharm
@file: txt.py
@time: 2022/5/21 22:02
@desc:
"""
def convert_cookies_to_dict(cookies):
    cookies = dict([l.split("=", 1) for l in cookies.split("; ")])
    return cookies

a=' _ga=GA1.1.1342262260.1647614122; token=ZmY4MDgwODE3ZjlkMGZlNjAxN2Y5ZDc0NjhhNjJkOTc=; _ga_6JB799PF8P=GS1.1.1653136707.92.1.1653138252.0'

print(convert_cookies_to_dict(a))

