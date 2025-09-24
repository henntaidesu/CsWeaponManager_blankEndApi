#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
在程序启动时运行，检查并初始化数据库表结构
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.db_manager import init_database, get_db_manager


def main():
    """主函数"""
    print("=" * 50)
    print("🚀 开始初始化数据库...")
    print("=" * 50)
    
    try:
        # 初始化数据库
        if init_database():
            print("\n✅ 数据库初始化成功！")
            
            # 显示统计信息
            db_manager = get_db_manager()
            stats = db_manager.get_statistics()
            
            print(f"\n📊 数据库统计信息:")
            print(f"   总记录数: {stats['total_records']}")
            print(f"   表详情:")
            for table_name, count in stats['tables'].items():
                print(f"     - {table_name}: {count} 条记录")
            
            # 检查表完整性
            print(f"\n🔍 检查表完整性...")
            if db_manager.check_table_integrity():
                print("✅ 所有表结构完整")
            else:
                print("⚠️ 发现表结构问题，正在修复...")
                if db_manager.repair_tables():
                    print("✅ 表结构修复完成")
                else:
                    print("❌ 表结构修复失败")
                    return False
            
        else:
            print("\n❌ 数据库初始化失败！")
            return False
            
    except Exception as e:
        print(f"\n❌ 初始化过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("🎉 数据库初始化完成！")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
