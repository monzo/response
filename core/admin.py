from django.contrib import admin
from core.models import Incident
from core.models import Action

admin.site.register(Incident)
admin.site.register(Action)
