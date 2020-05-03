from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view()),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UserTesting.as_view()),
    url(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/', views.PhoneTesting.as_view()),
    url(r'^login/', views.LoginView.as_view()),
    url(r'^logout/', views.LogoutView.as_view()),
    url(r'^info/$', views.UsercenterView.as_view()),
    url(r'^emails/$', views.CheckEmailView.as_view()),
    url(r'^emails/verification/$', views.ActiveEmailView.as_view()),
    url(r'^addresses/$', views.ShowAddress.as_view()),
    url(r'^addresses/create/$', views.CreateAddress.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/$', views.EditAddress.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddress.as_view()),
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.TitleAddress.as_view()),
    url(r'^password/$', views.ChangePasswordView.as_view())
]
