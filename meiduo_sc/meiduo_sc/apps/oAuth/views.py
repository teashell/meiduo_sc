from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from meiduo_sc.utils.response_code import RETCODE
from .models import OAuthQQUser
from django.contrib.auth import login
from meiduo_sc.utils import myJWS
from .constans import TOKEN_EXPIRE
from users.models import User


# Create your views here.
class ToQQView(View):

    def get(self, request):
        next_url = request.GET.get('next')
        oauth = OAuthQQ(
            settings.QQ_CLIENT_ID,
            settings.QQ_CLIENT_SECRET,
            settings.QQ_REDIRECT_URI,
            next_url
        )
        login_url = oauth.get_qq_url()
        return JsonResponse({
            'code': RETCODE.OK,
            'err_msg': 'OK',
            'login_url': login_url
        })


# 扫码后登录的类视图
class QQLoginView(View):

    def get(self, request):
        state = request.GET.get('state', '/')
        oauth = OAuthQQ(
            settings.QQ_CLIENT_ID,
            settings.QQ_CLIENT_SECRET,
            settings.QQ_REDIRECT_URI,
            state
        )
        code = request.GET.get('code')
        # 获取Access Token
        access_token = oauth.get_access_token(code)
        # 获取openid
        openid = oauth.get_open_id(access_token)
        # 判断是否首次用qq登录
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except:
            # 初次登录
            encryption_openid = myJWS.dumps(openid)
            context = {
                'token':encryption_openid
            }
            return render(request, 'oauth_callback.html', context)
        else:
            user = qquser.user
            # 状态保持
            login(request, user)
            response = redirect(state)
            response.set_cookie('username', user.username)
            return response

        # return HttpResponse(openid)

    def post(self, request):
        mobile = request.POST.get('mobile')
        password = request.POST.get('pwd')
        openid = request.POST.get('access_token')
        state = request.GET.get('state', '/')
        # 解密
        obj= myJWS.loads(openid)
        if not obj:
            return HttpResponseForbidden('秘钥过期,请重新绑定QQ')
        try:
            user = User.objects.get(mobile=mobile)
        except:
            user = User.objects.create_user(mobile, password=password, mobile=mobile)
        else:
            if not user.check_password(password):
                return HttpResponseForbidden('手机号已被注册或者密码错误')
        # 绑定用户
        qquser = OAuthQQUser.objects.create(
            user=user,
            openid=obj
        )
        # 状态保持
        login(request, user)
        response = redirect(state)
        response.set_cookie('username', user.username)

        return response


