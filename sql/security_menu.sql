-- ----------------------------
-- 安防系统菜单配置
-- ----------------------------

-- 安防系统主菜单
INSERT INTO sys_menu VALUES(2000, '安防系统', 0, 5, 'security', null, '', 1, 0, 'M', '0', '0', '', 'security', 'admin', sysdate(), '', null, '安防系统目录');

-- 设备管理菜单
INSERT INTO sys_menu VALUES(2001, '设备管理', 2000, 1, 'device', 'security/device/index', '', 1, 0, 'C', '0', '0', 'security:device:list', 'video-camera', 'admin', sysdate(), '', null, '设备管理菜单');
INSERT INTO sys_menu VALUES(2101, '设备查询', 2001, 1, '', '', '', 1, 0, 'F', '0', '0', 'security:device:query', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2102, '设备新增', 2001, 2, '', '', '', 1, 0, 'F', '0', '0', 'security:device:add', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2103, '设备修改', 2001, 3, '', '', '', 1, 0, 'F', '0', '0', 'security:device:edit', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2104, '设备删除', 2001, 4, '', '', '', 1, 0, 'F', '0', '0', 'security:device:remove', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2105, '区域标注', 2001, 5, '', '', '', 1, 0, 'F', '0', '0', 'security:device:annotation', '#', 'admin', sysdate(), '', null, '设备区域标注功能');

-- 预警中心菜单
INSERT INTO sys_menu VALUES(2002, '预警中心', 2000, 2, 'warning', 'security/warning/index', '', 1, 0, 'C', '0', '0', 'security:warning:list', 'warning', 'admin', sysdate(), '', null, '预警中心菜单');
INSERT INTO sys_menu VALUES(2201, '预警查询', 2002, 1, '', '', '', 1, 0, 'F', '0', '0', 'security:warning:query', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2202, '预警处置', 2002, 2, '', '', '', 1, 0, 'F', '0', '0', 'security:warning:handle', '#', 'admin', sysdate(), '', null, '');

-- 处置记录菜单
INSERT INTO sys_menu VALUES(2003, '处置记录', 2000, 3, 'handling', 'security/handling/index', '', 1, 0, 'C', '0', '0', 'security:handling:list', 'edit', 'admin', sysdate(), '', null, '处置记录菜单');
INSERT INTO sys_menu VALUES(2301, '处置查询', 2003, 1, '', '', '', 1, 0, 'F', '0', '0', 'security:handling:query', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2302, '处置新增', 2003, 2, '', '', '', 1, 0, 'F', '0', '0', 'security:handling:add', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2303, '处置修改', 2003, 3, '', '', '', 1, 0, 'F', '0', '0', 'security:handling:edit', '#', 'admin', sysdate(), '', null, '');

-- 居民管理菜单
INSERT INTO sys_menu VALUES(2004, '居民管理', 2000, 4, 'resident', 'security/resident/index', '', 1, 0, 'C', '0', '0', 'security:resident:list', 'user', 'admin', sysdate(), '', null, '居民管理菜单');
INSERT INTO sys_menu VALUES(2401, '居民查询', 2004, 1, '', '', '', 1, 0, 'F', '0', '0', 'security:resident:query', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2402, '居民新增', 2004, 2, '', '', '', 1, 0, 'F', '0', '0', 'security:resident:add', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2403, '居民修改', 2004, 3, '', '', '', 1, 0, 'F', '0', '0', 'security:resident:edit', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2404, '居民删除', 2004, 4, '', '', '', 1, 0, 'F', '0', '0', 'security:resident:remove', '#', 'admin', sysdate(), '', null, '');

-- 设备监控菜单
INSERT INTO sys_menu VALUES(2005, '设备监控', 2000, 5, 'monitor', 'security/monitor/index', '', 1, 0, 'C', '0', '0', 'security:monitor:view', 'monitor', 'admin', sysdate(), '', null, '设备监控菜单');

-- 视频回放菜单
INSERT INTO sys_menu VALUES(2006, '视频回放', 2000, 6, 'video', 'security/video/index', '', 1, 0, 'C', '0', '0', 'security:video:list', 'video', 'admin', sysdate(), '', null, '视频回放菜单');
INSERT INTO sys_menu VALUES(2601, '视频查询', 2006, 1, '', '', '', 1, 0, 'F', '0', '0', 'security:video:query', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2602, '视频删除', 2006, 2, '', '', '', 1, 0, 'F', '0', '0', 'security:video:remove', '#', 'admin', sysdate(), '', null, '');

-- 数据统计菜单
INSERT INTO sys_menu VALUES(2007, '数据统计', 2000, 7, 'statistics', 'security/statistics/index', '', 1, 0, 'C', '0', '0', 'security:statistics:view', 'chart', 'admin', sysdate(), '', null, '数据统计菜单');

-- 人脸特征管理菜单（在居民管理下）
INSERT INTO sys_menu VALUES(2008, '人脸特征', 2004, 1, 'face', 'security/face/index', '', 1, 0, 'C', '0', '0', 'security:face:list', 'camera', 'admin', sysdate(), '', null, '人脸特征菜单');
INSERT INTO sys_menu VALUES(2801, '特征查询', 2008, 1, '', '', '', 1, 0, 'F', '0', '0', 'security:face:query', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2802, '特征新增', 2008, 2, '', '', '', 1, 0, 'F', '0', '0', 'security:face:add', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(2803, '特征删除', 2008, 3, '', '', '', 1, 0, 'F', '0', '0', 'security:face:remove', '#', 'admin', sysdate(), '', null, '');

-- Android用户管理菜单
INSERT INTO sys_menu VALUES(2009, 'Android用户', 2000, 8, 'android', 'security/android/index', '', 1, 0, 'C', '0', '0', 'security:android:list', 'mobile', 'admin', sysdate(), '', null, 'Android用户菜单');
INSERT INTO sys_menu VALUES(2901, '用户查询', 2009, 1, '', '', '', 1, 0, 'F', '0', '0', 'security:android:query', '#', 'admin', sysdate(), '', null, '');



