"""
目标：根据规则对JSON格式数据进行提取，实现数据规则化抽取，可用于实现对API接口响应进行转换

支持的输入：JSON格式的简单值、对象、数组，对象和数组支持任意层次嵌套

规则设计：
1. 规则是一个JSON值，以下用Val表示
2. Val分为简单类型、数组类型和对象类型，形成返回数据的基本结构
3. 简单类型支持JSON的所有简单类型，包括null、整数、浮点数、字符串
4. 如果是字符串类型的简单类型，且以$开头，则认为是一个jsonpath规则，返回相应的解析结果；否则原样返回
5. 对于数组类型，则返回对应的数组；数组支持嵌套，其中每项元素也是一个Val
6. 对于对象类型，明确每个item的key为字符串、value为Val
7. 对象类型的key如果以$开头，表示特殊的规则，目前支持：
 - $root 用于指定当前访问的顶层节点，如果没有指定，则默认都是从原始数据的顶层开始计算
 - $val 用于将本规则返回值作为当前层级的值，等价于在上层直接用相应规则
 - $select 指定目标对象中需要返回的字段
 - $unselect 指定目标对象中不返回的字段
 - $keymap 提供一个字典 用于对当前规则子树对应的结果中的对象的key进行映射
 - $valuemap 提供一个字典 用于对当前规则子树对应的结果中的对象的value进行映射
8. 扩展jsonpath，目前支持：
 - $keys 目标对象的所有key
 - $values 目标对象的所有value
 - $* 任意一个元素或item


问题：
1. 如何实现根据业务逻辑进行获取？例如if-else的判断

样例1：
{
  code: 20000,
  msg: "abcde",
  data: {
    ner: {
      name: "aaa",
      type: "person",
      start: 5,
      end: 7,
      info: ['abc']
    },
    events: [
      {type, subtype, trigger}
    ],
    ent_name: [
      "a", "b", "c"
    ],
    ent_type: [
      "person", "loc", "org"
    ]
  }
}

基础语法示例
- $.code -> 20000
- $.data -> {ner, events }
- $.data.ner.name -> 'aaa'
- $.data.ner.info[0] -> 'abc'
- $.data.ner.$keys -> ['name', 'type', 'start', 'end', 'info']
- $.data.events.$length -> 1
- $.data.events

高级语法：
{
  "data": {
    "$root": "$.data.events",
    "$val": "$"
  }
}
->
{
  "data": [
      {type, subtype, trigger}
  ]
}


"""
import random


terminals = ['.', '[', ']']

OP_ERROR = -1
OP_DEFAULT = 0
OP_FIELD = 1
OP_INDEX = 2

MSG_EMPTY = "!Empty token"
MSG_INVALID = "!Invalid Token"
MSG_NOT_MATCH = "!Data Not Match"
MSG_NO_SUCH_KEY = "!No Such Key"
MSG_OUT_OF_RANGE = "!Index Out of Range"
MSG_NO_MORE_DATA = "!No More Data"


def parse_rule(s: str):
    if not s.startswith("$"):
        yield OP_ERROR, MSG_INVALID
        return
    i = 1
    s = s[i:]
    if not s:
        return
    cur_op = OP_DEFAULT
    cur_arg = ""
    quote_mode = False
    token_mode = False
    for ch in s:
        i += 1
        if quote_mode:  # 当前在引号中，直到引号结束
            if ch != '"':
                cur_arg += ch
            else:
                if cur_arg:
                    yield cur_op, cur_arg, i
                    cur_arg = ''
                else:
                    yield OP_ERROR, MSG_EMPTY
                quote_mode = False
                token_mode = False
            continue
        else:
            if ch == '"':  # 遇到引号，进入引号模式
                cur_arg = ''
                quote_mode = True
                continue
        if ch in terminals:
            # return and reset
            if cur_arg:
                yield cur_op, cur_arg, i
                cur_arg = ''
                token_mode = False
            elif ch == ']':
                yield OP_ERROR, MSG_EMPTY
        if ch == '.':
            if token_mode:  # 已经进入token
                yield OP_ERROR, MSG_INVALID
                continue
            cur_op = OP_FIELD
            token_mode = True
            continue
        if ch == '[':
            if token_mode:  # 已经进入token
                yield OP_ERROR, MSG_INVALID
                continue
            cur_op = OP_INDEX
            token_mode = True
            continue
        # if ch == ']':
        #     if not cur_arg:
        #         yield OP_ERROR, MSG_EMPTY
        if ch not in terminals:
            if not token_mode:  # 未进入token
                yield OP_ERROR, MSG_INVALID
            cur_arg += ch

    if quote_mode:
        yield OP_ERROR, "!Dangling Quote"
        return

    if token_mode:
        if cur_arg:
            yield cur_op, cur_arg, i
        else:
            yield OP_ERROR, MSG_EMPTY


def check_rule(s: str):
    for op, _ in parse_rule(s):
        if op == OP_ERROR:
            return False
    return True


def select_any(cur_node):
    """
    选择任意一项 支持list/str/字典
    :param cur_node:
    :return:
    """
    if isinstance(cur_node, list) or isinstance(cur_node, str):
        arg = random.randint(0, len(cur_node) - 1)
        return cur_node[arg]
    elif isinstance(cur_node, dict):
        keys = list(cur_node.keys())
        arg = keys[random.randint(0, len(keys) - 1)]
        return cur_node[arg]
    print(MSG_NOT_MATCH, cur_node, "$*")
    return None


def select_all(cur_node):
    """
    选择所有子节点
    :param cur_node:
    :return:
    """
    if isinstance(cur_node, dict):
        return list(cur_node.values())
    elif isinstance(cur_node, list) or isinstance(cur_node, str):
        return cur_node
    return []


def op_field(cur_node, arg: str):
    """
    处理 OP_FIELD类操作
    :param cur_node:
    :param arg:
    :return:
    """
    # 支持对list/str取长度
    if arg == "$len":
        if isinstance(cur_node, list) or isinstance(cur_node, str):
            cur_node = len(cur_node)
        else:
            print(MSG_NOT_MATCH, cur_node, arg)
            return None

    # 必须是对象
    if not isinstance(cur_node, dict):
        print(MSG_NOT_MATCH, cur_node, arg)
        return None

    # 以$开头的特殊算子
    if arg.startswith("$"):
        if arg == "$keys":
            if not isinstance(cur_node, dict):
                print(MSG_NOT_MATCH, cur_node, arg)
                return None
            cur_node = list(cur_node.keys())
        elif arg == "$values":
            if not isinstance(cur_node, dict):
                print(MSG_NOT_MATCH, cur_node, arg)
                return None
            cur_node = list(cur_node.values())

    if arg not in cur_node:
        print(MSG_NO_SUCH_KEY, arg)
        return None

    return cur_node[arg]


def process_leaf_node(data_root, rule_root: str):
    """
    处理叶子节点 即简单规则
    :param data_root:
    :param rule_root:
    :return:
    """
    if rule_root == "$":
        return data_root
    cur_node = data_root
    for args in parse_rule(rule_root):
        op, arg = args[0], args[1]
        # print(arg, cur_node)
        if op == OP_ERROR or not arg:
            print(MSG_INVALID)
            return None

        if cur_node is None:
            print(MSG_NO_MORE_DATA, arg)
            break

        if op != OP_ERROR:
            if arg == "$*":
                cur_node = select_any(cur_node)
                continue
            if arg == "$@":
                expands = select_all(cur_node)
                rule_right = "$" + rule_root[args[2]:]
                return [process_node(sub, rule_right) for sub in expands]

        if op == OP_FIELD:
            cur_node = op_field(cur_node, arg)
            if cur_node is None:
                return None
        elif op == OP_INDEX:
            # TODO 检查数据类型
            if not isinstance(cur_node, list):
                print(MSG_NOT_MATCH, cur_node, arg)
                return None
            _index = int(arg)
            if _index < 0 or _index >= len(cur_node):
                print(MSG_OUT_OF_RANGE, arg)
                return None
            cur_node = cur_node[int(arg)]
    return cur_node


def process_leaf_node_jsonpath(data_root, rule_root: str):
    """
    处理叶子节点 即简单规则
    :param data_root:
    :param rule_root:
    :return:
    """
    if rule_root == "$":
        return data_root
    cur_node = data_root

    if rule_root == "$*":
        return select_any(cur_node)
    # if rule_root == "$@":
    #     expands = select_all(cur_node)
    #     rule_right = "$" + rule_root[args[2]:]
    #     return [process_node(sub, rule_right) for sub in expands]

    from jsonpath2.path import Path
    p = Path.parse_str(rule_root)
    return [m.current_value for m in p.match(data_root)]


def process_node(data_root, rule_root):
    if isinstance(rule_root, str) and rule_root.startswith("$"):
        return process_leaf_node(data_root, rule_root)
    elif isinstance(rule_root, dict):
        # 执行函数
        if "$fun" in rule_root:
            print("Not Implemented!", rule_root)
            return None
        # 重定向
        if "$root" in rule_root:
            print(data_root, rule_root)
            data_root = process_node(data_root, rule_root.pop("$root"))
        # 指定或排出当前对象的某些字段
        selects = rule_root.get("$select")
        unselects = rule_root.get("$unselect")
        if selects or unselects:
            if not isinstance(data_root, dict):
                print("Invalid Data")
                return None
            if selects:
                rule_root.pop("$select")
                data_root = {k: v for k, v in data_root.items() if k in selects}
            if unselects:
                rule_root.pop("$unselect")
                data_root = {k: v for k, v in data_root.items() if k not in unselects}

        # 限定返回的规则
        # if "$val" in rule_root:
        #     return process_node(data_root, rule_root["$val"])
        # 联合子树结果
        if "$union" in rule_root:
            cur_rule = rule_root["$union"]
            if isinstance(data_root, list):
                return [process_node(sub, cur_rule) for sub in data_root]
            if isinstance(data_root, dict):
                return {k: process_node(v, cur_rule) for k, v in data_root.items()}
            print("Invalid Data")
            return None
        # if "$shift" in rule_root:
        #     pass
        # 以规则为模板，返回字典
        ret_obj = {}
        for k, v in rule_root.items():
            if not k.startswith("$"):
                ret_obj[k] = process_node(data_root, v)
        # 如果有其他key 则返回最新的节点
        return ret_obj or data_root

    elif isinstance(rule_root, list):
        ret_arr = []
        for rule_node in rule_root:
            ret_arr.append(process_node(data_root, rule_node))
        return ret_arr

    return rule_root
