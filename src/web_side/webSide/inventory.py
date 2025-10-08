from flask import jsonify, request, Blueprint
from src.db_manager.steam.steam_inventory import SteamInventoryModel
from src.db_manager.database import DatabaseManager

webInventoryV1 = Blueprint('webInventoryV1', __name__)

@webInventoryV1.route('/steam_ids', methods=['GET'])
def get_steam_ids():
    """获取所有不同的Steam ID列表"""
    try:
        db = DatabaseManager()
        sql = """
        SELECT DISTINCT data_user, COUNT(*) as item_count
        FROM steam_inventory 
        WHERE data_user IS NOT NULL AND data_user != ''
        GROUP BY data_user
        ORDER BY item_count DESC
        """
        results = db.execute_query(sql)
        
        steam_ids = []
        for row in results:
            data_user, item_count = row
            steam_ids.append({
                'steam_id': data_user,
                'item_count': item_count
            })
        
        return jsonify({
            'success': True,
            'data': steam_ids
        }), 200
        
    except Exception as e:
        print(f"查询Steam ID列表失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500

@webInventoryV1.route('/inventory/<steam_id>', methods=['GET'])
def get_inventory(steam_id):
    """获取指定用户的库存列表"""
    try:
        # 获取查询参数
        search_text = request.args.get('search', '')
        weapon_type = request.args.get('weapon_type', '')
        float_range = request.args.get('float_range', '')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 构建查询条件
        where_conditions = ["data_user = ?"]
        params = [steam_id]
        
        if search_text:
            where_conditions.append("(item_name LIKE ? OR weapon_name LIKE ?)")
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern])
        
        if weapon_type:
            where_conditions.append("weapon_type = ?")
            params.append(weapon_type)
        
        if float_range:
            where_conditions.append("float_range = ?")
            params.append(float_range)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询数据，使用自定义排序：未知物品放在最后
        from src.db_manager.database import DatabaseManager
        db = DatabaseManager()
        
        sql = f"""
        SELECT assetid, instanceid, classid, item_name, weapon_name, float_range, 
               weapon_type, weapon_float, remark, data_user 
        FROM {SteamInventoryModel.get_table_name()}
        WHERE {where_clause}
        ORDER BY 
            CASE 
                WHEN weapon_type = '未知物品' THEN 1
                ELSE 0
            END,
            ROWID
        LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        results = db.execute_query(sql, tuple(params))
        
        # 将结果转换为模型对象
        records = []
        if results:
            for row in results:
                record = SteamInventoryModel()
                record.assetid = row[0]
                record.instanceid = row[1]
                record.classid = row[2]
                record.item_name = row[3]
                record.weapon_name = row[4]
                record.float_range = row[5]
                record.weapon_type = row[6]
                record.weapon_float = row[7]
                record.remark = row[8]
                record.data_user = row[9]
                records.append(record)
        
        # 转换为字典列表
        inventory_list = []
        for record in records:
            inventory_list.append({
                'assetid': record.assetid,
                'instanceid': record.instanceid,
                'classid': record.classid,
                'weapon_name': record.weapon_name,
                'item_name': record.item_name,
                'weapon_type': record.weapon_type,
                'weapon_float': record.weapon_float,
                'float_range': record.float_range,
                'remark': record.remark
            })
        
        # 获取总数
        total = SteamInventoryModel.count(where_clause, tuple(params))
        
        return jsonify({
            'success': True,
            'data': inventory_list,
            'total': total
        }), 200
        
    except Exception as e:
        print(f"查询库存失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webInventoryV1.route('/inventory/grouped/<steam_id>', methods=['GET'])
def get_grouped_inventory(steam_id):
    """获取按item_name分组的库存列表"""
    try:
        from src.db_manager.database import DatabaseManager
        
        db = DatabaseManager()
        
        # 查询分组数据，未知物品排在最后
        sql = """
        SELECT 
            item_name,
            weapon_name,
            weapon_type,
            float_range,
            COUNT(*) as count,
            GROUP_CONCAT(assetid) as assetids,
            GROUP_CONCAT(weapon_float) as weapon_floats,
            GROUP_CONCAT(remark, '|||') as remarks
        FROM steam_inventory 
        WHERE data_user = ?
        GROUP BY item_name, weapon_name, weapon_type, float_range
        ORDER BY 
            CASE 
                WHEN weapon_type = '未知物品' THEN 1
                ELSE 0
            END,
            item_name
        """
        
        results = db.execute_query(sql, (steam_id,))
        
        # 转换为字典列表
        grouped_list = []
        for row in results:
            item_name, weapon_name, weapon_type, float_range, count, assetids, weapon_floats, remarks = row
            
            # 分割字符串为列表
            assetid_list = assetids.split(',') if assetids else []
            float_list = weapon_floats.split(',') if weapon_floats else []
            remark_list = remarks.split('|||') if remarks else []
            
            grouped_list.append({
                'item_name': item_name,
                'weapon_name': weapon_name,
                'weapon_type': weapon_type,
                'float_range': float_range,
                'count': count,
                'assetids': assetid_list,
                'weapon_floats': float_list,
                'remarks': remark_list
            })
        
        return jsonify({
            'success': True,
            'data': grouped_list,
            'total': len(grouped_list)
        }), 200
        
    except Exception as e:
        print(f"查询分组库存失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webInventoryV1.route('/inventory/stats/<steam_id>', methods=['GET'])
def get_inventory_stats(steam_id):
    """获取库存统计信息"""
    try:
        from src.db_manager.database import DatabaseManager
        
        db = DatabaseManager()
        
        # 统计总数
        total_sql = "SELECT COUNT(*) FROM steam_inventory WHERE data_user = ?"
        total_result = db.execute_query(total_sql, (steam_id,))
        total_count = total_result[0][0] if total_result else 0
        
        # 按武器类型统计
        type_sql = """
        SELECT weapon_type, COUNT(*) as count 
        FROM steam_inventory 
        WHERE data_user = ? AND weapon_type IS NOT NULL AND weapon_type != ''
        GROUP BY weapon_type
        ORDER BY count DESC
        """
        type_results = db.execute_query(type_sql, (steam_id,))
        
        type_stats = []
        for row in type_results:
            weapon_type, count = row
            type_stats.append({
                'weapon_type': weapon_type,
                'count': count
            })
        
        # 按磨损等级统计
        wear_sql = """
        SELECT float_range, COUNT(*) as count 
        FROM steam_inventory 
        WHERE data_user = ? AND float_range IS NOT NULL AND float_range != ''
        GROUP BY float_range
        ORDER BY count DESC
        """
        wear_results = db.execute_query(wear_sql, (steam_id,))
        
        wear_stats = []
        for row in wear_results:
            float_range, count = row
            wear_stats.append({
                'float_range': float_range,
                'count': count
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_count': total_count,
                'by_type': type_stats,
                'by_wear': wear_stats
            }
        }), 200
        
    except Exception as e:
        print(f"查询统计信息失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500

