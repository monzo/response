import json
import logging
from datetime import datetime, timedelta


import after_response
import urllib.parse
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from core.models.incident import Incident
from .models import SlackUser
from slack.decorators import handle_action, handle_event, handle_notifications, handle_dialog
from slack.authentication import slack_authenticate
from slack.dialog_builder import Dialog, Text, TextArea, SelectWithOptions, SelectFromUsers
from slack.settings import INCIDENT_REPORT_DIALOG
from slack.slack_utils import channel_reference, send_message
from django.core.signing import dumps, loads

logger = logging.getLogger(__name__)

from .models.slack_user import SlackUser

@csrf_exempt
@slack_authenticate
def slash_command(request):
    """
    Handles slash commands from slack
    More details here: https://api.slack.com/slash-commands

    @param request the request from slack containing the slash command
    @return: return a HTTP response to indicate the request was handled
    """

    user_id = request.POST.get('user_id')
    trigger_id = request.POST.get('trigger_id')
    report = request.POST.get('text')

    dialog = Dialog(
        title="Report an Incident",
        submit_label="Report",
        elements=[
            Text(label="Report", name="report", placeholder="What's the tl;dr?", value=report),
            TextArea(label="Summary", name="summary", optional=True, placeholder="Can you share any more details?"),
            TextArea(label="Impact", name="impact", optional=True, placeholder="Who or what might be affected?", hint="Think about affected people, systems, and processes"),
            SelectFromUsers(label="Lead", name="lead", optional=True),
            SelectWithOptions([(i, s.capitalize()) for i, s in Incident.SEVERITIES], label="Severity", name="severity", optional=True)
        ]
    )

    dialog.send_open_dialog(INCIDENT_REPORT_DIALOG, trigger_id)
    return HttpResponse()


@csrf_exempt
@slack_authenticate
def action(request):
    """
    Handles actions sent from Slack.

    @param request the request from slack containing an action
    @return: return a HTTP response to indicate the request was handled
    """
    payload = json.loads(request.POST['payload'])
    action_type = payload['type']

    if action_type == 'dialog_submission':
        handle_dialog.after_response(payload)
    elif action_type == 'block_actions':
        handle_action.after_response(payload)
    else:
        logger.error(f"No handler for action type {action_type}")

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

def claim_slack_user(request, user_id): # Me UHMBFACG5
    slack_user = SlackUser.objects.get(user_id=user_id)
    if slack_user.owner:
        return HttpResponseForbidden("User was already claimed")

    token = dumps({
        'created': datetime.now().isoformat(),
        'slack_user_id': slack_user.user_id })

    url = request.build_absolute_uri(reverse("confirm_claim_slack_user")) + f'?token={token}'
    send_message(slack_user.user_id,f'Would you like to link your slack account with response user `{request.user.username}` <{url}|Link account>')

    return HttpResponse('')

def confirm_claim_slack_user(request):
    token = loads(request.GET.get('token'))

    # Only want tokens less than x minutes old or newer
    if datetime.strptime(token['created'], "%Y-%m-%dT%H:%M:%S.%f") > datetime.now() - timedelta(minutes=10):
        slack_user = SlackUser.objects.get(user_id=token['slack_user_id'])
        if slack_user.owner:
            return HttpResponseForbidden("User was already claimed")
        slack_user.owner = request.user
        slack_user.save()
        return HttpResponse("🔗 Accounts linked. You may close this window.")

    return HttpResponseNotFound("⛔️ Failed to link your accounts. Your token has expired. 🎟")
