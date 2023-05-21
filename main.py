#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import xmltodict
import json
import requests
from pymongo import MongoClient
from datetime import datetime
import schedule
import time
import sys


def check_args(config=[]):
  #检测配置文件是否完整
  parms = ("url", "data_base", "sync_time")
  for parm in parms:
    if parm not in config:
      print(f"{parm} key is not exists.", file=sys.stderr)
      return False
  return True


def sync_job(db="", url=""):
  #获取URL内容
  response = requests.get(url)
  xml_content = response.content

  #将XML转换为JSON
  xml_dict = xmltodict.parse(xml_content)
  json_data = json.loads(json.dumps(xml_dict))

  #获取当前日期
  now = datetime.now()
  time_str = now.strftime("%Y%m%d%H")

  #建立与MongoDB的连接和选择数据库
  with MongoClient(db) as client:
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


if __name__ == "__main__":
  #读取配置文件
  with open("config.json", "r", encoding="utf-8") as config:
    config = json.load(config)
    if not check_args(config):
      sys.exit(1)
  sync_scheduler = schedule.Scheduler()
  #读取配置中的时间生成任务
  if type(config["sync_time"]) == list:
    sync_times = config["sync_time"]
  else:
    sync_times = [config["sync_time"]]
  for sync_time in sync_times:
    sync_scheduler.every().day.at(sync_time).do(sync_job,
                                                db=config["data_base"],
                                                url=config["url"])

  while True:
    # 运行所有可以运行的任务
    sync_scheduler.run_pending()
    time.sleep(60)
