from django.contrib import admin

from response.slack.models import (
    CommsChannel,
    HeadlinePost,
    Notification,
    PinnedMessage,
    UserStats,
)

# Register your models here.
admin.site.register(HeadlinePost)
admin.site.register(CommsChannel)
admin.site.register(Notification)
admin.site.register(UserStats)
admin.site.register(PinnedMessage)
