"""site1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
#from vnc.views import *

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login', 'vnc.views.login'),
    url(r'^logout', 'vnc.views.logout'),
    url(r'^index', 'vnc.views.index'),
    url(r'^createnew', 'vnc.views.createnew'),
    url(r'^createresult', 'vnc.views.createresult'),
    url(r'^test', 'vnc.views.test'),
    url(r'^kill', 'vnc.views.kill'),
    url(r'^changevncpassword', 'vnc.views.changevncpassword'),
    url(r'^getusername', 'vnc.views.getusername'),
    url(r'^recreate', 'vnc.views.recreate'),
    url(r'^getlocalvnc', 'vnc.views.getlocalvnc'),
    url(r'^$', 'vnc.views.index'),
    url(r'^help', 'vnc.views.help'),
    url(r'^comment', 'vnc.views.comment'),
]
