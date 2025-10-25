from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.now_time import today
from src.db_manager.yyyp.yyyp_lent import YyypLentModel
import requests

youpin898LentV1 = Blueprint('youpin898LentV1', __name__)

@youpin898LentV1.route('/getNowLentingList', methods=['get'])
def getNowLentingList():
    """获取当前租赁中的订单列表（不包括已完成的）"""
    try:
        records = YyypLentModel.find_all("status NOT IN ('完成')")
        data = [[record.ID] for record in records]
        return jsonify(data), 200
    except Exception as e:
        print(f"查询租借列表失败: {e}")
        return jsonify([]), 500  

@youpin898LentV1.route('/getTimeOutLent', methods=['get'])
def getTimeOutLent():
    """获取超时的租赁订单"""
    sql = f"SELECT ID FROM yyyp_lent WHERE lean_end_time < '{today()}' and status IN ('白玩中', '归还中', '租赁中')"
    flag, data = Date_base().select(sql)
    return jsonify(data), 200

@youpin898LentV1.route('/selectApexTime/<steamId>', methods=['get'])
def selectApexTime(steamId):
    """
    获取指定steamId的最新租赁订单时间
    用于判断是否有新数据需要同步
    """
    try:
        sql = f"SELECT lean_start_time FROM yyyp_lent WHERE data_user = '{steamId}' ORDER BY lean_start_time DESC LIMIT 1"
        flag, data = Date_base().select(sql)
        
        if flag and data and len(data) > 0:
            apex_time = data[0][0]
            return jsonify(apex_time), 200
        else:
            # 如果没有数据，返回一个很早的时间
            return jsonify('2000-01-01 00:00:00'), 200
    except Exception as e:
        print(f"查询最新租赁时间失败: {e}")
        return jsonify('2000-01-01 00:00:00'), 500

@youpin898LentV1.route('/getCount/<steamId>', methods=['get'])
def getCount(steamId):
    """
    获取指定steamId的租赁订单总数
    用于分页获取历史数据
    """
    try:
        sql = f"SELECT COUNT(*) FROM yyyp_lent WHERE data_user = '{steamId}'"
        flag, data = Date_base().select(sql)
        
        if flag and data and len(data) > 0:
            count = data[0][0]
            return jsonify(count), 200
        else:
            return jsonify(0), 200
    except Exception as e:
        print(f"查询租赁订单数量失败: {e}")
        return jsonify(0), 500

@youpin898LentV1.route('/updateLentData', methods=['post'])
def updateLentData():
    """更新租赁订单状态"""
    data = request.get_json()
    ID = data['ID']
    status = data['status']
    orderSubStatusName = data['orderSubStatusName']
    data_from = data['from']
    lean_end_time = data['lean_end_time']
    totalLeaseDays = data['totalLeaseDays']
    
    sql = (f"UPDATE yyyp_lent SET  status = '{status}', last_status = '{orderSubStatusName}', " 
           f"lean_end_time = '{lean_end_time}', total_Lease_Days = {totalLeaseDays} WHERE ID = '{ID}';")
    flag = Date_base().update(sql)
    
    if flag:
        return 'update_info', 200
    else:
        return "update_error", 500


@youpin898LentV1.route('/insert_webside_lentdata', methods=['post'])
def insert_webside_lentdata():
    """插入租赁订单数据"""
    data = request.get_json()
    
    ID = data['ID']
    weapon_name = data['weapon_name']
    item_name = data['item_name']
    weapon_float = data.get('weapon_float')
    float_range = data['float_range']
    price = data['price']
    lent_user_name = data['buyer_user_name']
    status = data['status']
    orderSubStatusName = data['orderSubStatusName']
    data_from = data['from']
    lean_start_time = data['lean_start_time']
    lean_end_time = data.get('lean_end_time')
    totalLeaseDays = int(data['totalLeaseDays'])
    # leaseMaxDays 字段可选，如果没有提供则使用 totalLeaseDays 作为默认值
    max_Lease_Days = int(data.get('leaseMaxDays', totalLeaseDays))
    data_user = data.get('data_user', '')
    
    # 处理weapon_float为None的情况
    if weapon_float is None:
        weapon_float_str = 'NULL'
    else:
        weapon_float_str = str(weapon_float)
    
    # 处理lean_end_time为None的情况
    if lean_end_time is None:
        lean_end_time_str = 'NULL'
    else:
        lean_end_time_str = f"'{lean_end_time}'"
    
    sql = (f"INSERT INTO yyyp_lent (ID, weapon_name, item_name, weapon_float, float_range, price, lenter_name, "
            f"status, last_status, \"from\", lean_start_time, lean_end_time, total_Lease_Days, max_Lease_Days, data_user) "
            f"VALUES ('{ID}', '{weapon_name}', '{item_name}', {weapon_float_str}, '{float_range}', {price}, '{lent_user_name}',"
            f"'{status}', '{orderSubStatusName}', '{data_from}', '{lean_start_time}', {lean_end_time_str}, {totalLeaseDays}, {max_Lease_Days}, '{data_user}');")
    
    a_status = Date_base().insert(sql)
    
    if a_status is True:
        insert_status = "写入成功"
    elif a_status == '重复数据':
        insert_status = '重复数据'
    else:
        insert_status = '写入失败'
    
    return insert_status, 200
