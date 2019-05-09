from django.conf.urls import url, include
from django.urls import path

import ui.views as views

urlpatterns = [
    path('incident/<int:incident_id>/', views.incident_doc, name='incident_doc'),
    path('', views.active_incidents, name='active_incidents'),
    path('active', views.active_incidents, name='active_incidents'),
    path('recent', views.recent_incidents, name='recent_incidents'),
]
