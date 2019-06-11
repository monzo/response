from django.contrib import admin

from slack.models import HeadlinePost, CommsChannel, Notification, UserStats, PinnedMessage, SlackUser

# Register your models here.
admin.site.register(HeadlinePost)
admin.site.register(CommsChannel)
admin.site.register(Notification)
admin.site.register(UserStats)
admin.site.register(PinnedMessage)
admin.site.register(SlackUser)
