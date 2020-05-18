from goods.models import GoodsCategory
from django.http import JsonResponse


def get_bread(category_id):
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
        cat = {
            'cat1': cat1,
            'cat2': cat2,
            'cat3': cat3,
        }
    return cat
