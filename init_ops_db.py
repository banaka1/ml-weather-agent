"""
创建 NL2SQL 示例运维数据库（SQLite）
表：servers / metrics / alerts
运行一次即可生成 ops.db
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ops.db")

SCHEMA = """
DROP TABLE IF EXISTS metrics;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS servers;

CREATE TABLE servers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname VARCHAR(64) NOT NULL,
    ip VARCHAR(32) NOT NULL,
    os VARCHAR(32),
    status VARCHAR(16) DEFAULT 'running',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    cpu REAL,
    memory REAL,
    disk REAL,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id)
);

CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id INTEGER NOT NULL,
    level VARCHAR(16),
    message TEXT,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (server_id) REFERENCES servers(id)
);
"""

SAMPLE_SERVERS = [
    ("web-01", "10.0.0.11", "Ubuntu 22.04", "running"),
    ("web-02", "10.0.0.12", "Ubuntu 22.04", "running"),
    ("db-01", "10.0.0.21", "CentOS 7", "running"),
    ("db-02", "10.0.0.22", "CentOS 7", "stopped"),
    ("cache-01", "10.0.0.31", "Debian 11", "running"),
]

SAMPLE_METRICS = [
    (1, 45.2, 62.1, 38.5),
    (1, 78.9, 71.3, 39.0),
    (2, 32.1, 55.0, 42.1),
    (3, 91.5, 88.7, 76.2),
    (3, 95.3, 90.1, 77.0),
    (4, 0.0, 0.0, 0.0),
    (5, 28.4, 41.2, 55.8),
]

SAMPLE_ALERTS = [
    (3, "critical", "CPU 使用率超过 90%"),
    (3, "warning", "内存使用率超过 85%"),
    (4, "critical", "服务器宕机"),
    (1, "info", "磁盘使用率接近 40%"),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(SCHEMA)
    # 插入示例数据
    c.executemany(
        "INSERT INTO servers (hostname, ip, os, status) VALUES (?, ?, ?, ?)",
        SAMPLE_SERVERS,
    )
    c.executemany(
        "INSERT INTO metrics (server_id, cpu, memory, disk) VALUES (?, ?, ?, ?)",
        SAMPLE_METRICS,
    )
    c.executemany(
        "INSERT INTO alerts (server_id, level, message) VALUES (?, ?, ?)",
        SAMPLE_ALERTS,
    )
    conn.commit()
    conn.close()
    print(f"✅ 示例库已创建: {DB_PATH}")
    print("   表: servers(5), metrics(7), alerts(4)")


if __name__ == "__main__":
    init_db()
