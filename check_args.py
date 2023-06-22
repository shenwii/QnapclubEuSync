"""
检测配置文件是否完整
"""

import sys


def check_args(config=None):
    """
    检测配置文件是否完整
    """
    if config is None:
        config = []
    parms = ("url", "data_base", "sync_time")
    for parm in parms:
        if parm not in config:
            print(f"{parm} key is not exists.", file=sys.stderr)
            return False
    return True
