from django.conf.urls import url
from . import views

urlpatterns = [
    url('^qq/login/$', views.ToQQView.as_view()),
    url('^oauth_callback', views.QQLoginView.as_view())
]