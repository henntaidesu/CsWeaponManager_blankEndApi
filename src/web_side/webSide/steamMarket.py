from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.now_time import today
from src.db_manager.steam.steam_buy import SteamBuyModel
from src.db_manager.steam.steam_sell import SteamSellModel
import requests

webSteamMarketV1 = Blueprint('webSteamMarketV1', __name__)

# ==================== Common APIs ====================

@webSteamMarketV1.route('/getBuyGameNames', methods=['GET'])
def getBuyGameNames():
    """获取Steam购买记录中的游戏名称列表（去重）"""
    try:
        sql = """
        SELECT DISTINCT game_name 
        FROM steam_buy 
        WHERE game_name IS NOT NULL AND game_name != ''
        ORDER BY 
            CASE WHEN game_name = 'Counter-Strike 2' THEN 0 ELSE 1 END,
            game_name
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                game_names = [row[0] for row in data]
                return jsonify(game_names), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"获取Steam购买游戏名称列表失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/getSellGameNames', methods=['GET'])
def getSellGameNames():
    """获取Steam销售记录中的游戏名称列表（去重）"""
    try:
        sql = """
        SELECT DISTINCT game_name 
        FROM steam_sell 
        WHERE game_name IS NOT NULL AND game_name != ''
        ORDER BY 
            CASE WHEN game_name = 'Counter-Strike 2' THEN 0 ELSE 1 END,
            game_name
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                game_names = [row[0] for row in data]
                return jsonify(game_names), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"获取Steam销售游戏名称列表失败: {e}")
        return jsonify([]), 500

# ==================== Steam Buy APIs ====================

@webSteamMarketV1.route('/countSteamBuyNumber', methods=['GET'])
def countSteamBuyNumber():
    """获取Steam购买记录总数"""
    try:
        records = SteamBuyModel.find_all()
        count = len(records)
        return jsonify({"count": count}), 200
    except Exception as e:
        print(f"查询Steam购买数量失败: {e}")
        return jsonify({"count": 0}), 500

@webSteamMarketV1.route('/getSteamBuyData/<int:min>/<int:max>', methods=['GET'])
def getSteamBuyData(min, max):
    """获取Steam购买数据（分页）"""
    try:
        records = SteamBuyModel.find_all(
            "1=1 ORDER BY trade_date DESC", 
            (), 
            limit=max, 
            offset=min
        )
        data = []
        for record in records:
            data.append([
                record.ID, record.item_name, record.weapon_name, 
                record.weapon_type, record.weapon_float, record.float_range, 
                record.price, 'Steam', record.trade_date, '已完成', record.game_name
            ])
        return jsonify(data), 200
    except Exception as e:
        print(f"查询Steam购买数据失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/selectSteamBuyWeaponName/<itemName>', methods=['GET'])
def selectSteamBuyWeaponName(itemName):
    """根据武器名称搜索Steam购买记录"""
    try:
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, 'Steam' as \"from\", trade_date, '已完成' as status, game_name FROM steam_buy WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%' ORDER BY trade_date DESC;"
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"搜索Steam购买记录失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/getSteamBuyDataByStatus/<status>/<int:min>/<int:max>', methods=['GET'])
def getSteamBuyDataByStatus(status, min, max):
    """根据状态获取Steam购买数据（Steam数据都是已完成状态）"""
    try:
        if status == 'all' or status == '已完成':
            sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, 'Steam' as \"from\", trade_date, '已完成' as status, game_name FROM steam_buy ORDER BY trade_date DESC LIMIT {max} OFFSET {min};"
        else:
            # 其他状态返回空数据，因为Steam数据都是已完成的
            return jsonify([]), 200
        
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"根据状态查询Steam购买数据失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/getSteamBuyDataByGameName/<gameName>/<int:min>/<int:max>', methods=['GET'])
def getSteamBuyDataByGameName(gameName, min, max):
    """根据游戏名称获取Steam购买数据（分页）"""
    try:
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, 'Steam' as \"from\", trade_date, '已完成' as status, game_name FROM steam_buy WHERE game_name = '{gameName}' ORDER BY trade_date DESC LIMIT {max} OFFSET {min};"
        
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"根据游戏名称查询Steam购买数据失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/getSteamBuyStats', methods=['GET'])
def getSteamBuyStats():
    """获取Steam购买统计数据"""
    try:
        sql = """
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(*) as completed_count,
            0 as cancelled_count,
            0 as pending_count
        FROM steam_buy
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"获取Steam购买统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

@webSteamMarketV1.route('/getSteamBuyStatsBySearch/<itemName>', methods=['GET'])
def getSteamBuyStatsBySearch(itemName):
    """根据搜索关键词获取Steam购买统计"""
    try:
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(*) as completed_count,
            0 as cancelled_count,
            0 as pending_count
        FROM steam_buy 
        WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%'
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"根据搜索获取Steam购买统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

@webSteamMarketV1.route('/getSteamBuyStatsByStatus/<status>', methods=['GET'])
def getSteamBuyStatsByStatus(status):
    """根据状态获取Steam购买统计"""
    try:
        if status == 'all' or status == '已完成':
            sql = """
            SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(price), 0) as total_amount,
                COALESCE(AVG(price), 0) as avg_price,
                COUNT(*) as completed_count,
                0 as cancelled_count,
                0 as pending_count
            FROM steam_buy
            """
        else:
            # 其他状态返回0统计
            return jsonify({
                "total_count": 0,
                "total_amount": 0,
                "avg_price": 0,
                "completed_count": 0,
                "cancelled_count": 0,
                "pending_count": 0
            }), 200
        
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"根据状态获取Steam购买统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

@webSteamMarketV1.route('/getSteamBuyStatsByGameName/<gameName>', methods=['GET'])
def getSteamBuyStatsByGameName(gameName):
    """根据游戏名称获取Steam购买统计"""
    try:
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(*) as completed_count,
            0 as cancelled_count,
            0 as pending_count
        FROM steam_buy 
        WHERE game_name = '{gameName}'
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"根据游戏名称获取Steam购买统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

@webSteamMarketV1.route('/searchSteamBuyByTimeRange/<startDate>/<endDate>', methods=['GET'])
def searchSteamBuyByTimeRange(startDate, endDate):
    """根据时间范围搜索Steam购买记录"""
    try:
        sql = f"""
        SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, 'Steam' as \"from\", trade_date, '已完成' as status, game_name 
        FROM steam_buy 
        WHERE DATE(trade_date) BETWEEN '{startDate}' AND '{endDate}'
        ORDER BY trade_date DESC
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"根据时间范围搜索Steam购买记录失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/getSteamBuyStatsByTimeRange/<startDate>/<endDate>', methods=['GET'])
def getSteamBuyStatsByTimeRange(startDate, endDate):
    """根据时间范围获取Steam购买统计"""
    try:
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(*) as completed_count,
            0 as cancelled_count,
            0 as pending_count
        FROM steam_buy 
        WHERE DATE(trade_date) BETWEEN '{startDate}' AND '{endDate}'
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"根据时间范围获取Steam购买统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

# ==================== Steam Sell APIs ====================

@webSteamMarketV1.route('/countSteamSellNumber', methods=['GET'])
def countSteamSellNumber():
    """获取Steam销售记录总数"""
    try:
        records = SteamSellModel.find_all()
        count = len(records)
        return jsonify({"count": count}), 200
    except Exception as e:
        print(f"查询Steam销售数量失败: {e}")
        return jsonify({"count": 0}), 500

@webSteamMarketV1.route('/getSteamSellData/<int:min>/<int:max>', methods=['GET'])
def getSteamSellData(min, max):
    """获取Steam销售数据（分页）"""
    try:
        records = SteamSellModel.find_all(
            "1=1 ORDER BY trade_date DESC", 
            (), 
            limit=max, 
            offset=min
        )
        data = []
        for record in records:
            data.append([
                record.ID, record.item_name, record.weapon_name, 
                record.weapon_type, record.weapon_float, record.float_range, 
                record.price, 'Steam', record.trade_date, '已完成', record.game_name
            ])
        return jsonify(data), 200
    except Exception as e:
        print(f"查询Steam销售数据失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/selectSteamSellWeaponName/<itemName>', methods=['GET'])
def selectSteamSellWeaponName(itemName):
    """根据武器名称搜索Steam销售记录"""
    try:
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, 'Steam' as \"from\", trade_date, '已完成' as status, game_name FROM steam_sell WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%' ORDER BY trade_date DESC;"
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"搜索Steam销售记录失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/getSteamSellDataByStatus/<status>/<int:min>/<int:max>', methods=['GET'])
def getSteamSellDataByStatus(status, min, max):
    """根据状态获取Steam销售数据（Steam数据都是已完成状态）"""
    try:
        if status == 'all' or status == '已完成':
            sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, 'Steam' as \"from\", trade_date, '已完成' as status, game_name FROM steam_sell ORDER BY trade_date DESC LIMIT {max} OFFSET {min};"
        else:
            # 其他状态返回空数据，因为Steam数据都是已完成的
            return jsonify([]), 200
        
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"根据状态查询Steam销售数据失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/getSteamSellDataByGameName/<gameName>/<int:min>/<int:max>', methods=['GET'])
def getSteamSellDataByGameName(gameName, min, max):
    """根据游戏名称获取Steam销售数据（分页）"""
    try:
        sql = f"SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, 'Steam' as \"from\", trade_date, '已完成' as status, game_name FROM steam_sell WHERE game_name = '{gameName}' ORDER BY trade_date DESC LIMIT {max} OFFSET {min};"
        
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"根据游戏名称查询Steam销售数据失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/getSteamSellStats', methods=['GET'])
def getSteamSellStats():
    """获取Steam销售统计数据"""
    try:
        sql = """
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(*) as completed_count,
            0 as cancelled_count,
            0 as pending_count
        FROM steam_sell
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"获取Steam销售统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

@webSteamMarketV1.route('/getSteamSellStatsBySearch/<itemName>', methods=['GET'])
def getSteamSellStatsBySearch(itemName):
    """根据搜索关键词获取Steam销售统计"""
    try:
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(*) as completed_count,
            0 as cancelled_count,
            0 as pending_count
        FROM steam_sell 
        WHERE item_name LIKE '%{itemName}%' OR weapon_name LIKE '%{itemName}%'
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"根据搜索获取Steam销售统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

@webSteamMarketV1.route('/getSteamSellStatsByStatus/<status>', methods=['GET'])
def getSteamSellStatsByStatus(status):
    """根据状态获取Steam销售统计"""
    try:
        if status == 'all' or status == '已完成':
            sql = """
            SELECT 
                COUNT(*) as total_count,
                COALESCE(SUM(price), 0) as total_amount,
                COALESCE(AVG(price), 0) as avg_price,
                COUNT(*) as completed_count,
                0 as cancelled_count,
                0 as pending_count
            FROM steam_sell
            """
        else:
            # 其他状态返回0统计
            return jsonify({
                "total_count": 0,
                "total_amount": 0,
                "avg_price": 0,
                "completed_count": 0,
                "cancelled_count": 0,
                "pending_count": 0
            }), 200
        
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"根据状态获取Steam销售统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

@webSteamMarketV1.route('/getSteamSellStatsByGameName/<gameName>', methods=['GET'])
def getSteamSellStatsByGameName(gameName):
    """根据游戏名称获取Steam销售统计"""
    try:
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(*) as completed_count,
            0 as cancelled_count,
            0 as pending_count
        FROM steam_sell 
        WHERE game_name = '{gameName}'
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"根据游戏名称获取Steam销售统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

@webSteamMarketV1.route('/searchSteamSellByTimeRange/<startDate>/<endDate>', methods=['GET'])
def searchSteamSellByTimeRange(startDate, endDate):
    """根据时间范围搜索Steam销售记录"""
    try:
        sql = f"""
        SELECT ID, item_name, weapon_name, weapon_type, weapon_float, float_range, price, 'Steam' as \"from\", trade_date, '已完成' as status, game_name 
        FROM steam_sell 
        WHERE DATE(trade_date) BETWEEN '{startDate}' AND '{endDate}'
        ORDER BY trade_date DESC
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag:
                return jsonify(data), 200
        return jsonify([]), 200
    except Exception as e:
        print(f"根据时间范围搜索Steam销售记录失败: {e}")
        return jsonify([]), 500

@webSteamMarketV1.route('/getSteamSellStatsByTimeRange/<startDate>/<endDate>', methods=['GET'])
def getSteamSellStatsByTimeRange(startDate, endDate):
    """根据时间范围获取Steam销售统计"""
    try:
        sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price,
            COUNT(*) as completed_count,
            0 as cancelled_count,
            0 as pending_count
        FROM steam_sell 
        WHERE DATE(trade_date) BETWEEN '{startDate}' AND '{endDate}'
        """
        result = Date_base().select(sql)
        if result and len(result) == 2:
            flag, data = result
            if flag and len(data) > 0:
                stats = data[0]
                return jsonify({
                    "total_count": stats[0],
                    "total_amount": round(float(stats[1]), 2),
                    "avg_price": round(float(stats[2]), 2),
                    "completed_count": stats[3],
                    "cancelled_count": stats[4],
                    "pending_count": stats[5]
                }), 200
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 200
    except Exception as e:
        print(f"根据时间范围获取Steam销售统计失败: {e}")
        return jsonify({
            "total_count": 0,
            "total_amount": 0,
            "avg_price": 0,
            "completed_count": 0,
            "cancelled_count": 0,
            "pending_count": 0
        }), 500

# ==================== Combined APIs ====================

@webSteamMarketV1.route('/getSteamMarketStats', methods=['GET'])
def getSteamMarketStats():
    """获取Steam市场综合统计数据（购买+销售）"""
    try:
        # 获取购买统计
        buy_sql = """
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price
        FROM steam_buy
        """
        
        # 获取销售统计
        sell_sql = """
        SELECT 
            COUNT(*) as total_count,
            COALESCE(SUM(price), 0) as total_amount,
            COALESCE(AVG(price), 0) as avg_price
        FROM steam_sell
        """
        
        buy_result = Date_base().select(buy_sql)
        sell_result = Date_base().select(sell_sql)
        
        buy_stats = [0, 0, 0]
        sell_stats = [0, 0, 0]
        
        if buy_result and len(buy_result) == 2 and buy_result[0] and len(buy_result[1]) > 0:
            buy_stats = buy_result[1][0]
        
        if sell_result and len(sell_result) == 2 and sell_result[0] and len(sell_result[1]) > 0:
            sell_stats = sell_result[1][0]
        
        # 计算净收益
        net_profit = float(sell_stats[1]) - float(buy_stats[1])
        
        return jsonify({
            "buy_count": buy_stats[0],
            "buy_total": round(float(buy_stats[1]), 2),
            "buy_avg": round(float(buy_stats[2]), 2),
            "sell_count": sell_stats[0],
            "sell_total": round(float(sell_stats[1]), 2),
            "sell_avg": round(float(sell_stats[2]), 2),
            "net_profit": round(net_profit, 2),
            "total_transactions": buy_stats[0] + sell_stats[0]
        }), 200
    except Exception as e:
        print(f"获取Steam市场综合统计失败: {e}")
        return jsonify({
            "buy_count": 0,
            "buy_total": 0,
            "buy_avg": 0,
            "sell_count": 0,
            "sell_total": 0,
            "sell_avg": 0,
            "net_profit": 0,
            "total_transactions": 0
        }), 500
