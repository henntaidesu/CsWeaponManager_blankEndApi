from flask import jsonify, request, Blueprint
from src.db_manager.index.weapon_classID import WeaponClassIDModel

buff163SelectWeaponV1 = Blueprint('buff163SelectWeaponV1', __name__)

@buff163SelectWeaponV1.route('/getWeaponList', methods=['GET'])
def getWeaponList():
    """获取所有武器列表"""
    try:
        records = WeaponClassIDModel.find_all()
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


@buff163SelectWeaponV1.route('/getWeaponByBuffId/<int:buff_id>', methods=['GET'])
def getWeaponByBuffId(buff_id):
    """根据BUFF ID获取武器信息"""
    try:
        records = WeaponClassIDModel.find_by_buff_id(buff_id)
        if records:
            return jsonify({
                'success': True,
                'data': records[0].to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404
    except Exception as e:
        print(f"根据BUFF ID获取武器失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@buff163SelectWeaponV1.route('/getWeaponByEnName/<en_weapon_name>', methods=['GET'])
def getWeaponByEnName(en_weapon_name):
    """根据英文武器名称获取武器列表"""
    try:
        records = WeaponClassIDModel.find_by_en_weapon_name(en_weapon_name)
        data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
    except Exception as e:
        print(f"根据英文武器名称获取武器列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@buff163SelectWeaponV1.route('/getWeaponByType/<weapon_type>', methods=['GET'])
def getWeaponByType(weapon_type):
    """根据武器类型获取武器列表"""
    try:
        records = WeaponClassIDModel.find_by_weapon_info(weapon_type=weapon_type)
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


@buff163SelectWeaponV1.route('/getWeaponByRarity/<rarity>', methods=['GET'])
def getWeaponByRarity(rarity):
    """根据稀有度获取武器列表"""
    try:
        records = WeaponClassIDModel.find_by_rarity(rarity)
        data = [record.to_dict() for record in records]
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        }), 200
    except Exception as e:
        print(f"根据稀有度获取武器列表失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@buff163SelectWeaponV1.route('/searchWeapon', methods=['POST'])
def searchWeapon():
    """搜索武器(支持多条件查询)"""
    try:
        data = request.get_json()
        weapon_type = data.get('weapon_type')
        weapon_name = data.get('weapon_name')
        item_name = data.get('item_name')

        records = WeaponClassIDModel.find_by_weapon_info(
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


@buff163SelectWeaponV1.route('/batchInsertOrUpdate', methods=['POST'])
def batchInsertOrUpdate():
    """
    批量更新BUFF武器数据（只更新buff_id字段）

    功能说明：
    - 通过 en_weapon_name (market_hash_name) 匹配已有记录
    - 只更新匹配到记录的 buff_id 字段，其他字段保持不变
    - 不会创建新的武器记录
    - 不会修改其他已有字段（如yyyp_id、weapon_name等）
    - 未匹配的BUFF数据会被跳过
    """
    try:
        data = request.get_json()
        if not data or not isinstance(data, list):
            return jsonify({
                'success': False,
                'error': '无效的JSON数据，需要数组格式'
            }), 400

        # 固定使用buff平台（只更新不插入）
        platform = 'buff'

        success_count = WeaponClassIDModel.batch_insert_or_update(data, platform=platform)

        return jsonify({
            'success': True,
            'message': f'成功处理 {success_count}/{len(data)} 条BUFF数据',
            'success_count': success_count,
            'total_count': len(data),
            'platform': platform
        }), 200
    except Exception as e:
        print(f"批量插入或更新BUFF武器数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@buff163SelectWeaponV1.route('/insertWeapon', methods=['POST'])
def insertWeapon():
    """插入单个BUFF武器数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '无效的JSON数据'
            }), 400

        # 固定使用buff平台
        platform = 'buff'

        # 兼容旧数据：如果传入的是'Id'字段，映射到buff_id
        if 'Id' in data and 'buff_id' not in data:
            data['buff_id'] = data.pop('Id')

        buff_id = data.get('buff_id')
        if not buff_id:
            return jsonify({
                'success': False,
                'error': '缺少buff_id字段'
            }), 400

        # 检查是否已存在
        existing_list = WeaponClassIDModel.find_by_buff_id(buff_id)

        if existing_list:
            return jsonify({
                'success': False,
                'error': f'武器buff_id已存在，请使用更新接口'
            }), 400

        # 创建新记录
        weapon = WeaponClassIDModel(**data)
        if weapon.save():
            return jsonify({
                'success': True,
                'message': 'BUFF武器数据插入成功',
                'data': weapon.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据插入失败'
            }), 500
    except Exception as e:
        print(f"插入BUFF武器数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@buff163SelectWeaponV1.route('/updateWeaponByBuffId/<int:buff_id>', methods=['PUT'])
def updateWeaponByBuffId(buff_id):
    """根据BUFF ID更新武器数据"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '无效的JSON数据'
            }), 400

        # 查找记录
        records = WeaponClassIDModel.find_by_buff_id(buff_id)
        if not records:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404

        weapon = records[0]

        # 更新字段
        for key, value in data.items():
            if key not in ['yyyp_id', 'buff_id', 'steam_id'] and hasattr(weapon, key):
                setattr(weapon, key, value)

        if weapon.save():
            return jsonify({
                'success': True,
                'message': 'BUFF武器数据更新成功',
                'data': weapon.to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据更新失败'
            }), 500
    except Exception as e:
        print(f"更新BUFF武器数据失败: {e}")
        import traceback
        print(f"详细错误信息: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@buff163SelectWeaponV1.route('/deleteWeaponByBuffId/<int:buff_id>', methods=['DELETE'])
def deleteWeaponByBuffId(buff_id):
    """根据BUFF ID删除武器数据"""
    try:
        records = WeaponClassIDModel.find_by_buff_id(buff_id)
        if not records:
            return jsonify({
                'success': False,
                'error': '武器不存在'
            }), 404

        weapon = records[0]
        if weapon.delete():
            return jsonify({
                'success': True,
                'message': 'BUFF武器数据删除成功'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '数据删除失败'
            }), 500
    except Exception as e:
        print(f"删除BUFF武器数据失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@buff163SelectWeaponV1.route('/getWeaponCount', methods=['GET'])
def getWeaponCount():
    """获取BUFF武器总数"""
    try:
        # 统计有buff_id的记录数
        all_records = WeaponClassIDModel.find_all()
        count = sum(1 for record in all_records if record.buff_id)
        return jsonify({
            'success': True,
            'count': count
        }), 200
    except Exception as e:
        print(f"获取BUFF武器总数失败: {e}")
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500
