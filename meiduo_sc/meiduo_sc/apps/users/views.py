from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.views import View
import re
from . import models
from django.contrib.auth import login
from meiduo_sc.utils.response_code import RETCODE


# Create your views here.
class RegisterView(View):
    # 注册请求页面
    def get(self, request):
        return render(request, 'register.html')

    # 注册提交
    def post(self,request):
        # 获取所有的参数
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        mobile = request.POST.get('phone')
        auth_code = request.POST.get('pic_code')

        # 验证参数是否为空
        if not all([username, password2, password, mobile, auth_code]):
            return HttpResponseForbidden('缺少重要参数')

        # 验证参数是否有效
        if not re.match('^[a-zA-Z0-9_-]{5,20}$', username):
            return HttpResponseForbidden('请输入正确的用户名')

        # 验证用户名是否重名
        if models.User.objects.filter(username=username).count() > 0:
            return HttpResponseForbidden('用户名已存在')

        # 验证密码有效
        if not re.match('^[0-9A-Za-z]{8,20}$', password):
            return HttpResponseForbidden('密码格式不正确')

        # 验证密码与确认码是否一致
        if not (password == password2):
            return HttpResponseForbidden('两次输入的密码不同')

        # 验证手机号是否有效
        if not re.match('^1[345789]\d{9}$', mobile):
            return HttpResponseForbidden('手机号码无效')

        # 验证手机号码是否重复
        if models.User.objects.filter(mobile=mobile).count() > 0:
            return HttpResponseForbidden('手机号码重复')

        # 处理1---创建用户对象
        user = models.User.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )

        # 处理2---状态持久化
        login(request, user)

        # 随便返回一点123
        return HttpResponse(123)


# 用来处理前端的ajax用户名的重复验证的类视图
class UserTesting(View):
    # 接收
    # 验证
    # 处理---验证是否重复
    def get(self, request, username):
        count = models.User.objects.filter(username=username).count()
        # 返回一个json格式的数据
        return JsonResponse({
            'count': count,
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })


class PhoneTesting(View):
    def get(self, request, mobile):
        count = models.User.objects.filter(mobile=mobile).count()
        return JsonResponse({
            'count': count,
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })
