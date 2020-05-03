from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
import re
from . import models
from django.contrib.auth import login,logout
from django.contrib.auth import authenticate
from meiduo_sc.utils.response_code import RETCODE
from django_redis import get_redis_connection
from .constants import USER_COOKIE_EXPIRE,USERNAME_COOKIE_EXPIRE
from meiduo_sc.utils.islogin import IsLoginMixin
import json
from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.checked_email.tasks import check_email
from meiduo_sc.utils import myJWS
from users.models import User, Address


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
        response = redirect('/')
        response.set_cookie('username', user.username, USERNAME_COOKIE_EXPIRE)
        return response


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


# 处理邮箱验证
class CheckEmailView(IsLoginMixin, View):

    def put(self, request):
        email = json.loads(request.body.decode())['email']
        print(email)
        print(type(email))
        # return JsonResponse({
        #     'code': RETCODE.OK,
        #     'errmsg': '验证成功'
        # })
        # 验证邮箱格式以及是否存在
        if not all([email]):
            return JsonResponse({
                'code': RETCODE.EMAILERR,
                'errmsg': '未输入邮箱'
            })
        if not re.match('[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', email):
            return JsonResponse({
                'code': RETCODE.EMAILERR,
                'errmsg': '邮箱格式错误'
            })
        # 处理
        user = request.user
        user.email = email
        user.save()

        # 生成加密的邮箱链接地址
        obj = {'user_id': user.id, 'email': user.email}
        json_str = myJWS.dumps(obj)
        verify_url =settings.EMAIL_VERIFY_URL + '?token=' + json_str


        # 发送验证邮件
        # subject = '美多商城邮箱验证'
        # verify_url = settings.EMAIL_VERIFY_URL
        # html = '<p>尊敬的用户您好！</p>' \
        #            '<p>感谢您使用美多商城。</p>' \
        #            '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #            '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        # send_mail(subject,
        #           '',
        #           settings.EMAIL_FROM,
        #           [email],
        #           html_message=html)

        # 异步调用
        check_email.delay(email, verify_url)

        # 响应
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })


# 邮件激活
class ActiveEmailView(View):

    def get(self, request):
        token = request.GET.get('token')
        # 验证token是否存在
        if not all([token]):
            return HttpResponseForbidden('token不存在')
        # 验证token是否有效
        token = myJWS.loads(token)
        if not token:
            return HttpResponseForbidden('token无效')
        user_id = token.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except:
            return HttpResponseForbidden('用户不存在')
        else:
            user.email_active = True
            user.save()
            return redirect('/info/')


# 地址页面展示
class ShowAddress(IsLoginMixin, View):

    def get(self, request):
        # 查询数据库收货地址
        address_set = request.user.addresses.all()
        # print(address_set)
        # print(type(address_set))
        address_list = []
        for address in address_set:
            if address.is_deleted == True:
                continue
            address_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        context = {
            'addresses': address_list,
        }
        return render(request, 'user_center_site.html', context)


# 创建收货地址
class CreateAddress(IsLoginMixin, View):
    def post(self, request):
        # 接收
        params = json.loads(request.body.decode('utf8'))
        # print(params)
        # print(type(params))
        title = params.get('title')
        receiver = params.get('receiver')
        province_id = params.get('province_id')
        city_id = params.get('city_id')
        district_id = params.get('district_id')
        place = params.get('place')
        mobile = params.get('mobile')
        tel = params.get('tel')
        email = params.get('email')
        # 验证
        if not all([title, receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '参数错误'
            })
        # 验证手机号的格式
        if not re.match('^1[3-9]\d{9}$', mobile):
            return JsonResponse({
                'code': RETCODE.MOBILEERR,
                'errmsg': '电话号码格式错误'
            })
        # 处理
        address = Address.objects.create(
            receiver=receiver,
            place=place,
            mobile=mobile,
            tel=tel,
            email=email,
            city_id=city_id,
            province_id=province_id,
            district_id=district_id,
            user=request.user
        )
        # 响应
        address_dict = {
            'id': address.id,
            'title': address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            'province_id': address.province_id,
            "city": address.city.name,
            "city_id": address.city_id,
            "district": address.district.name,
            "district_id": address.district_id,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'address':address_dict
        })
    pass


class EditAddress(IsLoginMixin, View):
    def put(self, request, address_id):
        # 接收
        params = json.loads(request.body.decode('utf8'))
        # print(params)
        # print(type(params))
        title = params.get('title')
        receiver = params.get('receiver')
        province_id = params.get('province_id')
        city_id = params.get('city_id')
        district_id = params.get('district_id')
        place = params.get('place')
        mobile = params.get('mobile')
        tel = params.get('tel')
        email = params.get('email')
        # 验证
        if not all([title, receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '参数错误'
            })
        if not re.match('^1[3-9]\d{9}$', mobile):
            return JsonResponse({
                'code': RETCODE.MOBILEERR,
                'errmsg': '电话号码格式错误'
            })
        # 处理
        Address.objects.filter(id=address_id).update(
            receiver = receiver,
            place = place,
            mobile = mobile,
            tel = tel,
            email = email,
            city_id = city_id,
            province_id = province_id,
            district_id = district_id,
            user = request.user
        )
        address = Address.objects.get(id=address_id)
        # 响应
        address_dict = {
            'id': address.id,
            'title': address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'address': address_dict
        })
        pass

    def delete(self, request, address_id):
        address = Address.objects.get(id=address_id)
        print(address_id)
        print(address)
        print(type(address))
        address.is_deleted = True
        address.save()
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })
    pass


# 修改默认地址
class DefaultAddress(IsLoginMixin, View):
    def put(self, request, address_id):
        user = request.user
        user.default_address_id = address_id
        user.save()
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })
        pass
    pass


# 修改地址标题
class TitleAddress(IsLoginMixin, View):
    def put(self, request, address_id):
        # 接收
        title = json.loads(request.body.decode('utf-8')).get('title')
        # 验证
        if not all([title]):
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': '没有title'
            })
        if Address.objects.filter(user_id=request.user.id, title=title, is_deleted=False).count() > 0:
            return JsonResponse({
                'code': RETCODE.PARAMERR,
                'errmsg': 'title已经存在'
            })
        # 处理
        address = Address.objects.get(id=address_id)
        address.title = title
        address.save()
        # 响应
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK'
        })
    pass


# 修改密码
class ChangePasswordView(IsLoginMixin, View):
    def get(self, request):
        return render(request, 'user_center_pass.html')

    def post(self, request):
        # 接收
        old_password = request.POST.get('old_pwd')
        new_password = request.POST.get('new_pwd')
        new_password2 = request.POST.get('new_cpwd')
        # 验证
        if not all([old_password, new_password, new_password2]):
            return HttpResponseForbidden('缺少的必要的参数')
        if not request.user.check_password(old_password):
            return HttpResponseForbidden('旧密码错误')
        if not re.match('^[0-9A-Za-z]{8,20}$', new_password):
            return HttpResponseForbidden('新密码格式长度有问题')
        if not new_password == new_password2:
            return HttpResponseForbidden('两个新密码不相同')
        # 处理
        request.user.set_password(new_password)
        request.user.save()
        # 响应
        logout(request)
        response = redirect('/login/')
        response.delete_cookie('username')
        return response
    pass
