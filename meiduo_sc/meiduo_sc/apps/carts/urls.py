from django.conf.urls import url
from . import views

urlpatterns = [
    url('^carts/$', views.add_carts.as_view())
]