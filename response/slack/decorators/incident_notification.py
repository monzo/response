import logging
from datetime import datetime

from response.core.models import Incident
from response.slack.models.notification import Notification

logger = logging.getLogger(__name__)


NOTIFICATION_HANDLERS = []


class NotificationHandler(object):
    def __init__(self, key, callback, interval_mins, max_notifications):
        self.key = key
        self.callback = callback
        self.interval_mins = interval_mins
        self.max_notifications = max_notifications

    def __str__(self):
        return self.key


def single_notification(initial_delay_mins=0, func=None):
    """
    Register a handler that'll be called once in each open incident
    """

    def _wrapper(fn):
        NOTIFICATION_HANDLERS.append(
            NotificationHandler(
                key=fn.__name__,
                callback=fn,
                interval_mins=initial_delay_mins,
                max_notifications=0,
            )
        )
        return fn

    if func:
        return _wrapper(func)
    return _wrapper


def recurring_notification(interval_mins, max_notifications=1):
    """
    Register a handler that'll be called periodically for all open incidents.
    """

    def _wrapper(fn):
        NOTIFICATION_HANDLERS.append(
            NotificationHandler(
                key=fn.__name__,
                callback=fn,
                interval_mins=interval_mins,
                max_notifications=max_notifications - 1,
            )
        )
        return fn

    return _wrapper


def handle_notifications():

    # Only notify open incidents with a comms channel
    open_incidents = Incident.objects.filter(
        end_time__isnull=True, commschannel__incident__isnull=False
    )

    for incident in open_incidents:
        for handler in NOTIFICATION_HANDLERS:
            try:
                # get the last sent notification for this incident/handler pair
                notification = Notification.objects.get(
                    incident=incident, key=handler.key
                )

                # if we can find a previous notification for this incident/handler pair and
                # it's been set to not repeat, exit here
                if (
                    notification.repeat_count >= handler.max_notifications
                    or notification.completed
                ):
                    continue

                # it's not exhausted its max_notifications, so wait 'interval_mins' before sending again
                mins_since_last_notify = int(
                    (datetime.now() - notification.time).total_seconds() / 60
                )
                if mins_since_last_notify >= handler.interval_mins:
                    try:
                        handler.callback(incident)
                    except Exception as e:
                        logger.error(
                            f"Error calling notification handler {handler}: {e}"
                        )

                    notification.time = datetime.now()
                    notification.repeat_count = notification.repeat_count + 1
                    notification.save()

            except Notification.DoesNotExist:
                # we've never sent a notification to this incident/handler pair,
                # so wait until 'interval_mins' mins have elapsed from start
                mins_since_started = int(
                    (datetime.now() - incident.start_time).total_seconds() / 60
                )
                if mins_since_started >= handler.interval_mins:
                    try:
                        handler.callback(incident)
                    except Exception as e:
                        logger.error(
                            f"Error calling notification handler {handler}: {e}"
                        )

                    notification = Notification(
                        incident=incident,
                        key=handler.key,
                        time=datetime.now(),
                        repeat_count=0,
                    )
                    notification.save()
