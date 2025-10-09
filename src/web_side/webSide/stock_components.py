from flask import jsonify, request, Blueprint
from src.db_manager.database import DatabaseManager

webStockComponentsV1 = Blueprint('webStockComponentsV1', __name__)

# 组件的classid常量
COMPONENT_CLASSID = '3604678661'


@webStockComponentsV1.route('/components/<steam_id>', methods=['GET'])
def get_components(steam_id):
    """获取指定用户的库存组件列表"""
    try:
        # 获取查询参数
        search_text = request.args.get('search', '')
        status = request.args.get('status', '')
        component_types = request.args.getlist('component_types[]')  # 多选
        quality = request.args.getlist('quality[]')  # 多选
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        db = DatabaseManager()
        
        # 构建查询条件
        where_conditions = [
            "data_user = ?",
            "if_inventory = '1'",
            "classid = ?"
        ]
        params = [steam_id, COMPONENT_CLASSID]
        
        # 关键词搜索
        if search_text:
            where_conditions.append("item_name LIKE ?")
            params.append(f"%{search_text}%")
        
        # 状态筛选（预留字段，当前数据库可能没有status字段）
        # if status:
        #     where_conditions.append("status = ?")
        #     params.append(status)
        
        # 组件类型筛选（需要根据item_name判断类型）
        if component_types and len(component_types) > 0:
            type_conditions = []
            for comp_type in component_types:
                type_conditions.append("item_name LIKE ?")
                params.append(f"%{comp_type}%")
            where_conditions.append(f"({' OR '.join(type_conditions)})")
        
        # 品质筛选（需要根据item_name判断品质）
        if quality and len(quality) > 0:
            quality_conditions = []
            for qual in quality:
                quality_conditions.append("item_name LIKE ?")
                params.append(f"%{qual}%")
            where_conditions.append(f"({' OR '.join(quality_conditions)})")
        
        where_clause = " AND ".join(where_conditions)
        
        # 查询数据
        sql = f"""
        SELECT 
            assetid, instanceid, classid, item_name, weapon_name, 
            weapon_type, weapon_float, float_range, remark, 
            data_user, buy_price, yyyp_price, buff_price, steam_price, order_time
        FROM steam_inventory
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
                component = {
                    'component_id': row[0],  # assetid
                    'assetid': row[0],
                    'instanceid': row[1],
                    'classid': row[2],
                    'component_name': row[3],  # item_name
                    'item_name': row[3],
                    'weapon_name': row[4],
                    'component_type': parse_component_type(row[3]),  # 从item_name解析类型
                    'weapon_type': row[5],
                    'weapon_float': row[6],
                    'float_range': row[7],
                    'quality': parse_quality(row[3]),  # 从item_name解析品质
                    'quantity': 1,  # 每个assetid代表1个物品
                    'unit_cost': float(row[10]) if row[10] else 0,
                    'total_cost': float(row[10]) if row[10] else 0,
                    'source': '库存',  # 可以根据需要扩展
                    'purchase_date': row[14],  # order_time
                    'status': '库存中',  # 当前if_inventory='1'，所以都是库存中
                    'status_desc': row[8],  # remark
                    'buy_price': row[10],
                    'yyyp_price': row[11],
                    'buff_price': row[12],
                    'steam_price': row[13]
                }
                components.append(component)
        
        # 获取总数
        count_params = params[:-2]  # 去掉limit和offset参数
        count_sql = f"SELECT COUNT(*) FROM steam_inventory WHERE {where_clause}"
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
    """获取库存组件统计信息"""
    try:
        db = DatabaseManager()
        
        # 统计总数
        total_sql = f"""
        SELECT COUNT(*) 
        FROM steam_inventory 
        WHERE data_user = ? AND if_inventory = '1' AND classid = ?
        """
        total_result = db.execute_query(total_sql, (steam_id, COMPONENT_CLASSID))
        total_count = total_result[0][0] if total_result else 0
        
        # 统计总成本
        cost_sql = f"""
        SELECT 
            SUM(CAST(buy_price AS REAL)) as total_cost,
            AVG(CAST(buy_price AS REAL)) as avg_cost
        FROM steam_inventory
        WHERE data_user = ? AND if_inventory = '1' AND classid = ?
        """
        cost_result = db.execute_query(cost_sql, (steam_id, COMPONENT_CLASSID))
        
        total_cost = 0
        avg_cost = 0
        if cost_result and cost_result[0][0] is not None:
            total_cost = round(cost_result[0][0], 2)
            avg_cost = round(cost_result[0][1], 2) if cost_result[0][1] else 0
        
        # 按状态统计（目前都是库存中）
        in_stock_count = total_count
        used_count = 0
        sold_count = 0
        
        return jsonify({
            'success': True,
            'data': {
                'totalCount': total_count,
                'totalCost': total_cost,
                'avgCost': avg_cost,
                'inStockCount': in_stock_count,
                'usedCount': used_count,
                'soldCount': sold_count
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
    """按时间范围搜索库存组件"""
    try:
        db = DatabaseManager()
        
        sql = f"""
        SELECT 
            assetid, instanceid, classid, item_name, weapon_name, 
            weapon_type, weapon_float, float_range, remark, 
            data_user, buy_price, yyyp_price, buff_price, steam_price, order_time
        FROM steam_inventory
        WHERE data_user = ? 
            AND if_inventory = '1' 
            AND classid = ?
            AND DATE(order_time) BETWEEN ? AND ?
        ORDER BY order_time DESC
        """
        
        results = db.execute_query(sql, (steam_id, COMPONENT_CLASSID, start_date, end_date))
        
        # 转换为字典列表
        components = []
        if results:
            for row in results:
                component = {
                    'component_id': row[0],
                    'assetid': row[0],
                    'component_name': row[3],
                    'item_name': row[3],
                    'component_type': parse_component_type(row[3]),
                    'quality': parse_quality(row[3]),
                    'quantity': 1,
                    'unit_cost': float(row[10]) if row[10] else 0,
                    'total_cost': float(row[10]) if row[10] else 0,
                    'source': '库存',
                    'purchase_date': row[14],
                    'status': '库存中',
                    'status_desc': row[8]
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
    """获取组件详细信息"""
    try:
        db = DatabaseManager()
        
        sql = f"""
        SELECT 
            assetid, instanceid, classid, item_name, weapon_name, 
            weapon_type, weapon_float, float_range, remark, 
            data_user, buy_price, yyyp_price, buff_price, steam_price, order_time
        FROM steam_inventory
        WHERE assetid = ? AND classid = ?
        """
        
        results = db.execute_query(sql, (component_id, COMPONENT_CLASSID))
        
        if not results or len(results) == 0:
            return jsonify({
                'success': False,
                'error': '组件不存在'
            }), 404
        
        row = results[0]
        component_detail = {
            'component_id': row[0],
            'assetid': row[0],
            'instanceid': row[1],
            'classid': row[2],
            'component_name': row[3],
            'item_name': row[3],
            'weapon_name': row[4],
            'component_type': parse_component_type(row[3]),
            'weapon_type': row[5],
            'weapon_float': row[6],
            'float_range': row[7],
            'quality': parse_quality(row[3]),
            'quantity': 1,
            'unit_cost': float(row[10]) if row[10] else 0,
            'total_cost': float(row[10]) if row[10] else 0,
            'source': '库存',
            'purchase_date': row[14],
            'status': '库存中',
            'status_desc': row[8],
            'buy_price': row[10],
            'yyyp_price': row[11],
            'buff_price': row[12],
            'steam_price': row[13],
            'data_user': row[9]
        }
        
        return jsonify({
            'success': True,
            'data': component_detail
        }), 200
        
    except Exception as e:
        print(f"查询组件详情失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'查询失败: {str(e)}'
        }), 500


def parse_component_type(item_name):
    """从物品名称解析组件类型"""
    if not item_name:
        return '未知'
    
    # 组件类型关键词映射
    type_keywords = {
        '印花': '印花',
        '贴纸': '贴纸',
        '涂鸦': '涂鸦',
        '探员': '探员',
        '音乐盒': '音乐盒',
        '徽章': '徽章',
        '补丁': '补丁',
        '勋章': '徽章',
        '硬币': '徽章'
    }
    
    for keyword, comp_type in type_keywords.items():
        if keyword in item_name:
            return comp_type
    
    return '其他'


def parse_quality(item_name):
    """从物品名称解析品质等级"""
    if not item_name:
        return '普通级'
    
    # 品质关键词映射
    quality_keywords = {
        'StatTrak™': '违禁',
        '★': '违禁',
        '纪念品': '奇异',
        '(Holo)': '非凡',
        '(Foil)': '超凡',
        '(Gold)': '超凡',
        '高级': '高级',
        '卓越': '卓越'
    }
    
    for keyword, quality in quality_keywords.items():
        if keyword in item_name:
            return quality
    
    # 默认返回普通级
    return '普通级'

