from django.contrib import admin
from core.models import Incident, Action, ExternalUser, Timeline, Source

admin.site.register(Action)
admin.site.register(Incident)
admin.site.register(ExternalUser)
admin.site.register(Timeline)
admin.site.register(Source)
