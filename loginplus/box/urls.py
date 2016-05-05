# coding=utf-8
"""
This is the main module for task management.
"""
from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

__author__ = 'shaomingwu@inspur.com'


urlpatterns = [
    url(r'^task/$', views.TaskNew.as_view()),
    url(r'^task/(?P<taskid>[\w-]+)/$', views.TaskState.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
