from django.core.mail import send_mail
from django.conf import settings
from celery_tasks.main import celery_app


@celery_app.task(bind=True, name='check_email', retry_backoff=3)
def check_email(self, email, verify_url):
    subject = '美多商城邮箱验证'
    html = '<p>尊敬的用户您好！</p>' \
           '<p>感谢您使用美多商城。</p>' \
           '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
           '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
    try:
        send_mail(subject,
                  '',
                  settings.EMAIL_FROM,
                  [email],
                  html_message=html)
    except Exception as e:
        print(e)
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)
