from flask import jsonify, request, Blueprint
from src.db_manager.yyyp.yyyp_weapon_classID import YyypWeaponClassIDModel

youpin898SelectWeaponV1 = Blueprint('youpin898SelectWeaponV1', __name__)

@youpin898SelectWeaponV1.route('/getWeaponList', methods=['GET'])
def getWeaponList():
    """获取所有武器列表"""
    try:
        records = YyypWeaponClassIDModel.find_all()
        data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
    except Exception as e:
        print(f"获取武器列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponById/<int:weapon_id>', methods=['GET'])
def getWeaponById(weapon_id):
    """根据ID获取武器信息"""
    try:
        record = YyypWeaponClassIDModel.find_by_id(Id=weapon_id)
        if record:
            return jsonify({
                'success': True,
                'data': record.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404
    except Exception as e:
        print(f"根据ID获取武器失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponByType/<weapon_type>', methods=['GET'])
def getWeaponByType(weapon_type):
    """根据武器类型获取武器列表"""
    try:
        records = YyypWeaponClassIDModel.find_by_weapon_info(weapon_type=weapon_type)
        data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
    except Exception as e:
        print(f"根据类型获取武器列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/searchWeapon', methods=['POST'])
def searchWeapon():
    """搜索武器(支持多条件查询)"""
    try:
        data = request.get_json()
        weapon_type = data.get('weapon_type')
        weapon_name = data.get('weapon_name')
        item_name = data.get('item_name')
        
        records = YyypWeaponClassIDModel.find_by_weapon_info(
            weapon_type=weapon_type,
            weapon_name=weapon_name,
            item_name=item_name
        )
        
        result_data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': result_data,
            'count': len(result_data)
        }), 200
    except Exception as e:
        print(f"搜索武器失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/batchInsertOrUpdate', methods=['POST'])
def batchInsertOrUpdate():
    """批量插入或更新武器数据"""
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({
                'success': False,
                'error': '无效的JSON数据，需要数组格式'
            }), 400
        
        success_count = YyypWeaponClassIDModel.batch_insert_or_update(data)
        
        return jsonify({
            'success': True,
            'message': f'成功处理 {success_count}/{len(data)} 条数据',
            'success_count': success_count,
            'total_count': len(data)
        }), 200
    except Exception as e:
        print(f"批量插入或更新武器数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/insertWeapon', methods=['POST'])
def insertWeapon():
    """插入单个武器数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '无效的JSON数据'
            }), 400
        
        # 检查是否已存在
        existing = YyypWeaponClassIDModel.find_by_id(Id=data.get('Id'))
        if existing:
            return jsonify({
                'success': False,
                'error': '武器ID已存在，请使用更新接口'
            }), 400
        
        # 创建新记录
        from datetime import datetime
        data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        weapon = YyypWeaponClassIDModel(**data)
        if weapon.save():
            return jsonify({
                'success': True,
                'message': '武器数据插入成功',
                'data': weapon.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据插入失败'
            }), 500
    except Exception as e:
        print(f"插入武器数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/updateWeapon/<int:weapon_id>', methods=['PUT'])
def updateWeapon(weapon_id):
    """更新武器数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '无效的JSON数据'
            }), 400
        
        # 查找记录
        weapon = YyypWeaponClassIDModel.find_by_id(Id=weapon_id)
        if not weapon:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404
        
        # 更新字段
        for key, value in data.items():
            if key != 'Id' and hasattr(weapon, key):
                setattr(weapon, key, value)
        
        # 更新时间戳
        from datetime import datetime
        weapon.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if weapon.save():
            return jsonify({
                'success': True,
                'message': '武器数据更新成功',
                'data': weapon.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据更新失败'
            }), 500
    except Exception as e:
        print(f"更新武器数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/deleteWeapon/<int:weapon_id>', methods=['DELETE'])
def deleteWeapon(weapon_id):
    """删除武器数据"""
    try:
        weapon = YyypWeaponClassIDModel.find_by_id(Id=weapon_id)
        if not weapon:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404
        
        if weapon.delete():
            return jsonify({
                'success': True,
                'message': '武器数据删除成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据删除失败'
            }), 500
    except Exception as e:
        print(f"删除武器数据失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@youpin898SelectWeaponV1.route('/getWeaponCount', methods=['GET'])
def getWeaponCount():
    """获取武器总数"""
    try:
        count = YyypWeaponClassIDModel.count()
        return jsonify({
            'success': True,
            'count': count
        }), 200
    except Exception as e:
        print(f"获取武器总数失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500

