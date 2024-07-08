# -*- coding: utf-8 -*-
"""
@File : config.py
配置文件
@Author : chenbo(chenbo@golaxy.cn)
@Time : 2022/1/1 00:01
"""
import os
import yaml

# 本服务的端口
SERVICE_PORT = 6150
# 服务名称
APP_NAME = "jsonql"
# 本服务 URL前缀
API_PREFIX = '/nlu/v1.0'


all_langs = ["zh", "en"]
all_tasks = ["ner", "event", "relation"]

profile = os.environ.get("mode", "dev")

NLU_CONFIGS = yaml.load(open(f"application-{profile}.yml"), yaml.Loader)

STORE_SERVICE = "http://10.208.63.15/store/v3.0/gox_config/services"
