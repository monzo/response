import json
import logging
from datetime import datetime

import after_response

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.models.incident import Incident
from slack.decorators import handle_action, handle_event, handle_notifications
from slack.slack_utils import channel_reference
from slack.authentication import slack_authenticate

logger = logging.getLogger(__name__)


@csrf_exempt
@slack_authenticate
def slash_command(request):
    """
    Handles slash commands from slack
    More details here: https://api.slack.com/slash-commands

    @param request the request from slack containing the slash command
    @return: return a HTTP response to indicate the request was handled
    """
    report = request.POST.get('text')

    if not report:
        return HttpResponse("It looks like you forgot to provide any details 🤔 \
        \n\nCan you try again with something like `/incident something has happened`?")

    user_id = request.POST.get('user_id')

    Incident.objects.create_incident(
        report=report,
        reporter=user_id,
        report_time=datetime.now(),
    )

    incidents_channel_ref = channel_reference(settings.INCIDENT_CHANNEL_ID)
    text = f"Thanks for raising the incident 🙏\n\nHead over to {incidents_channel_ref} to complete the report and/or help deal with the issue"

    return HttpResponse(text)


@csrf_exempt
@slack_authenticate
def action(request):
    """
    Handles actions sent from Slack.

    @param request the request from slack containing an action
    @return: return a HTTP response to indicate the request was handled
    """
    payload = json.loads(request.POST['payload'])

    handle_action.after_response(payload)

    return HttpResponse()


@csrf_exempt
@slack_authenticate
def event(request):
    """
    Handles events sent from Slack.

    Details: We can configure our Slack app receive specific events, and doing so tells
    slack to call this endpoint with a JSON payload representing the event.

    See here for reference: https://api.slack.com/events-api

    @param request the request from slack containing an event
    @return: return a HTTP response to indicate the request was handled
    """
    payload = json.loads(request.body)
    action_type = payload['type']

    if action_type == 'event_callback':
        handle_event(payload)
    elif action_type == 'url_verification':
        # the url_verification event is called when we change the registered event callback url
        # in the Sl ack app configuration.  It expects us to return the challenge token sent in
        # the request
        return HttpResponse(payload['challenge'])

    return HttpResponse()


@csrf_exempt
def cron_minute(request):
    "Handles actions that need to take place every minute"
    handle_notifications()
    return HttpResponse()
