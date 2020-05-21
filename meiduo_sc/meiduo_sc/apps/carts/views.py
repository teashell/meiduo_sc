from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse, response
from meiduo_sc.utils.response_code import RETCODE
from goods.models import SKU
from meiduo_sc.utils.my_pickle_json import dumps, loads
from . import constans
from django_redis import get_redis_connection


# Create your views here.
class add_carts(View):
    def post(self, request):
        # 接收
        sku_id = json.loads(request.body.decode()).get('sku_id')
        count = json.loads(request.body.decode()).get('count')
        selected = json.loads(request.body.decode()).get('selected')
        # 验证
        if not all([sku_id, count]):
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '某些参数值无效'
            })
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': 'sku_id无效'
            })
        if count > 5:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': 'count值过大,批量进货请联系厂家'
            })
        elif count < 0:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': 'count值不能小于0'
            })
        elif count > sku.stock:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '库存不够啦!!!'
            })
        # 处理
        # 判断是否登录,如果登录用redis,否则用cookie
        if request.user.is_authenticated:
            conn = get_redis_connection('carts')
            # 将sku_id和count存到hash中
            conn.hset(f'carts_{request.user.id}', sku_id, count)
            # 将是否选中存到set中
            conn.sadd(f'selected_{request.user.id}', sku_id)
            return JsonResponse({
                'code': RETCODE.OK,
                'errmsg': 'OK'
            })
        else:
            carts = request.COOKIES.get('carts')
            if carts:
                carts = loads(carts)
                carts[sku_id] = {
                    'sku_id': sku_id,
                    'count': count,
                    'selected': 1
                }
            else:
                carts = {}
                carts[sku_id] = {
                    'sku_id': sku_id,
                    'count': count,
                    'selected': 1
                }
            carts_json = dumps(carts)
            response = JsonResponse({
                'code': RETCODE.OK,
                'errmsg': 'OK'
            })
            response.set_cookie('carts', carts_json, max_age=constans.CARTS_DATA_EXPIRE)
            # 响应
            return response
        pass

    def get(self, request):
        if not request.user.is_authenticated:
            cookies = request.COOKIES.get('carts')
            print('cookies', cookies)
            if not cookies:
                carts = {}
                is_selected_list = []
            else:
                origin_carts = loads(cookies)
                print('origin_carts', origin_carts)
                carts = {}
                is_selected_list = []
                for key, value in origin_carts.items():
                    sku_id = value['sku_id']
                    count = value['count']
                    carts[sku_id] = count
                    if value['selected'] == 1:
                        is_selected_list.append(value['sku_id'])
                print('carts', carts)
                print('is_selected_list', is_selected_list)
        else:
            # 获取买过的商品id和数量
            conn = get_redis_connection('carts')
            carts_bytes = conn.hgetall(f'carts_{request.user.id}')
            carts = {int(sku_id): int(count) for sku_id, count in carts_bytes.items()}
            print('carts', carts)
            # 获取选中的状态
            is_selected_bytes = conn.smembers(f'selected_{request.user.id}')
            print('is_selected', is_selected_bytes)
            is_selected_list = [int(is_selected) for is_selected in is_selected_bytes]
            print('is_selected_list', is_selected_list)
        cart_skus = []
        for cart in carts.items():
            sku_id, count = cart
            sku = SKU.objects.get(pk=sku_id)
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': count,
                'price': str(sku.price),
                'selected': str(sku_id in is_selected_list),
                'total_amount': str(count * sku.price)
            })
        print('cart_skus', cart_skus)
        context = {
            'cart_skus':cart_skus
        }
        return render(request, 'cart.html', context)

    def put(self, request):
        # 接收
        sku_id = json.loads(request.body.decode()).get('sku_id')
        count = json.loads(request.body.decode()).get('count')
        selected = json.loads(request.body.decode()).get('selected')
        print('sku_id', sku_id)
        print('count', count)
        print('selected', selected)
        # 验证
        if not all([sku_id, count]):
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '某些参数值无效'
            })
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': 'sku_id无效'
            })
        if count > 5:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': 'count值过大,批量进货请联系厂家'
            })
        elif count < 0:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': 'count值不能小于0'
            })
        elif count > sku.stock:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '库存不够啦!!!'
            })
        # 响应
        response = JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'cart_sku': {
                'sku_id': sku_id,
                'count': count,
                'selected': selected,
                'id': sku.id,
                'name': sku.name,
                'price': str(sku.price),
                'total_amount': str(count * sku.price)
            }
        })
        # 处理
        if request.user.is_authenticated:
            # 已经登录用redis数据
            conn = get_redis_connection('carts')
            conn.hset(f'carts_{request.user.id}', sku_id, count)
            if selected == False:
                conn.srem(f'selected_{request.user.id}', sku_id)
            else:
                conn.sadd(f'selected_{request.user.id}', sku_id)
        else:
            carts = request.COOKIES.get('carts')
            print('carts_bytes', carts)
            if carts:
                carts = loads(carts)
                carts[sku_id] = {
                    'sku_id': sku.id,
                    'count': count,
                    'selected': selected
                }
            else:
                carts = {}
                carts[sku_id] = {
                    'sku_id': sku.id,
                    'count': count,
                    'selected': selected
                }
            carts_json = dumps(carts)
            response.set_cookie('carts', carts_json, max_age=constans.CARTS_DATA_EXPIRE)
            pass
        return response
        pass

    def delete(self, request):
        sku_id = json.loads(request.body.decode()).get('sku_id')
        # 验证
        if not all([sku_id]):
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '必要参数sku_id不存在'
            })
        try:
            sku = SKU.objects.get(pk=sku_id)
        except:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': 'sku_id无效'
            })
        response = JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })
        # 处理
        if request.user.is_authenticated:
            conn = get_redis_connection('carts')
            conn.hdel(f'carts_{request.user.id}', sku_id)
            conn.srem(f'selected_{request.user.id}', sku_id)
        else:
            carts_bytes = request.COOKIES.get('carts')
            if carts_bytes:
                carts = loads(carts_bytes)
            else:
                carts = {}
            if sku_id in carts.keys():
                carts.pop(sku_id)
            carts_json = dumps(carts)
            response.set_cookie('carts', carts_json, expires=constans.CARTS_DATA_EXPIRE)
        # 响应
        return response
        pass
