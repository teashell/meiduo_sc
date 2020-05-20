from django.conf.urls import url, include
from . import views

urlpatterns = [
    url('^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view()),
    url('^hot/(?P<category_id>\d+)/$', views.HotView.as_view()),
    url('^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view()),
    url('^detail/visit/(?P<category_id>\d+)/$', views.VisitView.as_view()),
    url('^browse_histories/$', views.HistoryView.as_view())
]
