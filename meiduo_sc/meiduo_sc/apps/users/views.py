from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import re
from . import models
from django.contrib.auth import login,logout
from django.contrib.auth import authenticate
from meiduo_sc.utils.response_code import RETCODE
from django_redis import get_redis_connection
from .constants import USER_COOKIE_EXPIRE
from meiduo_sc.utils.islogin import IsLoginMixin


# Create your views here.
class RegisterView(View):
    # 注册请求页面
    def get(self, request):
        return render(request, 'register.html')

    # 注册提交
    def post(self,request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        mobile = request.POST.get('phone')
        sms_code = request.POST.get('msg_code')

        # 验证参数是否为空
        if not all([username, password2, password, mobile, sms_code]):
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

        # 验证短信验证码是否正确
        conn = get_redis_connection('sms_code')
        sms_code_redis = conn.get(mobile).decode('utf8')
        if sms_code != sms_code_redis:
            conn.delete(mobile+'_flag')
            return HttpResponseForbidden('短信验证码错误')
        conn.delete(mobile)

        # 处理1---创建用户对象
        user = models.User.objects.create_user(
            username=username,
            password=password,
            mobile=mobile
        )

        # 处理2---状态持久化
        login(request, user)

        # 随便返回一点123
        return redirect('/')


# 用来处理前端的ajax用户名的重复验证的类视图
class UserTesting(View):
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


# 处理登录的类视图
class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    # 登录
    def post(self, request):
        # 获取用户,密码
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        next_url = request.GET.get('next')

        user = authenticate(request, username=username, password=password)
        if user is None:
            return HttpResponseForbidden('用户名或者密码错误或者用户不存在')
        else:
            # 状态保持
            login(request, user)

            if next_url:
                response = redirect(next_url)
            else:
                response = redirect('/')
            # 设置cookie值
            response.set_cookie('username', username, USER_COOKIE_EXPIRE)
            return response


# 处理登出的类视图
class LogoutView(View):

    def get(self, request):
        # 服务端退出
        logout(request)
        # 删除客户端cookie,彻底退出
        response = redirect('/')
        response.delete_cookie('username')
        return response


# 处理用户中心的类视图
class UsercenterView(IsLoginMixin, View):

    def get(self, request):
        # 验证是否登录
        # if request.user.is_authenticated:
        #     return render(request, 'user_center_info.html')
        # else:
        #     return redirect('/login/')
        return render(request, 'user_center_info.html')
