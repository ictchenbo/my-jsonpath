# coding=utf-8
from flask import Flask
from flasgger import Swagger

from config import APP_NAME, API_PREFIX

app = Flask(APP_NAME)
app.config['SWAGGER'] = {
    'title': '通用存储RESTFul API',
    'author': '陈波',
    'description': '提供通用存储服务',
    'version': '3.0',
    'url_prefix': API_PREFIX
    # 'uiversion': 3,
    # 'openapi': '3.0.2'
}


@app.route("/status", methods=["GET"])
def status():
    return {"code": 20000, "data": "OK"}


Swagger(app)
