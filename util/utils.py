# -*- coding: utf-8 -*-
"""
@File : utils.py

@Author : yaojianlin(yaojianlin@golaxy.cn)
@Time : 2021/7/2 17:16
"""
import time
import json
import datetime
from flask import make_response


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime.datetime) or isinstance(z, datetime.date):
            return str(z)
        else:
            return super().default(z)


def asJson(data=None, pager=None, code=20000, msg="操作成功"):
    ret = {"code": code}
    if msg:
        ret["message"] = msg
    if data:
        ret["data"] = data
    if pager:
        ret["pager"] = pager

    return asResponse(ret)


def asResponse(ret):
    body = json.dumps(ret, ensure_ascii=False, cls=DateTimeEncoder)
    resp = make_response(body, str(ret["code"] // 100))
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    return resp


def get_time_stamp():
    ts = int(round(time.time() * 1000))
    return ts
