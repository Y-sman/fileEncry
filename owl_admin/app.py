# -*- coding: utf-8 -*-
# @Author  : balabala

import os,sys
from flask import Flask 

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)


def create_app() -> Flask:
    """
    创建flask应用
    
    Returns:
        Flask: flask应用
    """
    from owl_admin.ext import db,fredis,lm,cors,owl
    from owl_common.base.signal import app_completed

    app = Flask(__name__,static_folder=None)
        
    owl.init_app(app,PROJECT_ROOT)
    cors.init_app(app)
    fredis.init_app(app)
    db.init_app(app)
    lm.init_app(app)
    
    # 注册WebSocket处理器
    try:
        from owl_chat.socket_server import socketio as chat_socketio
        chat_socketio.init_app(app, cors_allowed_origins="*")
    except ImportError:
        pass  # 如果模块不存在，跳过WebSocket初始化
    
    app_completed.send(app)
    return app


if __name__ == "__main__":
    app = create_app()
    from owl_chat.socket_server import socketio as chat_socketio
    chat_socketio.run(
        app,
        host=app.config.get('SERVER_HOST', '0.0.0.0'),
        port=app.config.get('SERVER_PORT', 9000),
        debug=app.config.get('DEBUG', False),
        allow_unsafe_werkzeug=True  # 允许在开发环境中使用 Werkzeug 服务器
    )
    