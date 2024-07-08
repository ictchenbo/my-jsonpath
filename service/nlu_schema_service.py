import os
import json


def load_config(path):
    if not os.path.exists(path):
        return None
    return json.load(open(path))


all_services = load_config("schema.json")


def get_schema(service):
    """
    获取对应服务的Schema
    :param service:
    :return:
    """
    if service in all_services:
        return all_services[service]

    config_file = f"schema_{service}.json"
    schema = load_config(config_file)
    if schema:
        all_services[service] = schema

    return schema
