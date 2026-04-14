-- ----------------------------
-- 文件加解密系统菜单配置
-- ----------------------------

-- 文件加解密主菜单
INSERT INTO sys_menu VALUES(3000, '文件加解密', 0, 6, 'encry', null, '', 1, 0, 'M', '0', '0', '', 'lock', 'admin', sysdate(), '', null, '文件加解密目录');

-- 文件管理菜单
INSERT INTO sys_menu VALUES(3001, '文件管理', 3000, 1, 'file', 'encry/file/index', '', 1, 0, 'C', '0', '0', 'encry:file:list', 'documentation', 'admin', sysdate(), '', null, '文件管理菜单');
INSERT INTO sys_menu VALUES(3101, '文件查询', 3001, 1, '', '', '', 1, 0, 'F', '0', '0', 'encry:file:query', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(3102, '文件上传', 3001, 2, '', '', '', 1, 0, 'F', '0', '0', 'encry:file:upload', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(3103, '文件下载', 3001, 3, '', '', '', 1, 0, 'F', '0', '0', 'encry:file:download', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(3104, '文件删除', 3001, 4, '', '', '', 1, 0, 'F', '0', '0', 'encry:file:remove', '#', 'admin', sysdate(), '', null, '');

-- 密钥管理菜单
INSERT INTO sys_menu VALUES(3002, '密钥管理', 3000, 2, 'key', 'encry/key/index', '', 1, 0, 'C', '0', '0', 'encry:key:list', 'key', 'admin', sysdate(), '', null, '密钥管理菜单');
INSERT INTO sys_menu VALUES(3201, '密钥查询', 3002, 1, '', '', '', 1, 0, 'F', '0', '0', 'encry:key:query', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(3202, '密钥生成', 3002, 2, '', '', '', 1, 0, 'F', '0', '0', 'encry:key:add', '#', 'admin', sysdate(), '', null, '');
INSERT INTO sys_menu VALUES(3203, '密钥导出', 3002, 3, '', '', '', 1, 0, 'F', '0', '0', 'encry:key:export', '#', 'admin', sysdate(), '', null, '');
