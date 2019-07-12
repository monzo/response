from django.conf.urls import url, include
from django.urls import path

from . import views

urlpatterns = [
    path('incident/<int:incident_id>/', views.incident_doc, name='incident_doc'),
]
