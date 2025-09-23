import sys
import sqlite3
from src.log import Log, err2
from src.read_conf import read_conf


class Date_base:

    def __init__(self):
        self.read_db_conf = read_conf()
        self.database_name = self.read_db_conf.get_database_name()
        self.print_log = Log()
        self.db = None
    
    def _get_connection(self):
        """获取数据库连接"""
        if self.db is None:
            self.db, _ = self.read_db_conf.database()
        return self.db

    def get_database_name(self):
        return self.database_name
    
    def _close_connection(self):
        """关闭 SQLite 数据库连接"""
        if hasattr(self, 'db') and self.db:
            self.db.close()

    def insert(self, sql):
        db = None
        try:
            db, _ = self.read_db_conf.database()
            cursor = db.cursor()
            sql = sql.replace("'None'", "NULL")
            cursor.execute(sql)
            db.commit()
            cursor.close()
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
        finally:
            if db:
                db.close()

    def update(self, sql):
        db = None
        try:
            db, _ = self.read_db_conf.database()
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
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
            if db:
                db.close()

    def select(self, sql):
        db = None
        try:
            db, _ = self.read_db_conf.database()
            cursor = db.cursor()
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
            if db:
                db.close()

    def delete(self, sql):
        db = None
        try:
            db, _ = self.read_db_conf.database()
            cursor = db.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            db.commit()
            return result
        except Exception as e:
            err2(e)
            if "timed out" in str(e).lower():
                self.print_log.write_log(f"连接数据库超时", 'error')
            self.print_log.write_log(sql, 'error')
        finally:
            if db:
                db.close()

    def system_sql(self, sql):
        db = None
        try:
            db, _ = self.read_db_conf.database()
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
            cursor.close()
        except Exception as e:
            err2(e)
            if "timed out" in str(e).lower():
                self.print_log.write_log(f"连接数据库超时", 'error')
            self.print_log.write_log(sql, 'error')
        finally:
            if db:
                db.close()