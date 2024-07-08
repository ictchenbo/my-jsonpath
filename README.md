# my-jsonpath
本项目基于JSON数据的数据转换及服务集成

客户首先通过UStore或MongoDB进行服务的添加、管理

然后本服务读取指定的配置，根据指定参数进行服务请求，将结果以指定格式返回。

这个需求中最难的地方就是从不同服务的响应数据中提取需要的数据。本系统采用扩展的jsonpath进行实现。

## 核心数据结构

主要包括服务、请求体

1. Service 服务，相当于定义了请求的模板
```json
{
  "_id": "service_id",
  "name": "service name",
  "desc": "service desc",
  "url": "http://10.208.63.15/store/v3.0/gox_config/services",
  "method": "get",
  "params": {
    "header": {},
    "path": {},
    "query": {},
    "body": {}
  },
  "param_setting": {
    "content-type": "application/json",
    "query_serialization": "normal"
  },
  "proxy_setting": {
    "timeout": 60000
  }, 
  "result_parser": "jsonpath定义的结果解析器"
}

```
注意，其中result_parser是对请求结果的解析定义

2. Request 请求，每次具体的请求信息
```json
{
  "method": "get",
  "params": {
    "header": {},
    "path": {},
    "query": {},
    "body": {}
  },
  "param_setting": {
    "content-type": "application/json",
    "query_serialization": "normal"
  },
  "proxy_setting": {
    "timeout": 60000
  }, 
  "result_parser": "jsonpath定义的结果解析器"
}
```
最终使用的请求参数是Service + Request，其中Request优先级更高

这里需要设计一个关键处理函数，实现两个对象的合并。

3. 扩展的jsonpath定义
典型的jsonpath是一个表达式，每个表达式从`$`开始

扩展的jsonpath是一个JSON Val，定义如下：
- Val包括简单值、数组或对象，返回对应的简单值、数组值或对象值
- 数组支持嵌套，其中每个元素也是一个Val
- 对象支持嵌套，其中entry的key固定为String类型，value是一个Val
- 简单值如果是String类型，且以`$`开头，则表示其是一个jsonpath；其他情况则返回本身
- Val如果是对象，支持特殊的value，例如`$root`、`$val`、`$fun` 

## 接口设计
POST /services/<service_id> -d '#Request'

## 处理流程

1. 根据service_id 获取相应的Service对象
2. 将当前Request对象与Service对象合并，形成一个新的请求说明对象
3. 基于新的请求说明对象的相关字段发起http请求，利用requests已有方法，获得res对象
4. 判断res状态码，成功的情况下获取返回的JSON数据
5. 利用result_parser进行结果JSON的解析，获取返回的数据
6. 按照统一格式返回{data}数据 


## JsonPath语法参考
官方文档：[https://jsonpath.com/](https://jsonpath.com/)

## 使用方式
```shell
pip install -r requirements.txt

python rest_app.py

```
