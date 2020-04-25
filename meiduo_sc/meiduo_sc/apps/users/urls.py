from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view()),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UserTesting.as_view()),
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/', views.PhoneTesting.as_view())
]
