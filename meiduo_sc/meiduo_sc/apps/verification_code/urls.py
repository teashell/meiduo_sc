from django.urls import path
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url('^image_codes/(?P<uuid>[\w-]+)/$', views.Capture.as_view()),
    url('^sms_codes/(?P<mobile>1[345789]\d{9})/$', views.SmCapture.as_view())
]
