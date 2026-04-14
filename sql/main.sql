-- ----------------------------
-- 文件加解密系统数据表设计
-- 依赖: sql/ry_20230706.sql (需先执行基础数据表)
-- ----------------------------

-- ----------------------------
-- 1、用户RSA密钥对表
-- 存储用户公钥及加密后的私钥，用于混合加密体系中的密钥管理
-- ----------------------------
drop table if exists enc_user_key;
create table enc_user_key (
  key_id              bigint(20)      not null auto_increment    comment '密钥ID',
  user_id             bigint(20)      not null                   comment '用户ID',
  public_key          text            not null                   comment 'RSA公钥(PEM格式)',
  private_key_enc     text            not null                   comment 'RSA私钥(加密存储)',
  key_size            int(4)          default 2048               comment '密钥长度(2048/4096)',
  status              char(1)         default '0'                comment '状态(0正常 1停用)',
  create_by           varchar(64)     default ''                 comment '创建者',
  create_time         datetime                                   comment '创建时间',
  update_by           varchar(64)     default ''                 comment '更新者',
  update_time         datetime                                   comment '更新时间',
  remark              varchar(500)    default null               comment '备注',
  primary key (key_id),
  unique key uk_user_id (user_id)
) engine=innodb auto_increment=1 comment = '用户RSA密钥对表';


-- ----------------------------
-- 2、加密文件表
-- 存储加密文件的元数据及加密相关信息
-- ----------------------------
drop table if exists enc_file;
create table enc_file (
  file_id             bigint(20)      not null auto_increment    comment '文件ID',
  user_id             bigint(20)      not null                   comment '所属用户ID',
  original_name       varchar(255)    not null                   comment '原始文件名',
  stored_name         varchar(64)     not null                   comment '存储文件名(UUID)',
  file_path           varchar(500)    not null                   comment '文件存储路径',
  file_size           bigint(20)      default 0                  comment '文件大小(字节)',
  encrypt_algo        varchar(20)     not null                   comment '对称加密算法(AES/DES)',
  sym_key_enc         text            not null                   comment '对称密钥(RSA加密后存储)',
  iv                  varchar(64)     default ''                 comment '加密向量/IV(Base64)',
  file_hash           varchar(64)     default null               comment '原始文件SHA256哈希(十六进制,用于完整性校验)',
  del_flag            char(1)         default '0'                comment '删除标志(0存在 2删除)',
  create_by           varchar(64)     default ''                 comment '创建者',
  create_time         datetime                                   comment '创建时间',
  update_by           varchar(64)     default ''                 comment '更新者',
  update_time         datetime                                   comment '更新时间',
  remark              varchar(500)    default null               comment '备注',
  primary key (file_id),
  key idx_user_id (user_id),
  key idx_create_time (create_time)
) engine=innodb auto_increment=1 comment = '加密文件表';


-- ----------------------------
-- 3、文件加解密系统菜单
-- ----------------------------
-- 一级菜单
insert into sys_menu values('3000', '文件加解密', '0', 6, 'encry', null, '', 1, 0, 'M', '0', '0', '', 'lock', 'admin', sysdate(), '', null, '文件加解密目录');

-- 文件管理菜单
insert into sys_menu values('3001', '文件管理', '3000', 1, 'file', 'encry/file/index', '', 1, 0, 'C', '0', '0', 'encry:file:list', 'documentation', 'admin', sysdate(), '', null, '文件管理菜单');
insert into sys_menu values('3101', '文件查询', '3001', 1, '', '', '', 1, 0, 'F', '0', '0', 'encry:file:query', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('3102', '文件上传', '3001', 2, '', '', '', 1, 0, 'F', '0', '0', 'encry:file:upload', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('3103', '文件下载', '3001', 3, '', '', '', 1, 0, 'F', '0', '0', 'encry:file:download', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('3104', '文件删除', '3001', 4, '', '', '', 1, 0, 'F', '0', '0', 'encry:file:remove', '#', 'admin', sysdate(), '', null, '');

-- 密钥管理菜单
insert into sys_menu values('3002', '密钥管理', '3000', 2, 'key', 'encry/key/index', '', 1, 0, 'C', '0', '0', 'encry:key:list', 'key', 'admin', sysdate(), '', null, '密钥管理菜单');
insert into sys_menu values('3201', '密钥查询', '3002', 1, '', '', '', 1, 0, 'F', '0', '0', 'encry:key:query', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('3202', '密钥生成', '3002', 2, '', '', '', 1, 0, 'F', '0', '0', 'encry:key:add', '#', 'admin', sysdate(), '', null, '');
insert into sys_menu values('3203', '密钥导出', '3002', 3, '', '', '', 1, 0, 'F', '0', '0', 'encry:key:export', '#', 'admin', sysdate(), '', null, '');

-- ----------------------------
-- 4、角色菜单关联(文件加解密模块)
-- 为admin(1)和common(2)角色分配文件加解密菜单权限
-- ----------------------------
insert into sys_role_menu values('1', '3000');
insert into sys_role_menu values('1', '3001');
insert into sys_role_menu values('1', '3101');
insert into sys_role_menu values('1', '3102');
insert into sys_role_menu values('1', '3103');
insert into sys_role_menu values('1', '3104');
insert into sys_role_menu values('1', '3002');
insert into sys_role_menu values('1', '3201');
insert into sys_role_menu values('1', '3202');
insert into sys_role_menu values('1', '3203');
insert into sys_role_menu values('2', '3000');
insert into sys_role_menu values('2', '3001');
insert into sys_role_menu values('2', '3101');
insert into sys_role_menu values('2', '3102');
insert into sys_role_menu values('2', '3103');
insert into sys_role_menu values('2', '3104');
insert into sys_role_menu values('2', '3002');
insert into sys_role_menu values('2', '3201');
insert into sys_role_menu values('2', '3202');
insert into sys_role_menu values('2', '3203');
