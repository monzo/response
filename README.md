# Response ⚡

Dealing with incidents can be stressful. On top of dealing with the issue at hand, responders are often responsible for handling comms, coordinating the efforts of other engineers, and reporting what happened after the fact.  Monzo built Response to help reduce the pressure and cognitive burden on engineers during an incident, and to make it easy to create information rich reports for others to learn from.

<p align="center">
  <img width="300px" src="./docs/headline_post.png"><br />
  <em>The headline post when an incident is declared</em>
</p>

If you're interested in how we use this tool at Monzo, there's an overview in [📺 this video](https://twitter.com/evnsio/status/1116026261401247745).

---

# Try it out

Response is a Django app which you can include in your project.  If you're just looking to give it a try, follow the instuctions for the [demo app](demo/README.md)!

---

# Quick Start

Ready to create your own project using Response?  This quick start explains how to start one from scratch.

[Start a new Django project](https://docs.djangoproject.com/en/2.2/intro/tutorial01/), if you don't have one already:
```
$ django-admin startproject myincidentresponse
```

Install response:
```
$ pip install django-incident-response
```

In `settings.py`, add these lines to `INSTALLED_APPS`:
```
INSTALLED_APPS = [
    ...
    "after_response",
    "rest_framework",
    "bootstrap4",
    "response.apps.ResponseConfig",
]
```

Add the following to `settings.py`:

```
USE_TZ = False # if this exists elsewhere in your settings.py, just update the value

STATIC_ROOT = "static"

# Django Rest Framework
REST_FRAMEWORK = {
    "PAGE_SIZE": 100,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}
#

# Markdown Filter
MARKDOWN_FILTER_WHITELIST_TAGS = [
    "a", "p", "code", "h1", "h2", "ul", "li", "strong", "em", "img",
]

MARKDOWN_FILTER_WHITELIST_ATTRIBUTES = ["src", "style"]

MARKDOWN_FILTER_WHITELIST_STYLES = [
    "width", "height", "border-color", "background-color", "white-space",
    "vertical-align", "text-align", "border-style", "border-width", "float",
    "margin", "margin-bottom", "margin-left", "margin-right", "margin-top",
]
```

In `urls.py`, add the following to `urlpatterns` (you may also need to import `include`):
```
urlpatterns = [
    ...
    path('slack/', include('response.slack.urls')),
    path('core/', include('response.core.urls')),
    path('', include('response.ui.urls')),
]
```

---
# Configuring your project as a Slack App

## 1. Create a Slack App

- Navigate to [https://api.slack.com/apps](https://api.slack.com/apps) and click `Create New App`.
- Give it a name, e.g. 'Response', and select the relevant workspace.

- In the OAuth and Permissions page, scroll down to scopes.

- Add the following scopes:
  - `channels:history`
  - `channels:read`
  - `channels:write`
  - `chat:write:bot`
  - `chat:write:user`
  - `users:read`

- At the top of the page, the `Install App to Workspace` button is now available.  Click it!

## 2. Add config to `settings.py`

### Base site address (`SITE_URL`)

Response needs to know where it is running in order to create links to the UI in Slack.  Whilst running locally, you might want this set to something like "http://localhost:8000".


### OAuth Access Token (`SLACK_TOKEN`)

Response needs an OAuth access token to use the Slack API.

- Copy the token that starts `xoxp-...` from the OAuth & Permissions section of your Slack App and use it to set the `SLACK_TOKEN` variable.

**Note:** Since some of the APIs commands we use require a _user_ token, we only need the token starting with `xoxp-...`.  If/when Slack allow these actions to be controlled by Bots, we can use the _bot_ token, starting `xoxb-...`.

### Signing Secret (`SLACK_SIGNING_SECRET`)

Response uses the Slack signing secret to restrict access to public endpoints.

- Copy the Signing secret from the Basic Information page and use it to set the `SIGNING SECRET` variable.

### Incident Channel and ID (`INCIDENT_CHANNEL_NAME`, `INCIDENT_CHANNEL_ID`)

When an incident is declared, a 'headline' post is sent to a central channel.

See the demo app for an example of how to get the incident channel ID from the Slack API.

### Bot Name and ID (`INCIDENT_BOT_NAME`, `INCIDENT_BOT_ID`)

We want to invite the Bot to all Incident Channels, so need to know its ID.


### Running the server

```
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
```

---

# Development

## Django
Response is built using [Django](https://www.djangoproject.com/). If you're not familiar with it, there are good [docs here](https://docs.djangoproject.com/en/2.1/).

## Making Changes

- The docker-compose setup maps your Response working directory into the running container.  Any changes made locally will automatically be reflected in the running instance.

- In some cases, it may be necessary to run commands within the container.  This can be done with:

```
docker-compose exec -ti response
```

- If you need to rebuild the app you can use:

```
docker-compose build
```

## Building Blocks

It's likely you'll want to configure Response to support your own environment and processes.  To make this easier, Response provides some useful building blocks in the form of function decorators.

### Incident Commands: `@incident_command`

The `@incident_command` decorator allows you to define a new incident command handler in single function.

**Example** if you wanted a command to show how long an incident had been running you'd simply need to add this one function:

```
@incident_command(['duration'], helptext='How long has this incident been running?')
def update_duration(incident: Incident, user_id: str, message: str):
    duration = incident.duration()

    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.post_in_channel(f"⏱ The incident has been running for {duration}")

    return True, None
```

### Incident Notifications: `@recurring_notification` / `@single_notification`

These decorators allow you to define Notifications which get posted to comms channel as specific intervals.

**Example** if you wanted to remind the engineer to take break every 15 minutes you could define a function similar to the following:

```
@recurring_notification(interval_mins=30, max_notifications=10)
def take_a_break(incident: Incident):
    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.post_in_channel("👋 30 minutes have elapsed. Think about taking a few minutes away from the screen.")
```

### Keyword Handlers: `@keyword_handler`

These decorators allow functions to called when a specific keyword or phrase appears in a message posted in comms channel.

**Example** if you wanted to remind people where to find your runbooks when they mention 'runbook' you could do the following:

```
@keyword_handler(['runbook', 'run book'])
def runbook_notification(comms_channel: CommsChannel, user: str, text: str, ts: str):
    comms_channel.post_in_channel("📗 If you're looking for our runbooks they can be found here https://...")
```

### Event Handlers: `@event_handler`

Slack can send events for pretty much anything going on in your team. The full list is available [here](https://api.slack.com/events), and new handlers can be added to Response by using the `@event_handler` decorator.

Examples of these can be found in [event_handlers.py](https://github.com/monzo/response/blob/master/slack/event_handlers.py).

### Action Handlers: `@action_handler`

Action handlers are used to handle button presses.  Buttons are assigned IDs when they are created (see [here](https://github.com/monzo/response/blob/master/slack/models/headline_post.py#L57)), and a handler can be linked by simply using the same ID.

```
@action_handler(HeadlinePost.CLOSE_INCIDENT_BUTTON)
def handle_close_incident(action_context: ActionContext):
    incident = action_context.incident
    incident.end_time = datetime.now()
    incident.save()
```
