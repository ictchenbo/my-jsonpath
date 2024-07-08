# -*- coding: utf-8 -*-
"""
@File : rest_app.py
服务启动入口
@Author : chenbo(chenbo@golaxy.cn)
@Time : 2021/8/22 11:54
"""

if __name__ == '__main__':
    from config import SERVICE_PORT

    from rest_app_base import app
    from web.nlu_controller import api as nlu_api

    app.register_blueprint(nlu_api)

    app.run(host='0.0.0.0', port=SERVICE_PORT, debug=True)
