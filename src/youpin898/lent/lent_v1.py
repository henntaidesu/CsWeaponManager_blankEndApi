from flask import jsonify, request, Blueprint
from src.log import Log
from src.execution_db import Date_base
from src.now_time import today
import requests

youpin898LentV1 = Blueprint('youpin898LentV1', __name__)

@youpin898LentV1.route('/getNowLentingList', methods=['get'])
def getNowLentingList():
    sql = "SELECT ID FROM yyyp_lent WHERE status NOT IN ('完成')"
    flag, data = Date_base().select(sql)
    if flag:
        return jsonify(data), 200
    else:
        return "查询失败", 500  

@youpin898LentV1.route('/getTimeOutLent', methods=['get'])
def getTimeOutLent():
    sql = f"SELECT ID FROM yyyp_lent WHERE lean_end_time < '{today()}' and status IN ('白玩中', '归还中', '租赁中')"
    flag, data = Date_base().select(sql)
    return jsonify(data), 200

@youpin898LentV1.route('/updateLentData', methods=['post'])
def updateLentData():
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
    data = request.get_json()
    ID = data['ID']
    weapon_name = data['weapon_name']
    item_name = data['item_name']
    weapon_float = data['weapon_float']
    float_range = data['float_range']
    price = data['price']
    lent_user_name = data['buyer_user_name']
    status = data['status']
    orderSubStatusName = data['orderSubStatusName']
    data_from = data['from']
    lean_start_time = data['lean_start_time']
    lean_end_time = data['lean_end_time']
    totalLeaseDays = int(data['totalLeaseDays'])
    max_Lease_Days = int(data['leaseMaxDays'])
    sql = (f"INSERT INTO yyyp_lent (ID, weapon_name, item_name, weapon_float, float_range, price, lenter_name, "
            f"status, last_status, \"from\", lean_start_time, lean_end_time, total_Lease_Days, max_Lease_Days) "
            f"VALUES ('{ID}', '{weapon_name}', '{item_name}', {weapon_float}, '{float_range}', {price}, '{lent_user_name}',"
            f"'{status}', '{orderSubStatusName}', '{data_from}', '{lean_start_time}', '{lean_end_time}', {totalLeaseDays}, {max_Lease_Days});")
    a_status = Date_base().insert(sql)
    
    if a_status is True:
        insert_status = "写入成功"
    elif a_status == '重复数据':
        insert_status = '重复数据'
    else:
        insert_status = '写入失败'
    return insert_status, 200

