import logging
from flask import Blueprint, request
import json

from config import API_PREFIX, NLU_CONFIGS, all_langs, all_tasks
from util import utils

from service.nlu_schema_service import get_schema

logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)
api = Blueprint('NLU Genernal API', __name__)


def get_impl_class(name):
    clz = f"service.extract_impl.{name}"
    try:
        mod = __import__(clz, fromlist=(clz,))
        return mod.ExtractImpl
    except:
        return None


@api.route(API_PREFIX + "/<service>/", methods=["GET", "POST"])
def nlu_schema(service):
    """
    获取算法schema
    :param service:
    :return:
    """
    return utils.asJson(data=get_schema(service))


@api.route(API_PREFIX + "/<service>/<algorithm>/<lang>", methods=["POST"])
def nlu_service(service, algorithm, lang):
    """
    算法集成接口 实现统一算法
    :param algorithm:
    :param lang:
    :param service:
    :return:
    """
    if lang not in all_langs:
        return utils.asJson(code=40000, msg="Language not supported: "+lang)
    if algorithm not in all_tasks:
        return utils.asJson(code=40000, msg="Model not supported: "+algorithm)
    data = request.json
    if not data:
        return utils.asJson(code=40000, msg="No Body")
    if isinstance(data, dict):
        if "data" not in data:
            return utils.asJson(code=40000, msg="No data")
        data = data["data"]
    config = NLU_CONFIGS.get(service, {})
    clz_constructor = get_impl_class(service)
    if clz_constructor is None:
        return utils.asJson(code=50000, msg="NLU service not available: "+ service)
    extractor = clz_constructor(config)
    error = None
    if algorithm == "ner":
        res, error = extractor.extract_ner(data, lang)
    elif algorithm == "event":
        res, error = extractor.extract_event(data, lang)
    elif algorithm == "relation":
        res, error = extractor.extract_relation(data, lang)

    if error:
        return utils.asJson(code=50000, msg=error)

    # return utils.asJson(data=res)
    return json.dumps(res, ensure_ascii=False)


@api.route(API_PREFIX + "/<service>/<algorithm>/<lang>/schema", methods=["GET"])
def nlu_schema_v1(service, algorithm, lang):
    # return utils.asJson(data=get_schema(service))
    return json.dumps(get_schema(service), ensure_ascii=False)
