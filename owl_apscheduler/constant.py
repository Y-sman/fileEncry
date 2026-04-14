# -*- coding: utf-8 -*-
# @Author  : balabala

from enum import Enum

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"  # 标准日期时间格式


class ScheduleStatus(Enum):
    
    NORMAL = "0"
    
    PAUSED = "1"
    

class ScheduleConstant:
    
    MISFIRE_DEFAULT = "0"
    
    MISFIRE_IGNORE_MISFIRES = "1"
    
    MISFIRE_FIRE_AND_PROCEED = "2"
    
    MISFIRE_DO_NOTHING = "3"
    
    ALLOW_CONCURRENT = "0"
    
    FORBIDDEN_CONCURRENT = "1"
    
    JOB_WHITELIST_STR = { "owl_apscheduler" }
    
