from goods.models import GoodsChannel


def query_goods():
    # 查询所有的频道数据
    channels = GoodsChannel.objects.order_by('group_id')
    categories = {}
    for channel in channels:
        if channel.group_id not in categories:
            categories[channel.group_id] = {
                'cat': [],
                'sub_cat': []
            }
        # 添加一级分类
        categories[channel.group_id]['cat'].append({
            'name': channel.category.name,
            'url': channel.url
        })
        # 添加二级分类和三级分类
        for sub2 in channel.category.subs.all():
            # print(sub2)
            # print(type(sub2))
            sub2.sub_cat = sub2.subs.all()
            categories[channel.group_id]['sub_cat'].append(sub2)
    return categories
