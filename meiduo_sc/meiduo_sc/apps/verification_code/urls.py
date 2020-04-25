from django.urls import path
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url('^image_codes/(?P<uuid>[\w-]+)/$', views.Capture.as_view())
]
