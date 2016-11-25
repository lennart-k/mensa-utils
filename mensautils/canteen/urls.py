from django.conf.urls import url

from mensautils.canteen import views

app_name = 'mensautils.canteen'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stats/$', views.stats, name='stats'),
    url(r'^rate/(\d+)/$', views.rate_serving, name='rate_serving'),
    url(r'^deprecate/(\d+)/$', views.report_deprecation, name='report_deprecation'),
    url(r'^submit/(\d+)/$', views.submit_serving, name='submit_serving'),
]
