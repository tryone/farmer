# coding: utf-8

from django.conf.urls import *

urlpatterns = patterns('farmer.openid2.views',
        (r'^login/', 'login'),
        (r'^logout/', 'logout'),
        (r'^verify/', 'verify'),
        (r'^$', 'index'),
    )
