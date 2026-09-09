-- ============================================================
-- 智能运维 Agent 平台 · 数据库初始化脚本
-- 兼容版本：MySQL 5.7.26
-- 字符集：utf8mb4 / utf8mb4_unicode_ci
-- 引擎：InnoDB
-- 说明：
--   1. 使用 CREATE TABLE IF NOT EXISTS（5.7 支持，可重复执行）
--   2. JSON 类型在 MySQL 5.7.8+ 原生支持
--   3. 不使用 ADD COLUMN IF NOT EXISTS（5.7 不支持）
--   4. 所有字符串字面量统一使用单引号
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `agent_ops`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `agent_ops`;

-- ------------------------------------------------------------
-- 1. 用户表
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id`         BIGINT       NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username`   VARCHAR(64)  NOT NULL COMMENT '用户名',
  `password`   VARCHAR(128) NOT NULL COMMENT 'bcrypt 哈希密码',
  `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ------------------------------------------------------------
-- 2. 会话表
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `sessions` (
  `id`         CHAR(36)     NOT NULL COMMENT '会话ID（UUID v4）',
  `user_id`    BIGINT       NOT NULL COMMENT '所属用户ID',
  `title`      VARCHAR(128) NOT NULL DEFAULT '新对话' COMMENT '会话标题',
  `is_deleted` TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '软删除标记：0=正常 1=已删除',
  `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_updated` (`user_id`, `updated_at`),
  CONSTRAINT `fk_session_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会话表';

-- ------------------------------------------------------------
-- 3. 消息表
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `messages` (
  `id`          BIGINT      NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `session_id`  CHAR(36)    NOT NULL COMMENT '所属会话ID',
  `role`        ENUM('human','ai','tool','system') NOT NULL COMMENT '消息角色',
  `content`     TEXT        NOT NULL COMMENT '消息内容',
  `tool_calls`  JSON        NULL COMMENT '模型工具调用决策（仅 ai 消息可能有）',
  `created_at`  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_session_time` (`session_id`, `created_at`),
  CONSTRAINT `fk_msg_session` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';

-- ------------------------------------------------------------
-- 4. 工具调用日志表
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `tool_call_logs` (
  `id`          BIGINT      NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `session_id`  CHAR(36)    NOT NULL COMMENT '所属会话ID',
  `tool_name`   VARCHAR(64) NOT NULL COMMENT '工具名称',
  `args`        JSON        NOT NULL COMMENT '工具参数',
  `result`      TEXT        NOT NULL COMMENT '工具返回结果',
  `latency_ms`  INT         NOT NULL COMMENT '执行耗时（毫秒）',
  `created_at`  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_session` (`session_id`, `created_at`),
  CONSTRAINT `fk_log_session` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='工具调用日志表';

-- ------------------------------------------------------------
-- 验证：列出已创建的表
-- ------------------------------------------------------------
SHOW TABLES;
