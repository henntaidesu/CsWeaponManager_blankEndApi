import sys
import sqlite3
from src.log import Log, err2
from src.read_conf import read_conf


class Date_base:

    def __init__(self):
        read_db_conf = read_conf()
        self.db, self.database_name = read_db_conf.database()
        self.print_log = Log()

    def get_database_name(self):
        return self.database_name
    
    def _close_connection(self):
        """关闭 SQLite 数据库连接"""
        if hasattr(self, 'db') and self.db:
            self.db.close()

    def insert(self, sql):
        try:
            cursor = self.db.cursor()
            sql = sql.replace("'None'", "NULL")
            cursor.execute(sql)
            self.db.commit()
            self._close_connection()
            return True
        except Exception as e:
            error_str = str(e).upper()
            if "PRIMARY" in error_str or "UNIQUE" in error_str:
                self.print_log.write_log(f"重复数据 {sql}", 'warning')
                return '重复数据'
            elif "timed out" in str(e).lower():
                self.print_log.write_log("连接数据库超时", 'error')
                return 'timed out'
                sys.exit()
            else:
                err2(e)
                self.print_log.write_log(f"错误 {sql}", 'warning')
                return False

    def update(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            err2(e)
            if "timed out" in str(e).lower():
                self.print_log.write_log("连接数据库超时", 'error')
            else:
                self.print_log.write_log(f'{sql}', 'error')
            return False
        finally:
            self._close_connection()

    def select(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return True, result
        except Exception as e:
            err2(e)
            if "timed out" in str(e).lower():
                self.print_log.write_log("连接数据库超时", 'error')
            else:
                self.print_log.write_log(f'{sql}', 'error')
            return False, None
        finally:
            self._close_connection()

    def delete(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            self.db.commit()  # 添加提交操作
            return result
        except Exception as e:
            err2(e)
            if "timed out" in str(e).lower():
                self.print_log.write_log(f"连接数据库超时", 'error')
            self.print_log.write_log(sql, 'error')
        finally:
            self._close_connection()

    def system_sql(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            self.db.commit()  # 修正：应该是 db.commit() 而不是 cursor.commit()
            cursor.close()
        except Exception as e:
            err2(e)
            if "timed out" in str(e).lower():
                self.print_log.write_log(f"连接数据库超时", 'error')
            self.print_log.write_log(sql, 'error')
        finally:
            self._close_connection()