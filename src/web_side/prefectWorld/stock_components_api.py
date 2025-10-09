# -*- coding: utf-8 -*-
"""
完美世界库存组件数据API
用于接收爬虫采集的库存组件数据并写入数据库
"""

from flask import Blueprint, request, jsonify
import sys
sys.path.append('..')

from src.db_manager.steam import SteamStockComponentsModel

prefectWorldStockComponentsV1 = Blueprint('prefectWorldStockComponentsV1', __name__)


@prefectWorldStockComponentsV1.route('/batch', methods=['POST'])
def batch_insert_components():
    try:
        data = request.get_json()
        
        if not data or 'items' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少必要参数 items',
                'result': None
            }), 400
        
        items = data.get('items', [])
        
        if not isinstance(items, list):
            return jsonify({
                'code': 400,
                'message': 'items 必须是数组类型',
                'result': None
            }), 400
        
        if len(items) == 0:
            return jsonify({
                'code': 400,
                'message': 'items 不能为空',
                'result': None
            }), 400
        
        # 数据库字段映射 - 只保留数据库中存在的字段
        db_fields = set(SteamStockComponentsModel.get_fields().keys())
        
        # 统计信息
        total_count = len(items)
        success_count = 0
        failed_count = 0
        insert_count = 0
        update_count = 0
        failed_items = []
        
        print(f"📦 开始处理数据: 总数={total_count}")
        
        # 处理所有数据
        for item_index, item in enumerate(items):
            try:
                # 过滤出数据库中存在的字段
                filtered_item = {}
                for key, value in item.items():
                    if key in db_fields:
                        # 转换数据类型为字符串（数据库字段都是TEXT类型）
                        if value is not None:
                            filtered_item[key] = str(value)
                        else:
                            filtered_item[key] = None
                
                # 检查是否有主键 assetid
                if 'assetid' not in filtered_item or not filtered_item['assetid']:
                    failed_count += 1
                    failed_items.append({
                        'index': item_index,
                        'error': '缺少主键 assetid'
                    })
                    continue
                
                # 检查记录是否已存在
                assetid = filtered_item['assetid']
                existing_record = SteamStockComponentsModel.find_by_assetid(assetid)
                
                if existing_record:
                    # 如果记录已存在，更新记录
                    for key, value in filtered_item.items():
                        setattr(existing_record, key, value)
                    
                    if existing_record.save():
                        success_count += 1
                        update_count += 1
                    else:
                        failed_count += 1
                        failed_items.append({
                            'index': item_index,
                            'assetid': assetid,
                            'error': '更新记录失败'
                        })
                else:
                    # 创建新记录
                    new_record = SteamStockComponentsModel(**filtered_item)
                    
                    if new_record.save():
                        success_count += 1
                        insert_count += 1
                    else:
                        failed_count += 1
                        failed_items.append({
                            'index': item_index,
                            'assetid': assetid,
                            'error': '插入记录失败'
                        })
                
                # 每处理100条输出一次进度
                if (item_index + 1) % 100 == 0:
                    progress = ((item_index + 1) / total_count) * 100
                    print(f"📊 进度: {progress:.1f}% ({item_index + 1}/{total_count}) - 成功:{success_count}, 失败:{failed_count}")
                
            except Exception as e:
                failed_count += 1
                failed_items.append({
                    'index': item_index,
                    'error': str(e)
                })
        
        print(f"✅ 处理完成 - 总数:{total_count}, 成功:{success_count}, 失败:{failed_count}, 插入:{insert_count}, 更新:{update_count}")
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'result': {
                'total': total_count,
                'success': success_count,
                'failed': failed_count,
                'insert_count': insert_count,
                'update_count': update_count,
                'failed_items': failed_items[:20] if failed_items else []  # 最多返回20条失败记录
            }
        })
        
    except Exception as e:
        print(f"❌ 处理异常: {str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'result': None
        }), 500


@prefectWorldStockComponentsV1.route('/single', methods=['POST'])
def insert_single_component():
    """
    插入单条库存组件数据
    
    请求体格式:
    {
        "assetid": "29719329234",
        "classid": "41435",
        "data_user": "76561198334278515",
        "float_range": "崭新出厂",
        "instanceid": "45483288961",
        "item_name": "WOOD7（全息）",
        "weapon_float": "0.0",
        "weapon_level": "奇异",
        "weapon_name": "2023年巴黎锦标赛",
        "weapon_type": "印花"
    }
    
    返回:
    {
        "code": 0,
        "message": "success",
        "result": {
            "assetid": "29719329234"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 400,
                'message': '缺少请求数据',
                'result': None
            }), 400
        
        # 数据库字段映射 - 只保留数据库中存在的字段
        db_fields = set(SteamStockComponentsModel.get_fields().keys())
        
        # 过滤出数据库中存在的字段
        filtered_data = {}
        for key, value in data.items():
            if key in db_fields:
                # 转换数据类型为字符串（数据库字段都是TEXT类型）
                if value is not None:
                    filtered_data[key] = str(value)
                else:
                    filtered_data[key] = None
        
        # 检查是否有主键 assetid
        if 'assetid' not in filtered_data or not filtered_data['assetid']:
            return jsonify({
                'code': 400,
                'message': '缺少主键 assetid',
                'result': None
            }), 400
        
        # 检查记录是否已存在
        assetid = filtered_data['assetid']
        existing_record = SteamStockComponentsModel.find_by_assetid(assetid)
        
        if existing_record:
            # 如果记录已存在，更新记录
            for key, value in filtered_data.items():
                setattr(existing_record, key, value)
            
            if existing_record.save():
                return jsonify({
                    'code': 0,
                    'message': '记录更新成功',
                    'result': {
                        'assetid': assetid,
                        'action': 'update'
                    }
                })
            else:
                return jsonify({
                    'code': 500,
                    'message': '更新记录失败',
                    'result': None
                }), 500
        else:
            # 创建新记录
            new_record = SteamStockComponentsModel(**filtered_data)
            
            if new_record.save():
                return jsonify({
                    'code': 0,
                    'message': '记录插入成功',
                    'result': {
                        'assetid': assetid,
                        'action': 'insert'
                    }
                })
            else:
                return jsonify({
                    'code': 500,
                    'message': '插入记录失败',
                    'result': None
                }), 500
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'result': None
        }), 500


@prefectWorldStockComponentsV1.route('/delete/<assetid>', methods=['DELETE'])
def delete_component(assetid):
    """
    删除指定的库存组件记录
    
    返回:
    {
        "code": 0,
        "message": "success"
    }
    """
    try:
        record = SteamStockComponentsModel.find_by_assetid(assetid)
        
        if not record:
            return jsonify({
                'code': 404,
                'message': '记录不存在',
                'result': None
            }), 404
        
        if record.delete():
            return jsonify({
                'code': 0,
                'message': '删除成功',
                'result': None
            })
        else:
            return jsonify({
                'code': 500,
                'message': '删除失败',
                'result': None
            }), 500
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}',
            'result': None
        }), 500

