# -*- coding: utf-8 -*-

from owl_admin.app import create_app
from owl_admin.ext import db
from owl_system.domain.po import SysMenuPo

# 创建应用对象
app = create_app()

with app.app_context():
    # 更新好友列表菜单的权限
    friend_list_menu = db.session.query(SysMenuPo).filter(
        SysMenuPo.menu_name == '好友列表'
    ).first()
    
    if friend_list_menu:
        # 设置完整的好友模块权限
        friend_list_menu.perms = 'friend:list,friend:search,friend:add,friend:edit,friend:remove,friend:query'
        db.session.commit()
        print("好友列表菜单权限更新成功")
    else:
        print("未找到好友列表菜单")
    
    # 更新聊天列表菜单的权限
    chat_list_menu = db.session.query(SysMenuPo).filter(
        SysMenuPo.menu_name == '聊天列表'
    ).first()
    
    if chat_list_menu:
        # 设置完整的聊天模块权限
        chat_list_menu.perms = 'chat:sessions,chat:history,chat:read'
        db.session.commit()
        print("聊天列表菜单权限更新成功")
    else:
        print("未找到聊天列表菜单")
    
    # 验证更新结果
    print("\n更新后的菜单权限:")
    menus = db.session.query(SysMenuPo).filter(
        SysMenuPo.menu_name.in_(['好友列表', '聊天列表'])
    ).all()
    
    for menu in menus:
        print(f"菜单名称: {menu.menu_name}, 权限: {menu.perms}")
