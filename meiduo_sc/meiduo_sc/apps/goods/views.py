from django.shortcuts import render
from django.views import View
from meiduo_sc.utils.query_goods_category import query_goods
from .models import GoodsCategory
from django.http.response import JsonResponse
from .models import SKU
from django.core.paginator import Paginator
from .constans import NUM_PER_PAGE
from meiduo_sc.utils.response_code import RETCODE


# Create your views here.
class ListView(View):
    def get(self, request, category_id, page_num):
        # 查询分类数据
        categories = query_goods()
        try:
            cat3 = GoodsCategory.objects.get(pk=category_id)
        except:
            print('pk不存在')
            return JsonResponse({
                'code': 10000,
                'errmsg': 'id不存在'
            })
        else:
            cat2 = cat3.parent
            cat1 = cat2.parent
            # 排序规则
            sort = request.GET.get('sort', 'default')
            if sort == 'default':
                sort_filed = '-sales'
            elif sort == 'price':
                sort_filed = '-price'
            else:
                sort_filed = '-comments'
            # 具体商品
            # 1.获取
            skus = SKU.objects.filter(category_id=category_id, is_launched=1).order_by(sort_filed)
            # print(skus)
            # 2.分页
            paginator = Paginator(skus, NUM_PER_PAGE)
            # 获取某一页的商品对象
            page_skus = paginator.page(page_num)
            # 一共分了多少页
            total_page = paginator.num_pages
            print('page_skus', page_skus)
            print('total_page', total_page)
            context = {
                'categories': categories,
                'category_id': category_id,
                'cat1': cat1,
                'cat2': cat2,
                'cat3': cat3,
                'current_page': page_num,
                'page_skus': page_skus,
                'total_page': total_page,
                'sort': sort
            }

            return render(request, 'list.html', context)


class HotView(View):
    def get(self, request, category_id):
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[0:2]
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': '/static/images/goods/goods001.jpg',
                'price': sku.price
            })
        print(hot_skus)
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'hot_skus': hot_skus,
        })
    pass
