from django.contrib import admin
from response.core.models import Incident, Action, ExternalUser

admin.site.register(Action)
admin.site.register(Incident)
admin.site.register(ExternalUser)
