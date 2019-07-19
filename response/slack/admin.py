from django.contrib import admin
from response.slack.models import HeadlinePost, CommsChannel, Notification, UserStats, PinnedMessage


# Register your models here.
admin.site.register(HeadlinePost)
admin.site.register(CommsChannel)
admin.site.register(Notification)
admin.site.register(UserStats)
admin.site.register(PinnedMessage)
