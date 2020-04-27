from meiduo_sc.libs.yuntongxun.sms import CCP
from .contains import SMS_CODE_EXPIRE
from celery_tasks.main import celery_app


# 发送短信任务
@celery_app.task(bind=True, name='sms_send', retry_backoff=3)
def sms_send(self, mobile, sms_code):
    ccp = CCP()
    # # 成功返回0,不成功返回-1
    ccp.send_template_sms(mobile, [sms_code, SMS_CODE_EXPIRE/60], 1)
    # print(sms_code)
    # print(mobile)


