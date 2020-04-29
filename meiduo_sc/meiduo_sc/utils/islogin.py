# 判断用户时都登录的工具
from django.contrib.auth.decorators import login_required


class IsLoginMixin(object):

    @classmethod
    def as_view(cls, **kwargs):
        view = super().as_view(**kwargs)
        return login_required(view)
