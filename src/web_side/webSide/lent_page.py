from flask import jsonify, request, Blueprint
from src.execution_db import Date_base
from src.db_manager.index.lease import LeaseModel

webLentPageV1 = Blueprint('webLentPageV1', __name__)

@webLentPageV1.route('/getWeaponTypes', methods=['GET'])
def getWeaponTypes():
    """获取所有武器类型的唯一值"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT weapon_type 
        FROM lease 
        WHERE weapon_type IS NOT NULL AND weapon_type != '' 
        ORDER BY weapon_type
        """
        success, result = db.select(sql)
        
        weapon_types = []
        if success and result:
            for row in result:
                if row[0]:  # 确保不是空值
                    weapon_types.append(row[0])
        
        return jsonify({
            'success': True,
            'data': weapon_types
        }), 200
        
    except Exception as e:
        print(f"获取武器类型失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

@webLentPageV1.route('/getFloatRanges', methods=['GET'])
def getFloatRanges():
    """获取所有磨损等级的唯一值"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT float_range 
        FROM lease 
        WHERE float_range IS NOT NULL AND float_range != '' 
        ORDER BY float_range
        """
        success, result = db.select(sql)
        
        float_ranges = []
        if success and result:
            for row in result:
                if row[0]:  # 确保不是空值
                    float_ranges.append(row[0])
        
        return jsonify({
            'success': True,
            'data': float_ranges
        }), 200
        
    except Exception as e:
        print(f"获取磨损等级失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

@webLentPageV1.route('/searchByTypeAndWear', methods=['POST'])
def searchByTypeAndWear():
    """根据类型和磨损等级搜索租赁记录"""
    try:
        data = request.get_json()
        weapon_type = data.get('weapon_type', '')
        float_range = data.get('float_range', '')
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        
        # 构建查询条件
        conditions = []
        params = []
        
        if weapon_type:
            conditions.append("weapon_type = ?")
            params.append(weapon_type)
            
        if float_range:
            conditions.append("float_range = ?")
            params.append(float_range)
        
        # 如果没有条件，返回空结果
        if not conditions:
            return jsonify({
                'success': True,
                'data': [],
                'total': 0,
                'page': page,
                'page_size': page_size
            }), 200
        
        where_clause = " AND ".join(conditions)
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 查询数据
        db = Date_base()
        
        # 获取总数
        count_sql = f"SELECT COUNT(*) FROM lease WHERE {where_clause}"
        count_result = db.execute_query(count_sql, tuple(params))
        total = count_result[0][0] if count_result else 0
        
        # 获取分页数据
        data_sql = f"""
        SELECT ID, lease_day, status, unit_price, deposit, create_time, 
               item_name, weapon_name, weapon_type, float_range, weapon_float, 
               leaser_id, leaser_name, buy_of, lease_from
        FROM lease 
        WHERE {where_clause} 
        ORDER BY create_time DESC 
        LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        data_result = db.execute_query(data_sql, tuple(params))
        
        # 格式化数据
        records = []
        for row in data_result:
            records.append([
                row[0],   # ID
                row[1],   # lease_day
                row[2],   # status
                row[3],   # unit_price
                row[4],   # deposit
                row[5],   # create_time
                row[6],   # item_name
                row[7],   # weapon_name
                row[8],   # weapon_type
                row[9],   # float_range
                row[10],  # weapon_float
                row[11],  # leaser_id
                row[12],  # leaser_name
                row[13],  # buy_of
                row[14]   # lease_from
            ])
        
        return jsonify({
            'success': True,
            'data': records,
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200
        
    except Exception as e:
        print(f"按类型和磨损等级搜索失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': [],
            'total': 0
        }), 500

@webLentPageV1.route('/getStatsByTypeAndWear', methods=['POST'])
def getStatsByTypeAndWear():
    """获取按类型和磨损等级筛选的统计数据"""
    try:
        data = request.get_json()
        weapon_type = data.get('weapon_type', '')
        float_range = data.get('float_range', '')
        
        # 构建查询条件
        conditions = []
        params = []
        
        if weapon_type:
            conditions.append("weapon_type = ?")
            params.append(weapon_type)
            
        if float_range:
            conditions.append("float_range = ?")
            params.append(float_range)
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        db = Date_base()
        
        # 获取统计数据
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(unit_price * lease_day), 0) as total_amount,
            COALESCE(AVG(unit_price), 0) as avg_price,
            COALESCE(SUM(lease_day), 0) as total_lease_days,
            COALESCE(AVG(lease_day), 0) as avg_lease_days,
            COUNT(CASE WHEN status = '租赁中' THEN 1 END) as renting_count
        FROM lease 
        {where_clause}
        """
        
        result = db.execute_query(sql, tuple(params))
        
        if result:
            row = result[0]
            stats = {
                'totalCount': row[0],
                'totalAmount': round(row[1], 2),
                'avgPrice': round(row[2], 2),
                'totalLeaseDays': row[3],
                'avgLeaseDays': round(row[4], 2),
                'rentingCount': row[5]
            }
        else:
            stats = {
                'totalCount': 0,
                'totalAmount': 0,
                'avgPrice': 0,
                'totalLeaseDays': 0,
                'avgLeaseDays': 0,
                'rentingCount': 0
            }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        print(f"获取统计数据失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': {}
        }), 500
