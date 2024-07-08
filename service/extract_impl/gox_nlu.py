import requests

from .base_class import BaseClass


class ExtractImpl(BaseClass):
    def __init__(self, service_config):
        self.service = service_config.get("service")

    def extract(self, algo, lang, data):
        url = f'{self.service[algo]}'
        res = requests.post(url, json=data)
        if res.status_code == 200:
            return res.json()
        return None

    def extract_ner(self, data, lang="zh"):
        return self.extract("ner", lang, data)

    def extract_event(self, data, lang="zh"):
        return self.extract("event", lang, data)

    def extract_relation(self, data, lang="zh"):
        return self.extract("relation", lang, data)
