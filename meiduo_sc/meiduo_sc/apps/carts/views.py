from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
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
    pass
