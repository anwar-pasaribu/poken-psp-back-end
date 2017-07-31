# coding=utf-8
from django.conf.urls import url

from poken_web import views


urlpatterns = [
	# /peber_web/
	url(r'^$', views.index, name='index'),
]