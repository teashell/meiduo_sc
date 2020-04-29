from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from meiduo_sc.utils.response_code import RETCODE


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
        oauth = OAuthQQ(
            settings.QQ_CLIENT_ID,
            settings.QQ_CLIENT_SECRET,
            settings.QQ_REDIRECT_URI,
            request.GET.get('next')
        )
        code = request.GET.get('code')
        # 获取Access Token
        access_token = oauth.get_access_token(code)
        # 获取openid
        openid = oauth.get_open_id(access_token)
        return HttpResponse(openid)
