from django.shortcuts import render
from django.views import View
from goods.models import GoodsCategory, GoodsChannel
from contents.models import ContentCategory
from meiduo_sc.utils.query_goods_category import query_goods


# Create your views here.
class IndexView(View):
    def get(self, request):
        categories = query_goods()
        # 获取渲染首页信息(广告)
        # contents:{
        #     类别1:[{广告1},...],
        #     类别2:[{广告1},...]
        # }
        content_category = ContentCategory.objects.all()
        contents = {}
        for kind in content_category:
            contents[kind.key] = kind.content_set.all()
        # print(contents)
        context = {
            'categories': categories,
            'contents': contents
        }

        return render(request, 'index.html',context)
