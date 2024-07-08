# -*- coding: utf-8 -*-
"""
@File : test_case.py

@Author : chenbo(chenbo@golaxy.cn)
@Time : 2021/8/25 01:02
"""
import json
import os

from json_extract import parse_rule, check_rule, process_node


def t(s: str):
    print(list(parse_rule(s)))
    print(s, check_rule(s))


def m(test_data, s):
    print(process_node(test_data, s))


def test_simple_rules(data_id):
    data = json.load(open(data_id+".json"))
    with open(data_id+".test") as fin:
        for line in fin:
            rule = line.strip()
            if rule and not rule.startswith("#"):
                print(rule, process_node(data, rule))


def test_object_rules(data_id):
    data = json.load(open(data_id + ".json"))
    base_dir = os.path.join('object_rules', data_id)
    files = os.listdir(base_dir)
    for f in files:
        with open(os.path.join(base_dir, f)) as fin:
            rule = json.load(fin)
            print(f, process_node(data, rule))


if __name__ == "__main__":
    # test_simple_rules("json1")

    test_simple_rules("relation1")

    test_object_rules('relation1')
