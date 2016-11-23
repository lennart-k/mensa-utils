from django.conf.urls import url

from mensautils.base import views

app_name = 'mensautils.base'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
