from django.conf.urls import url
from . import views

urlpatterns = [
    url('^areas/$', views.ProvinceView.as_view())
]
