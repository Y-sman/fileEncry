# -*- coding: utf-8 -*-

from owl_admin.app import create_app
from owl_admin.ext import db
from owl_system.domain.po import SysMenuPo

# 创建应用对象
app = create_app()

with app.app_context():
    # 检查是否存在好友管理和聊天模块的菜单
    menus = db.session.query(SysMenuPo).filter(
        SysMenuPo.menu_name.in_(['好友管理', '聊天'])
    ).all()
    
    print("菜单信息:")
    for menu in menus:
        print(f"ID: {menu.menu_id}, 名称: {menu.menu_name}, 权限: {menu.perms}")
    
    # 检查子菜单
    parent_ids = [menu.menu_id for menu in menus]
    if parent_ids:
        child_menus = db.session.query(SysMenuPo).filter(
            SysMenuPo.parent_id.in_(parent_ids)
        ).all()
        
        print("\n子菜单信息:")
        for child in child_menus:
            print(f"ID: {child.menu_id}, 名称: {child.menu_name}, 权限: {child.perms}, 父菜单ID: {child.parent_id}")
    else:
        print("\n没有找到好友管理和聊天模块的菜单")
