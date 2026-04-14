# -*- coding: utf-8 -*-

from owl_admin.app import create_app
from owl_admin.ext import db
from owl_system.domain.po import SysMenuPo

# 创建应用对象
app = create_app()

with app.app_context():
    # 查询所有菜单名称
    menus = db.session.query(SysMenuPo).all()
    print("当前系统中的菜单：")
    for menu in menus:
        print(f"ID: {menu.menu_id}, 名称: {menu.menu_name}, 权限: {menu.perms}")

    # 检查是否存在好友管理和聊天模块的菜单
    friend_menu_exists = any(menu.menu_name == '好友管理' for menu in menus)
    chat_menu_exists = any(menu.menu_name == '聊天' for menu in menus)
    
    print(f"\n好友管理菜单存在: {friend_menu_exists}")
    print(f"聊天菜单存在: {chat_menu_exists}")
