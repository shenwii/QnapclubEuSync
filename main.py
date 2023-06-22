"""
#!/usr/bin/python3
# -*- coding: UTF-8 -*-
"""

import json
import sys
import time
import schedule
from check_args import check_args
from sync_job import sync_job

if __name__ == "__main__":
    # 读取配置文件
    with open("config.json", "r", encoding="utf-8") as config:
        config = json.load(config)
        if not check_args(config):
            sys.exit(1)
    sync_scheduler = schedule.Scheduler()
    # 读取配置中的时间生成任务
    if isinstance(type(config["sync_time"]), list):
        sync_times = config["sync_time"]
    else:
        sync_times = [config["sync_time"]]
    for sync_time in sync_times:
        sync_scheduler.every().day.at(sync_time).do(sync_job,
                                                    sync_db=config["data_base"],
                                                    sync_url=config["url"])

    while True:
        # 运行所有可以运行的任务
        sync_scheduler.run_pending()
        time.sleep(60)
