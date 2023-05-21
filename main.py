import xmltodict
import json
import requests
from pymongo import MongoClient
from datetime import datetime

with open("config.json", "r") as config:
  config_data = json.load(config)

#获取URL内容
response = requests.get(config_data["url"])
xml_content = response.content

#将XML转换为JSON
xml_dict = xmltodict.parse(xml_content)
json_data = json.loads(json.dumps(xml_dict))
#print(json_data)

now = datetime.now()
time_str = now.strftime("%Y%m%d")

#建立与MongoDB的连接和选择数据库
with MongoClient(config_data["DataBase"]) as client:
  db = client["qnap"]
  collection = db["officialxml" + time_str]
  #增量存储到MongoDB
  for item in json_data["plugins"]["item"]:
    #假设数据的唯一标识符是"id"
    document = collection.find_one({"name": item["name"]})
    if document:
      #如果文档已经存在，则更新
      collection.update_one({"name": item["name"]}, {"$set": item})
    else:
      #如果文档不存在，则插入新文档
      collection.insert_one(item)
