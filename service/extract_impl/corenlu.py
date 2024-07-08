import requests
import logging

from .base_class import BaseClass

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')
logger = logging.getLogger(__name__)


def parse_event(result):
    data = []
    _nlu_sentences = result.get("_nlu_sentences", [])
    _nlu_event = result.get("_nlu_event", [])
    if len(_nlu_event) != len(_nlu_sentences):
        logger.error("mismatch length")
        return None

    for ind, doc_dict in enumerate(_nlu_sentences):
        if _nlu_event[ind]:
            doc_events = _nlu_event[ind]
            temp_doc = []
            for ind_sent, sent_lst in doc_dict.items():
                ind_sent = int(ind_sent)
                content = " ".join(sent_lst)
                # if doc_events[ind_sent]:
                # 某个句子有事件
                one_sentence_events = []
                one_event = doc_events[ind_sent]
                for ev in one_event:
                    if "argument_list" in ev:
                        argument_list = ev["argument_list"]
                        if argument_list:
                            for arg in argument_list:
                                temp_lst = []
                                role_content = arg["argument_content"]
                                role_type = arg["argument_role"]
                                if "event_type" in ev:
                                    event_type = ev["event_type"]
                                else:
                                    event_type = ""
                                temp_lst.append(role_content)
                                temp_lst.append(role_type)
                                temp_lst.append(event_type)
                                one_sentence_events.append(temp_lst)
                event_dict = {
                    "content": content,
                    "content_info": one_sentence_events
                }
                temp_doc.append(event_dict)
            if temp_doc:
                data.append(temp_doc)
    return data


def parse_ner(result, lang):
    res = {}
    ners = result.get('_nlu_ner', [])
    for i in range(len(ners)):
        ent_list = []
        for k, v in ners[i].items():
            sent = {
                "content": "",
                "content_info": []
            }
            sentence = [i[0] for i in v]
            sentence = ' '.join(sentence)
            if lang == "zh":
                sentence = ''.join(sentence)
            sent["content"] = sentence

            for pos in v:
                content_info_one = {}
                if pos[1] != 'O':
                    content_info_one['entity_name'] = pos[0]
                    content_info_one['entity_type'] = pos[1]
                    content_info_one['start'] = sentence.find(pos[0])
                    content_info_one['end'] = sentence.find(pos[0]) + len(pos[0]) - 1
                if content_info_one:
                    sent["content_info"].append(content_info_one)
            ent_list.append(sent)
        res["{}".format(i)] = ent_list
    return res


class ExtractImpl(BaseClass):
    def __init__(self, service_config):
        self.service = service_config.get("service")

    def extract_ner(self, data, lang="zh"):
        url = self.service + "/_nlu_ner"

        param = {
            "data": data,
            "lang": lang
        }
        response = requests.request("POST", url, json=param)
        print(response.text)
        if response.status_code != 200:
            return None, response.text

        resp_data = response.json()
        result = resp_data.get("result")
        if not result:
            return None, "No result"

        return parse_ner(result, lang), None

    def extract_event(self, data, lang="zh"):
        url = self.service + "/_nlu_integrate"

        param = {
            "data": data,
            "tasks": ["_nlu_event", "_nlu_sentences"],
            "lang": lang
        }

        resp = requests.post(url, json=param)
        print(resp.text)
        if resp.status_code != 200:
            return None, resp.text

        resp_data = resp.json()
        result = resp_data.get("result")
        if not result:
            return None, "No result"

        return parse_event(result), None
