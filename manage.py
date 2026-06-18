"""
数据库管理小工具（针对本项目的 sqlite: database.db）。

用法:
    # 1) 给已有数据库补上新增的列（role / audit_*），不会清空数据
    python manage.py migrate

    # 2) 把某个用户设为管理员（管理端）
    python manage.py set-admin <用户名>

    # 3) 把某个用户改回普通用户
    python manage.py set-user <用户名>

注意: 如果你不在意旧数据，也可以直接删除 database.db，
      启动 main.py 时会按最新的模型自动重新创建表。
"""
import sqlite3
import sys

DB_FILE = "database.db"

# 需要确保存在的新列： 表名 -> [(列名, 列定义), ...]
NEW_COLUMNS = {
    "user": [
        ("role", "TEXT DEFAULT 'user'"),
    ],
    "target": [
        ("audit_status", "TEXT DEFAULT 'pending'"),
        ("audit_reason", "TEXT"),
        ("audited_by", "INTEGER"),
        ("audited_at", "TIMESTAMP"),
    ],
}


def _existing_columns(conn, table):
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def migrate():
    conn = sqlite3.connect(DB_FILE)
    try:
        for table, columns in NEW_COLUMNS.items():
            existing = _existing_columns(conn, table)
            for name, definition in columns:
                if name in existing:
                    print(f"[skip] {table}.{name} 已存在")
                    continue
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
                print(f"[add ] {table}.{name}")
        conn.commit()
        print("迁移完成")
    finally:
        conn.close()


def set_role(name, role):
    conn = sqlite3.connect(DB_FILE)
    try:
        if "role" not in _existing_columns(conn, "user"):
            print("用户表还没有 role 列，请先执行: python manage.py migrate")
            return
        cur = conn.execute("UPDATE user SET role = ? WHERE name = ?", (role, name))
        conn.commit()
        if cur.rowcount == 0:
            print(f"未找到用户: {name}")
        else:
            print(f"已将用户 {name} 设为 {role}")
    finally:
        conn.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    if cmd == "migrate":
        migrate()
    elif cmd == "set-admin" and len(sys.argv) == 3:
        set_role(sys.argv[2], "admin")
    elif cmd == "set-user" and len(sys.argv) == 3:
        set_role(sys.argv[2], "user")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
