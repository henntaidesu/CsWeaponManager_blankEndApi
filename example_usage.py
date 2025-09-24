#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新数据库管理器使用示例
演示如何使用对象化的数据库操作
"""

import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.db_manager import (
    ConfigModel, 
    BuyModel, 
    YyypBuyModel,
    get_db_manager
)


def example_config_operations():
    """配置表操作示例"""
    print("\n=== 配置表操作示例 ===")
    
    # 设置配置值
    success = ConfigModel.set_value("system", "version", "2.0.0", "系统版本")
    print(f"设置配置: {'成功' if success else '失败'}")
    
    # 获取配置值
    version = ConfigModel.get_value("system", "version", "1.0.0")
    print(f"获取配置值: {version}")
    
    # 查找所有配置
    configs = ConfigModel.find_all()
    print(f"配置总数: {len(configs)}")


def example_buy_operations():
    """购买记录操作示例"""
    print("\n=== 购买记录操作示例 ===")
    
    # 创建新的购买记录
    buy_record = BuyModel(
        ID="test_buy_001",
        weapon_name="AK-47",
        weapon_type="步枪",
        item_name="红线",
        weapon_float=0.15,
        float_range="略磨损",
        price=150.0,
        seller_name="测试卖家",
        status="已完成",
        **{"from": "test"}  # from 是关键字，需要特殊处理
    )
    
    # 保存到数据库
    success = buy_record.save()
    print(f"创建购买记录: {'成功' if success else '失败'}")
    
    if success:
        # 查找刚创建的记录
        found_record = BuyModel.find_by_id(ID="test_buy_001", **{"from": "test"})
        if found_record:
            print(f"找到记录: {found_record.weapon_name} - {found_record.price}元")
            
            # 修改记录
            found_record.price = 160.0
            found_record.status = "已发货"
            update_success = found_record.save()
            print(f"更新记录: {'成功' if update_success else '失败'}")
        
        # 统计信息
        total_count = BuyModel.count()
        print(f"购买记录总数: {total_count}")
        
        stats = BuyModel.get_statistics_by_status()
        print(f"按状态统计: {stats}")
        
        # 清理测试数据
        if found_record:
            found_record.delete()
            print("测试数据已清理")


def example_yyyp_operations():
    """YYYP表操作示例"""
    print("\n=== YYYP购买记录操作示例 ===")
    
    # 查找最近的YYYP购买记录
    recent_orders = YyypBuyModel.find_all("1=1 ORDER BY order_time DESC", (), limit=5)
    print(f"最近5条YYYP购买记录: {len(recent_orders)}")
    
    for order in recent_orders:
        print(f"  - {order.weapon_name}: {order.price}元 ({order.status})")


def example_database_info():
    """数据库信息示例"""
    print("\n=== 数据库信息 ===")
    
    db_manager = get_db_manager()
    
    # 获取统计信息
    stats = db_manager.get_statistics()
    print(f"总记录数: {stats['total_records']}")
    print("各表记录数:")
    for table_name, count in stats['tables'].items():
        print(f"  - {table_name}: {count}")
    
    # 获取数据库详细信息
    db_info = db_manager.get_database_info()
    print(f"\n数据库路径: {db_info['db_path']}")
    print(f"表数量: {len(db_info['tables'])}")


def main():
    """主函数"""
    print("🚀 新数据库管理器使用示例")
    print("=" * 50)
    
    try:
        # 配置操作示例
        example_config_operations()
        
        # 购买记录操作示例
        example_buy_operations()
        
        # YYYP操作示例
        example_yyyp_operations()
        
        # 数据库信息示例
        example_database_info()
        
    except Exception as e:
        print(f"示例运行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 示例运行完成！")


if __name__ == "__main__":
    main()
