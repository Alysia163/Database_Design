# db_config.py
import pymysql

# 数据库连接配置
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "AbcD@314159",
    "database": "student_score_db",
    "port": 3306,
    "charset": "utf8mb4"
}


def get_db_connection():
    try:
        # 尝试连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        print("=" * 50)
        print("数据库连接成功！")
        print("=" * 50)
        return conn

    except pymysql.MySQLError as e:
        # 连接失败提示
        print("=" * 50)
        print("数据库连接失败！")
        print(f"错误信息：{e}")
        print("=" * 50)
        return None