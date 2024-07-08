import requests

from .base_class import BaseClass


relation_keys = ["subject", "subject_type", "subject_start", "subject_end",
                 "object", "object_type", "object_start", "object_end"]


class ExtractImpl(BaseClass):
    def __init__(self, service_config):
        self.service = service_config.get("service")
        self.langs = service_config.get("langs")

    def url(self, algo, lang="zh"):
        return f'{self.service[algo]}/{self.langs[lang]}/v1'

    def extract_ner(self, data, lang="zh"):
        res = {}
        for i, doc in enumerate(data):
            key = str(i)
            params = {
                "text": doc
            }
            resp = requests.post(self.url("ner", lang), json=params)

            if resp.status_code != 200:
                res[key] = None
                continue
            resp_data = resp.json()
            ners = resp_data["ner"].get("ners", [])
            ners_new = []
            for ner in ners:
                ners_new.append({
                    "entity_name": ner["text"],
                    "entity_type": ner["ner_type"],
                    "start": ner["start"],
                    "end": ner["end"]
                })
            res[key] = [
                {
                    "content": doc,
                    "content_info": ners_new
                }
            ]
            #
            # if "ner" not in resp_data:
            #     return None, "No ner"
            # results = resp_data["ner"].get("ners", [])
        return res, None

    def extract_event(self, data, lang="zh"):
        params = {
            "text": data[0]
        }
        resp = requests.post(self.url("event", lang), json=params)
        if resp.status_code != 200:
            return None, resp.text
        resp_data = resp.json()
        if "events" not in resp_data:
            return None, "No events"
        results = resp_data["events"]

        res = [v for k, v in results.items()]
        return res, None

    def extract_relation(self, data, lang):
        res = {}
        for i, doc in enumerate(data):
            key = str(i)
            params = {
                "text": doc
            }
            resp = requests.post(self.url("relation", lang), json=params)

            if resp.status_code != 200:
                res[key] = None
                continue
            resp_data = resp.json()
            relations = resp_data["relations"]
            print(relations)

            relations_new = []
            for r in relations:
                new_r = {k: r.get(k) for k in relation_keys}
                new_r["relation"] = r.get("predicate")
                relations_new.append({
                    "content": r.get("text"),
                    "content_info": {
                        "relation": new_r
                    }
                })
            res[key] = relations_new
            #
            # if "ner" not in resp_data:
            #     return None, "No ner"
            # results = resp_data["ner"].get("ners", [])
        return res, None
