from flask import jsonify, request, Blueprint
from src.execution_db import Date_base
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from src.db_manager.index.buy import BuyModel

webBuyPageV1 = Blueprint('webBuyPageV1', __name__)

@webBuyPageV1.route('/getWeaponTypes', methods=['GET'])
def getWeaponTypes():
    """获取所有武器类型的唯一值"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT weapon_type 
        FROM buy 
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
        logger.error(f"获取武器类型失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

@webBuyPageV1.route('/getFloatRanges', methods=['GET'])
def getFloatRanges():
    """获取所有磨损等级的唯一值"""
    try:
        db = Date_base()
        sql = """
        SELECT DISTINCT float_range 
        FROM buy 
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
        logger.error(f"获取磨损等级失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': []
        }), 500

@webBuyPageV1.route('/searchByTypeAndWear', methods=['POST'])
def searchByTypeAndWear():
    """根据类型和磨损等级搜索购买记录"""
    try:
        data = request.get_json()
        weapon_type = data.get('weapon_type', '')
        float_range = data.get('float_range', '')
        page = data.get('page', 1)
        page_size = data.get('page_size', 20)
        
        # 构建查询条件
        conditions = []
        
        if weapon_type:
            conditions.append(f"weapon_type = '{weapon_type}'")
            
        if float_range:
            conditions.append(f"float_range = '{float_range}'")
        
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
        count_sql = f"SELECT COUNT(*) FROM buy WHERE {where_clause}"
        success, count_result = db.select(count_sql)
        total = count_result[0][0] if success and count_result else 0
        
        # 获取分页数据
        data_sql = f"""
        SELECT ID, weapon_name, weapon_type, item_name, weapon_float, float_range, 
               price, seller_name, status, status_sub, `from`, order_time, 
               steam_id, buy_number, sell_of, st, sou, payment, trade_type, data_user
        FROM buy 
        WHERE {where_clause} 
        ORDER BY order_time DESC 
        LIMIT {page_size} OFFSET {offset}
        """
        success2, data_result = db.select(data_sql)
        
        # 格式化数据
        records = []
        if success2 and data_result:
            for row in data_result:
                records.append([
                    row[0],   # ID
                    row[1],   # weapon_name
                    row[2],   # weapon_type
                    row[3],   # item_name
                    row[4],   # weapon_float
                    row[5],   # float_range
                    row[6],   # price
                    row[7],   # seller_name
                    row[8],   # status
                    row[9],   # status_sub
                    row[10],  # from
                    row[11],  # order_time
                    row[12],  # steam_id
                    row[13],  # buy_number
                    row[14],  # sell_of
                    row[15],  # st
                    row[16],  # sou
                    row[17],  # payment
                    row[18],  # trade_type
                    row[19]   # data_user
                ])
        
        return jsonify({
            'success': True,
            'data': records,
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200
        
    except Exception as e:
        logger.error(f"按类型和磨损等级搜索失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': [],
            'total': 0
        }), 500

@webBuyPageV1.route('/getStatsByTypeAndWear', methods=['POST'])
def getStatsByTypeAndWear():
    """获取按类型和磨损等级筛选的统计数据"""
    try:
        data = request.get_json()
        weapon_type = data.get('weapon_type', '')
        float_range = data.get('float_range', '')
        
        # 构建查询条件
        conditions = []
        
        if weapon_type:
            conditions.append(f"weapon_type = '{weapon_type}'")
            
        if float_range:
            conditions.append(f"float_range = '{float_range}'")
        
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
        
        db = Date_base()
        
        # 获取统计数据
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(CASE WHEN status = '已完成' THEN 1 END) as completed_count,
            COUNT(CASE WHEN status = '已取消' THEN 1 END) as cancelled_count,
            COUNT(CASE WHEN status = '待收货' THEN 1 END) as pending_count
        FROM buy 
        {where_clause}
        """
        
        success, result = db.select(sql)
        
        if success and result:
            row = result[0]
            stats = {
                'totalCount': row[0],
                'totalAmount': round(row[1], 2),
                'avgPrice': round(row[2], 2),
                'completedCount': row[3],
                'cancelledCount': row[4],
                'pendingCount': row[5]
            }
        else:
            stats = {
                'totalCount': 0,
                'totalAmount': 0,
                'avgPrice': 0,
                'completedCount': 0,
                'cancelledCount': 0,
                'pendingCount': 0
            }
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'data': {}
        }), 500
