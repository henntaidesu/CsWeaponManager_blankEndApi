from flask import jsonify, request, Blueprint
from src.db_manager.database import DatabaseManager
import traceback

webStockComponentsV1 = Blueprint('webStockComponentsV1', __name__)

# 组件的classid常量
COMPONENT_CLASSID = '3604678661'


@webStockComponentsV1.route('/steam_ids', methods=['GET'])
def get_steam_ids():
    """从 steam_stockComponents 表获取所有不同的Steam ID列表"""
    try:
        db = DatabaseManager()
        
        # 查询所有不同的 data_user (Steam ID)，并统计每个ID的组件数量
        sql = """
        SELECT data_user, COUNT(*) as item_count
        FROM steam_stockComponents
        WHERE data_user IS NOT NULL AND data_user != ''
        GROUP BY data_user
        ORDER BY data_user
        """
        results = db.execute_query(sql)
        
        steam_ids = []
        for row in results:
            steam_ids.append({
                'steam_id': row[0],
                'item_count': row[1]
            })
        
        return jsonify({
            'success': True,
            'data': steam_ids
        }), 200
        
    except Exception as e:
        print(f"获取Steam ID列表失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/<steam_id>', methods=['GET'])
def get_components(steam_id):
    """获取指定用户的库存组件列表 - 从 steam_stockComponents 表读取"""
    try:
        # 获取查询参数
        search_text = request.args.get('search', '')
        weapon_type = request.args.get('weapon_type', '')  # 武器类型筛选
        weapon_level = request.args.get('weapon_level', '')  # 武器等级筛选
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        db = DatabaseManager()
        
        # 构建查询条件
        where_conditions = ["data_user = ?"]
        params = [steam_id]
        
        # 关键词搜索 - 搜索武器名称
        if search_text:
            where_conditions.append("weapon_name LIKE ?")
            params.append(f"%{search_text}%")
        
        # 武器类型筛选
        if weapon_type:
            where_conditions.append("weapon_type = ?")
            params.append(weapon_type)
        
        # 武器等级筛选
        if weapon_level:
            where_conditions.append("weapon_level = ?")
            params.append(weapon_level)
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询数据 - 查询所有字段
        sql = f"""
        SELECT 
            assetid, instanceid, classid, item_name, weapon_name, 
            float_range, weapon_type, weapon_float, weapon_level, data_user, 
            buy_price, yyyp_price, buff_price, order_time, steam_price
        FROM steam_stockComponents
        WHERE {where_clause}
        ORDER BY order_time DESC
        LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        results = db.execute_query(sql, tuple(params))
        
        # 转换为字典列表
        components = []
        if results:
            for row in results:
                # 安全的浮点数转换函数
                def safe_float(value, default=0.0):
                    if value is None or value == '':
                        return default
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return default
                
                component = {
                    # 基本信息
                    'component_id': row[0],  # assetid - 用于操作
                    'item_name': row[3],  # 物品名称
                    'weapon_name': row[4],  # 武器名称
                    'float_range': row[5],  # 磨损值范围
                    'weapon_type': row[6],  # 武器类型
                    'weapon_float': row[7],  # 武器磨损值/数量
                    'weapon_level': row[8],  # 武器等级
                    
                    # 价格信息
                    'buy_price': safe_float(row[10]),  # 购入价格
                    'yyyp_price': safe_float(row[11]),  # 悠悠价格
                    'buff_price': safe_float(row[12]),  # BUFF价格
                    'steam_price': safe_float(row[14]),  # Steam价格
                    
                    # 时间信息
                    'order_time': row[13],  # 入库时间
                    
                    # 兼容旧字段
                    'component_name': row[3],
                    'component_type': row[6],
                    'quality': row[8],
                    'quantity': row[7],  # weapon_float 作为数量
                    'unit_cost': safe_float(row[10]),
                    'total_cost': safe_float(row[10]),
                    'source': '库存',
                    'purchase_date': row[13],
                    'status': '库存中',
                    'status_desc': ''
                }
                components.append(component)
        
        # 获取总数
        count_params = params[:-2]  # 去掉limit和offset参数
        count_sql = f"SELECT COUNT(*) FROM steam_stockComponents WHERE {where_clause}"
        count_result = db.execute_query(count_sql, tuple(count_params))
        total = count_result[0][0] if count_result else 0
        
        return jsonify({
            'success': True,
            'data': components,
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200
        
    except Exception as e:
        print(f"查询库存组件失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/stats/<steam_id>', methods=['GET'])
def get_components_stats(steam_id):
    """获取库存组件统计信息 - 从 steam_stockComponents 表读取"""
    try:
        db = DatabaseManager()
        
        # 统计总数和各种价格总和
        stats_sql = f"""
        SELECT 
            COUNT(*) as total_count,
            SUM(CAST(buy_price AS REAL)) as total_buy_price,
            SUM(CAST(yyyp_price AS REAL)) as total_yyyp_price,
            SUM(CAST(buff_price AS REAL)) as total_buff_price,
            SUM(CAST(steam_price AS REAL)) as total_steam_price
        FROM steam_stockComponents
        WHERE data_user = ?
        """
        stats_result = db.execute_query(stats_sql, (steam_id,))
        
        total_count = 0
        total_cost = 0
        total_yyyp_price = 0
        total_buff_price = 0
        total_steam_price = 0
        
        if stats_result and stats_result[0][0] is not None:
            total_count = stats_result[0][0] or 0
            total_cost = round(stats_result[0][1] or 0, 2)
            total_yyyp_price = round(stats_result[0][2] or 0, 2)
            total_buff_price = round(stats_result[0][3] or 0, 2)
            total_steam_price = round(stats_result[0][4] or 0, 2)
        
        return jsonify({
            'success': True,
            'data': {
                'totalCount': total_count,
                'totalCost': total_cost,
                'totalYYYPPrice': total_yyyp_price,
                'totalBuffPrice': total_buff_price,
                'totalSteamPrice': total_steam_price
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


@webStockComponentsV1.route('/components/time-range/<steam_id>/<start_date>/<end_date>', methods=['GET'])
def get_components_by_time_range(steam_id, start_date, end_date):
    """按时间范围搜索库存组件 - 从 steam_stockComponents 表读取"""
    try:
        db = DatabaseManager()
        
        sql = f"""
        SELECT 
            assetid, instanceid, classid, item_name, weapon_name, 
            float_range, weapon_type, weapon_float, weapon_level, data_user, 
            buy_price, yyyp_price, buff_price, order_time, steam_price
        FROM steam_stockComponents
        WHERE data_user = ? 
            AND DATE(order_time) BETWEEN ? AND ?
        ORDER BY order_time DESC
        """
        
        results = db.execute_query(sql, (steam_id, start_date, end_date))
        
        # 转换为字典列表
        components = []
        if results:
            for row in results:
                def safe_float(value, default=0.0):
                    if value is None or value == '':
                        return default
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return default
                
                component = {
                    'component_id': row[0],
                    'item_name': row[3],
                    'weapon_name': row[4],
                    'float_range': row[5],
                    'weapon_type': row[6],
                    'weapon_float': row[7],
                    'weapon_level': row[8],
                    'buy_price': safe_float(row[10]),
                    'yyyp_price': safe_float(row[11]),
                    'buff_price': safe_float(row[12]),
                    'steam_price': safe_float(row[14]),
                    'order_time': row[13],
                    'component_name': row[3],
                    'component_type': row[6],
                    'quality': row[8],
                    'quantity': row[7],
                    'unit_cost': safe_float(row[10]),
                    'total_cost': safe_float(row[10]),
                    'source': '库存',
                    'purchase_date': row[13],
                    'status': '库存中',
                    'status_desc': ''
                }
                components.append(component)
        
        return jsonify({
            'success': True,
            'data': components,
            'total': len(components)
        }), 200
        
    except Exception as e:
        print(f"按时间范围搜索失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/use/<component_id>', methods=['POST'])
def use_component(component_id):
    """使用组件"""
    try:
        # TODO: 实现使用组件的逻辑
        # 可能需要更新if_inventory字段或添加使用记录
        
        return jsonify({
            'success': True,
            'message': f'组件 {component_id} 使用成功'
        }), 200
        
    except Exception as e:
        print(f"使用组件失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'操作失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/sell/<component_id>', methods=['POST'])
def sell_component(component_id):
    """出售组件"""
    try:
        # TODO: 实现出售组件的逻辑
        # 可能需要更新if_inventory字段或添加出售记录
        
        return jsonify({
            'success': True,
            'message': f'组件 {component_id} 出售成功'
        }), 200
        
    except Exception as e:
        print(f"出售组件失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'操作失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/components/detail/<component_id>', methods=['GET'])
def get_component_detail(component_id):
    """获取组件详细信息 - 从 steam_stockComponents 表读取"""
    try:
        db = DatabaseManager()
        
        sql = f"""
        SELECT 
            assetid, instanceid, classid, item_name, weapon_name, 
            float_range, weapon_type, weapon_float, weapon_level, data_user, 
            buy_price, yyyp_price, buff_price, order_time, steam_price
        FROM steam_stockComponents
        WHERE assetid = ?
        """
        
        results = db.execute_query(sql, (component_id,))
        
        if not results or len(results) == 0:
            return jsonify({
                'success': False,
                'error': '组件不存在'
            }), 404
        
        row = results[0]
        
        def safe_float(value, default=0.0):
            if value is None or value == '':
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        component_detail = {
            'component_id': row[0],
            'item_name': row[3],
            'weapon_name': row[4],
            'float_range': row[5],
            'weapon_type': row[6],
            'weapon_float': row[7],
            'weapon_level': row[8],
            'buy_price': safe_float(row[10]),
            'yyyp_price': safe_float(row[11]),
            'buff_price': safe_float(row[12]),
            'steam_price': safe_float(row[14]),
            'order_time': row[13],
            # 兼容旧字段
            'assetid': row[0],
            'instanceid': row[1],
            'classid': row[2],
            'component_name': row[3],
            'component_type': row[6],
            'quality': row[8],
            'quantity': row[7],
            'unit_cost': safe_float(row[10]),
            'total_cost': safe_float(row[10]),
            'source': '库存',
            'purchase_date': row[13],
            'status': '库存中',
            'status_desc': '',
            'data_user': row[9]
        }
        
        return jsonify({
            'success': True,
            'data': component_detail
        }), 200
        
    except Exception as e:
        print(f"查询组件详情失败: {e}")
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


@webStockComponentsV1.route('/update/buy_price/<steam_id>/<assetid>', methods=['PUT'])
def update_buy_price(steam_id, assetid):
    """
    更新指定组件的购入价格
    
    参数:
        steam_id: Steam用户ID (对应data_user字段)
        assetid: 资产ID
    
    请求体:
    {
        "buy_price": "100.50"
    }
    
    返回:
    {
        "success": True,
        "message": "价格更新成功"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'buy_price' not in data:
            return jsonify({
                'success': False,
                'message': '缺少 buy_price 参数'
            }), 400
        
        buy_price = data.get('buy_price')
        
        # 验证价格格式
        try:
            price_float = float(buy_price)
            if price_float < 0:
                return jsonify({
                    'success': False,
                    'message': '价格不能为负数'
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'message': '价格格式不正确'
            }), 400
        
        db = DatabaseManager()
        
        # 检查记录是否存在
        check_sql = """
        SELECT COUNT(*) FROM steam_stockComponents 
        WHERE assetid = ? AND data_user = ?
        """
        check_result = db.execute_query(check_sql, (assetid, steam_id))
        
        if not check_result or check_result[0][0] == 0:
            return jsonify({
                'success': False,
                'message': '未找到该组件记录'
            }), 404
        
        # 更新价格
        update_sql = """
        UPDATE steam_stockComponents 
        SET buy_price = ?
        WHERE assetid = ? AND data_user = ?
        """
        
        db.execute_update(update_sql, (str(buy_price), assetid, steam_id))
        
        print(f"✅ 价格更新成功 - assetid: {assetid}, steam_id: {steam_id}, buy_price: {buy_price}")
        
        return jsonify({
            'success': True,
            'message': '价格更新成功'
        })
        
    except Exception as e:
        print(f"❌ 更新价格失败 - assetid: {assetid}, steam_id: {steam_id}")
        print(f"错误详情: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

