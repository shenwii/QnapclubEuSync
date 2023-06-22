"""
同步QnapclubEu
"""

import json
import requests
from pymongo import MongoClient
import xmltodict


def sync_job(sync_db="", sync_url=""):
    """
    获取URL内容并同步至数据库
    """

    # 获取URL内容
    response = requests.get(sync_url, timeout=30)
    xml_content = response.content

    # 将XML转换为JSON
    xml_dict = xmltodict.parse(xml_content)
    json_data = json.loads(json.dumps(xml_dict))

    # 建立与MongoDB的连接和选择数据库
    with MongoClient(sync_db) as client:
        sync_db = client["qnap"]
        collection = sync_db["officialxml"]
        # 增量存储到MongoDB
        for item in json_data["plugins"]["item"]:
            # 假设数据的唯一标识符是"id"
            document = collection.find_one({"name": item["name"]})
            if document:
                # 如果文档已经存在，则更新
                collection.update_one({"name": item["name"]}, {"$set": item})
            else:
                # 如果文档不存在，则插入新文档
                collection.insert_one(item)
