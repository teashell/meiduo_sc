from django.shortcuts import render
from django.views import View
from meiduo_sc.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from meiduo_sc.apps.verification_code.contains import IMG_CODE_EXPIRE
from django.http.response import HttpResponse


# Create your views here.
class Capture(View):
    def get(self, request, uuid):
        # 调用第三方生成器生成验证码
        name, code, img = captcha.generate_captcha()
        # 对验证码进行缓存
        conn = get_redis_connection('img_code')
        conn.setex(uuid, IMG_CODE_EXPIRE, code)
        # 返回图片
        return HttpResponse(img, content_type='image/jpg')

