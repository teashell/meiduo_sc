from django.shortcuts import render
from django.views import View
from .models import Area
from django.http.response import JsonResponse
from meiduo_sc.utils.response_code import RETCODE
from django.core.cache import cache
from .constans import PROVIENCE_CACHCE_EXPIRE,CITY_CACHE_EXPIRE


# Create your views here.
class ProvinceView(View):
    def get(self, request):
        area_id = request.GET.get('area_id')
        if not area_id:
            # 表示请求省份的数据
            # 判断是否有缓存
            result = cache.get('province')
            if result:
                return JsonResponse(result)
            province_obj = Area.objects.filter(parent__isnull=True)
            province_list = []
            for province in province_obj:
                province_list.append({
                    'id': province.id,
                    'name': province.name
                })
            result = {
                'code': RETCODE.OK,
                'errmsg': 'OK',
                'province_list': province_list
            }
            # 缓存一下
            cache.set('province', result, PROVIENCE_CACHCE_EXPIRE)
            return JsonResponse(result)
        else:
            # 获取缓存数据
            result = cache.get(area_id)
            if result:
                return JsonResponse(result)
            # 表示请求市,区县的数据
            try:
                area = Area.objects.get(pk=area_id)
            except:
                return JsonResponse({
                    'code': RETCODE.PARAMERR,
                    'errmsg': '请求地区无效'
                })
            else:
                sub_area_set = area.subs.all()
                sub_area_list = []
                for sub_area in sub_area_set:
                    sub_area_list.append({
                        'id': sub_area.id,
                        'name': sub_area.name
                    })
                result = {
                    'code': RETCODE.OK,
                    'errmsg': 'OK',
                    'sub_data': {
                        'id': area.id,
                        'name': area.name,
                        'subs': sub_area_list
                    }
                }
                # 缓存市县区数据
                cache.set(area_id, result, CITY_CACHE_EXPIRE)
                return JsonResponse(result)

