from django.contrib import admin

from response.core.models import Action, Event, ExternalUser, Incident

admin.site.register(Action)
admin.site.register(Event)
admin.site.register(Incident)
admin.site.register(ExternalUser)
