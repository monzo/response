from django.conf.urls import url, include
from django.urls import path

import response.slack.views as views

urlpatterns = [
    path('slash_command', views.slash_command, name='slash_command'),
    path('action', views.action, name='action'),
    path('event', views.event, name='event'),
    path('cron_minute', views.cron_minute, name='cron_minute'),
]
