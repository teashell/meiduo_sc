from django.shortcuts import render
from django.views import View
from meiduo_sc.utils.query_goods_category import query_goods
from .models import GoodsCategory
from django.http.response import JsonResponse, HttpResponseForbidden
from .models import SKU, SPUSpecification, GoodsVisitCount
from django.core.paginator import Paginator
from .constans import NUM_PER_PAGE
from meiduo_sc.utils.response_code import RETCODE
from meiduo_sc.utils.breadcrumb import get_bread


# Create your views here.
class ListView(View):
    def get(self, request, category_id, page_num):
        # 查询分类数据
        categories = query_goods()
        # 面包屑导航
        cat = get_bread(category_id)
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
            'cat': cat,
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


class DetailView(View):
    def get(self, request, sku_id):
        # 获取所有商品分类
        categories = query_goods()
        # 面包屑导航
        sku = SKU.objects.get(pk=sku_id)
        category_id = sku.category_id
        cat = get_bread(category_id)
        # 获取spu
        spu = sku.spu
        # 获取所有商品
        skus = spu.sku_set.order_by('id')
        print('skus', skus)
        # 获取spu的总的规格信息
        specs = spu.specs.order_by('id')
        print('specs', specs)
        # 构造字典并返回信息
        skus_option = {}
        # 当前商品的信息列表
        current_sku = []
        '''
        sku_option={
            (选项1, 选项2):商品id
        }
        '''
        i = 0
        for sku1 in skus:
            i += 1
            # 所有指向该sku的商品的具体的规格选项
            options = sku1.specs.order_by('spec_id')
            sku_option = []
            for option in options:
                sku_option.append(option.option_id)
                # 获取当前商品的配置信息
                if sku.id == sku1.id:
                    current_sku.append(option.option_id)
            print(f'sku_option{i}', sku_option)
            print(current_sku)
            skus_option[tuple(sku_option)] = sku1.id
        print('skus_option', skus_option)
        # 遍历当前的商品的所有的spu的规格(例：遍历[颜色, 内存])
        specs_list = []
        for index, spec in enumerate(specs):
            option_list = []
            for option in spec.options.all():
                # 将当前文件的配置信息暂存
                sku_option_temp = current_sku[:]
                # 替换对应索引的元素:规格的索引是固定的
                sku_option_temp[index] = option.id
                #为选项添加sku_id用来指引跳转的对象
                option.sku_id = skus_option.get(tuple(sku_option_temp), 0)
                # 添加选项对象
                option_list.append(option)
            # 为规格对象添加选项列表
            spec.option_list = option_list
            # 重新构造规格数据
            specs_list.append(spec)
        context = {
            'cat': cat,
            'category_id': category_id,
            'sku':sku,
            'categories': categories,
            'spu': spu,
            'specs': specs,
            'specs_list': specs_list
        }
        return render(request, 'detail.html', context)
    pass


class VisitView(View):
    def post(self, request, category_id):
        try:
            goods_count = GoodsVisitCount.objects.get(category_id=category_id)
        except:
            GoodsVisitCount.objects.create(
                category_id=category_id,
                count=1,
            )
        else:
            goods_count.count += 1
            goods_count.save()
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })
    pass
