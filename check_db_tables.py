# -*- coding: utf-8 -*-
from sqlalchemy import inspect
from owl_admin.app import create_app

# 创建应用实例
app = create_app()

# 在应用上下文中检查数据库表
with app.app_context():
    from owl_admin.ext import db
    
    # 创建 inspector 对象
    inspector = inspect(db.engine)
    
    # 检查 chat_message 表
    print('Checking chat_message table:')
    if 'chat_message' in inspector.get_table_names():
        print('Table exists')
        columns = inspector.get_columns('chat_message')
        print('Columns:')
        for column in columns:
            print(f'  {column["name"]}: {column["type"]}')
    else:
        print('Table does not exist')
    
    print('\nChecking chat_session table:')
    if 'chat_session' in inspector.get_table_names():
        print('Table exists')
        columns = inspector.get_columns('chat_session')
        print('Columns:')
        for column in columns:
            print(f'  {column["name"]}: {column["type"]}')
    else:
        print('Table does not exist')