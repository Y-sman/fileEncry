-- 加密文件表添加 file_hash 字段（用于文件完整性校验）
-- 哈希算法：SHA256，存储格式：十六进制字符串
ALTER TABLE enc_file ADD COLUMN file_hash varchar(64) DEFAULT NULL COMMENT '原始文件SHA256哈希(十六进制)' AFTER iv;
