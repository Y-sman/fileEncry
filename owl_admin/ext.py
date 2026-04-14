# -*- coding: utf-8 -*-
# @Author  : balabala

from werkzeug.local import LocalProxy
from flask import current_app

from flask_redis import FlaskRedis
from flask_login import LoginManager
from flask_cors import CORS
from flask_socketio import SocketIO
from redis import Redis

from owl_common.owl.extension import FlaskOwl
from owl_common.sqlalchemy.extension import SQLAlchemy
    

owl = FlaskOwl()
cors = CORS()

fredis = FlaskRedis()
redis_cache:Redis = LocalProxy(
    lambda: current_app.extensions["redis"]._redis_client
) 
lm = LoginManager()
db = SQLAlchemy()
socketio = SocketIO(
    cors_allowed_origins="*", 
    async_mode='threading',
    ping_timeout=60,  # ping 超时时间（秒）
    ping_interval=25,  # ping 间隔（秒），应该小于 ping_timeout
    max_http_buffer_size=1e6  # 最大 HTTP 缓冲区大小
)