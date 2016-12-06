from django.conf.urls import url

from mensautils.canteen import views

app_name = 'mensautils.canteen'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^userconfig/save/$', views.save_canteen_user_config,
        name='save_canteen_user_config'),
    url(r'^stats/$', views.stats, name='stats'),
    url(r'^rate/(\d+)/$', views.rate_serving, name='rate_serving'),
    url(r'^deprecate/(\d+)/$', views.report_deprecation, name='report_deprecation'),
    url(r'^submit/(\d+)/$', views.submit_serving, name='submit_serving'),
    url(r'^verify/(\d+)/$', views.verify_serving, name='verify_serving'),
    url(r'^notification/$', views.notification, name='notification'),
    url(r'^notification/(\d+)/delete/$', views.delete_notification,
        name='delete_notification'),
    url(r'^notification/add/$', views.add_notification, name='add_notification'),
]
