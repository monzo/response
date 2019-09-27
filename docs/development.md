# Development

## Django
Response is built using [Django](https://www.djangoproject.com/). If you're not familiar with it, there are good [docs here](https://docs.djangoproject.com/en/2.1/).

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
def runbook_notification(comms_channel: CommsChannel, user: str, keyword: str, text: str, ts: str):
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

### Headline Post Actions

When a new incident is created, we create a "headline post" message in the central incidents channel. We add action buttons here - by default allowing creating an incident channel, editing the incident or closing. There is a decorator that allows you to add custom action buttons here - `@headline_post_action`.

For example:
```
from response.slack import block_kit
from response.slack.decorators import headline_post_action

@headline_post_action(order=150)
def my_cool_headline_action(headline_post):
    return block_kit.Button(":sparkles: My cool action", "my-cool-action", value=headline_post.incident.pk)
```

You should provide a function which takes a `headline_post` parameter, and either returns `None` (a button won't be created) or an action, e.g. `block_kit.Button`. You can also specify an `order` parameter, which will determine the order in which actions appear. The default buttons have orders of 100, 200 and 300, so the above example would appear second:

![](https://www.dropbox.com/s/ummtglal8xmw2rj/Screenshot%202019-08-08%2014.55.20.png?raw=1)

Check the logs to see which actions have been registered, and what order they're registered in.

```
INFO  - headline_post_a - Registering headline post action create_comms_channel_action with order 100
INFO  - headline_post_a - Registering headline post action edit_incident_button with order 200
INFO  - headline_post_a - Registering headline post action close_incident_button with order 300
INFO  - headline_post_a - Registering headline post action my_cool_headline_action with order 150
```

## Release Process

See [release.md](release.md) for how to release an update.
