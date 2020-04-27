from django.shortcuts import render
from django.views import View
from meiduo_sc.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from meiduo_sc.apps.verification_code.contains import IMG_CODE_EXPIRE,SMS_CODE_EXPIRE, SMS_CODE_FLAG
from django.http.response import HttpResponse,JsonResponse
from meiduo_sc.utils.response_code import RETCODE
from meiduo_sc.libs.yuntongxun.sms import CCP
from random import randint
from celery_tasks.sms.tasks import sms_send

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


# 处理短信验证的类视图
# 1.接收图形验证码
# url = this.host +'/sms_codes/' +this.mobile + '/?image_code=' + this.image_code + '&image_code_id=' + this.image_code_id;
# 2.获取redis中的图形验证码并验证
# 3.发送一个6位的短信验证码
class SmCapture(View):
    def get(self, request, mobile):
        image_code = request.GET.get('image_code')
        image_code_id = request.GET.get('image_code_id')

        print(image_code)
        print(image_code_id)

        conn = get_redis_connection('sms_code')
        flag = conn.get(mobile+'_flag')

        # 判断短信标志位
        if flag is not None:
            return JsonResponse({
                'code': RETCODE.SMSCODERR,
                'errmsg': '请在一分钟之后再请求发送验证码'
            })

        # 标志位--防止客户端频繁要求发送短信验证码
        conn.setex(mobile+'_flag', SMS_CODE_FLAG, 1)

        # 非空验证
        if not all([image_code, image_code_id]):
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '参数不完整'
            })

        #取redis中的图形验证码进行验证
        conn = get_redis_connection('img_code')
        image_code_redis = conn.get(image_code_id)

        print('image_code_redis的数据类型:',type(image_code_redis))
        print('image_code_redis:', image_code_redis)

        if image_code_redis is None:
            return JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图形验证码失效'
            })

        # redis中的图形验证码用完即删除
        conn.delete(image_code_id)

        # 取到值之后进行对比
        if image_code.lower() != image_code_redis.decode('utf8').lower():
            conn.delete(mobile + '_flag')
            return JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图形验证码不一致'
            })

        # 说明图形验证码成功,生成六位短信验证码
        sms_code = int(str(randint(0, 999999)).zfill(6))

        # 向客户端发送短信
        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_code, SMS_CODE_EXPIRE/60], 1)
        # result = sms_send.delay(mobile, sms_code)
        # print(result)

        # 将短信验证码存到redis
        conn = get_redis_connection('sms_code')
        conn.setex(mobile, SMS_CODE_EXPIRE, sms_code)

        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })
