# -*- coding: utf-8 -*-
from owl_admin.ext import db

print('Chat message table:', 'chat_message' in db.Model.metadata.tables)
print('Chat session table:', 'chat_session' in db.Model.metadata.tables)

if 'chat_message' in db.Model.metadata.tables:
    print('Chat message columns:', [c.name for c in db.Model.metadata.tables['chat_message'].columns])

if 'chat_session' in db.Model.metadata.tables:
    print('Chat session columns:', [c.name for c in db.Model.metadata.tables['chat_session'].columns])