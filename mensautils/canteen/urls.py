from django.conf.urls import url

from mensautils.canteen import views

app_name = 'mensautils.base'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stats/$', views.stats, name='stats'),
]
