# -*- coding: utf-8 -*-

from owl_admin.app import create_app
from owl_admin.ext import db
from owl_system.domain.po import SysMenuPo

# 创建应用对象
app = create_app()

with app.app_context():
    # 检查是否已经存在好友管理和聊天模块的菜单
    existing_menus = db.session.query(SysMenuPo).all()
    friend_menu_exists = any(menu.menu_name == '好友管理' for menu in existing_menus)
    chat_menu_exists = any(menu.menu_name == '聊天' for menu in existing_menus)
    
    if not friend_menu_exists:
        # 添加好友管理菜单
        friend_menu = SysMenuPo(
            menu_name='好友管理',
            parent_id=0,
            order_num=5,
            path='friend',
            component='Layout',
            is_frame=0,
            visible=0,
            status=0,
            perms='',
            icon='friend',
            create_by='admin',
            update_by='admin'
        )
        db.session.add(friend_menu)
        db.session.flush()  # 获取menu_id
        
        # 添加好友管理的子菜单
        friend_sub_menus = [
            {
                'menu_name': '好友列表',
                'parent_id': friend_menu.menu_id,
                'order_num': 1,
                'path': 'index',
                'component': 'friend/index',
                'is_frame': 0,
                'visible': 0,
                'status': 0,
                'perms': 'friend:list',
                'icon': 'friend-list'
            }
        ]
        
        for sub_menu_data in friend_sub_menus:
            sub_menu = SysMenuPo(
                menu_name=sub_menu_data['menu_name'],
                parent_id=sub_menu_data['parent_id'],
                order_num=sub_menu_data['order_num'],
                path=sub_menu_data['path'],
                component=sub_menu_data['component'],
                is_frame=sub_menu_data['is_frame'],
                visible=sub_menu_data['visible'],
                status=sub_menu_data['status'],
                perms=sub_menu_data['perms'],
                icon=sub_menu_data['icon'],
                create_by='admin',
                update_by='admin'
            )
            db.session.add(sub_menu)
        
        print("好友管理菜单添加成功")
    else:
        print("好友管理菜单已存在")
    
    if not chat_menu_exists:
        # 添加聊天菜单
        chat_menu = SysMenuPo(
            menu_name='聊天',
            parent_id=0,
            order_num=6,
            path='chat',
            component='Layout',
            is_frame=0,
            visible=0,
            status=0,
            perms='',
            icon='chat',
            create_by='admin',
            update_by='admin'
        )
        db.session.add(chat_menu)
        db.session.flush()  # 获取menu_id
        
        # 添加聊天的子菜单
        chat_sub_menus = [
            {
                'menu_name': '聊天列表',
                'parent_id': chat_menu.menu_id,
                'order_num': 1,
                'path': 'index',
                'component': 'chat/index',
                'is_frame': 0,
                'visible': 0,
                'status': 0,
                'perms': 'chat:sessions',
                'icon': 'chat-list'
            }
        ]
        
        for sub_menu_data in chat_sub_menus:
            sub_menu = SysMenuPo(
                menu_name=sub_menu_data['menu_name'],
                parent_id=sub_menu_data['parent_id'],
                order_num=sub_menu_data['order_num'],
                path=sub_menu_data['path'],
                component=sub_menu_data['component'],
                is_frame=sub_menu_data['is_frame'],
                visible=sub_menu_data['visible'],
                status=sub_menu_data['status'],
                perms=sub_menu_data['perms'],
                icon=sub_menu_data['icon'],
                create_by='admin',
                update_by='admin'
            )
            db.session.add(sub_menu)
        
        print("聊天菜单添加成功")
    else:
        print("聊天菜单已存在")
    
    # 提交事务
    db.session.commit()
    print("菜单添加完成")
