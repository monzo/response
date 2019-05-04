# Response ⚡

Dealing with incidents can be stressful. On top of dealing with the issue at hand, responders are often responsible for handling comms, both internal and external, reporting, and coordinating the efforts of other engineers. To reduce the pressure and cognitive burden on its engineers, Monzo built Response to help coordinate and report incidents.

The tool integrates deeply with Slack and revolves around the following ideals:

- **Limit context switching**
  Context switching during an incident is often unavoidable.  Response aims to limit this, by enabling actions to be carried out without leaving the conversation.

- **Make the easy thing the right thing**
  If something needs doing, bring it to the attention of the responder when it makes sense, or better still automate it away.

<p align="center">
  <img width="300px" src="./docs/headline_post.png"><br />
  <em>The headline post when an incident is declared</em>
</p>

If you're interested in how we use this tool at Monzo, there's an overview in [this video](https://twitter.com/evnsio/status/1116026261401247745).

---

# Quick Start

The following steps explain how to create a Slack app, run Response locally, and configure everything to develop and test locally.

Broadly speaking, this sets things up as below:
<p align="center">
  <img width="600px" src="./docs/response.svg">
</p>

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

## 2. Configure Response

Response is configured using environment variables in a `.env` file. Create your own:
```
$ cp env.example .env
```
and update the variables in it:

### OAuth Access Token (`SLACK_TOKEN`)

Response needs an OAuth access token to use the Slack API.

- Copy the token that starts `xoxp-...` from the OAuth & Permissions section of your Slack App and use it to set the `SLACK_TOKEN` variable.

**Note:** Since some of the APIs commands we use require a _user_ token, we only need the token starting with `xoxp-...`.  If/when Slack allow these actions to be controlled by Bots, we can use the _bot_ token, starting `xoxb-...`.

### Signing Secret (`SIGNING_SECRET`)

Response uses the Slack signing secret to restrict access to public endpoints.

- Copy the Signing secret from the Basic Information page and use it to set the `SIGNING SECRET` variable.

### Incident Channel (`INCIDENT_CHANNEL_NAME`)

When an incident is declared, a 'headline' post is sent to a central channel.

- The default channel is `incidents` - change `INCIDENT_CHANNEL_NAME` if you want them to be sent somewhere else (note: do not include the #).

### Bot Name (`INCIDENT_BOT_NAME`)

We want to invite the Bot to all Incident Channels, so need to know its ID.

- The default bot name is `incident` - change the `INCIDENT_BOT_NAME` if your app uses something different.


## 3. Run Response

From the root of the Response directory run:

```
docker-compose up
```

This starts the following containers:

- response: the main Response app
- postgres: the DB used by the app to store incident data
- cron: a container running cron, configured to hit an endpoint in Response every minute
- ngrok: ngrok in a container, providing a public URL pointed at Response.

Ngrok establishes a new, random, URL any time it starts.  You'll need this to complete the Slack app setup, so look for an entry like this and make note of the https://abc123.ngrok.io address - this is your public URL.

```
ngrok       | The ngrok tunnel is active
ngrok       | https://6bb315c8.ngrok.io ---> response:8000
```

If everything has started successfully, you should see logs resembling the following:

```
response    | Django version 2.1.7, using settings 'response.settings.dev'
response    | Starting development server at http://0.0.0.0:8000/
response    | Quit the server with CONTROL-C.
```

## 4. Complete the Slack App Setup

### Slash Command

- In the Slash commands page click `Create New Command`.

- Enter the following info:
  - Command:  `/incident`
  - Request URL: `https://<public-url>/slack/slash_command`
  - Short Description: `Trigger an incident`
  - Usage Hint: `What's the problem?`

### Event Subscriptions

In the Event Subscriptions page we need to configure the following:

- Toggle `Enable Events` to On
- In the Request URL enter: `https://<public-url>/slack/event`
- You need to have the server running and available as Slack sends a challenge to this address and expects a specific response.

- Under the Subscribe to Bot Events section, add the following:
  - `app_mention`
  - `pin_added`
  - `pin_removed`
  - `message.channels`

### Configure interactive components

- In the Interactive Components page, enable and set the URL to `https://<public-url>/slack/action`.

### Bot Users

- In the Bot Users page, configure the Display Name and Default Username to `incident`.
- Toggle 'Always Show My Bot as Online' to On.


## 5. Test it's working!

In Slack, start an incident with `/incident Something's happened`.  You should see a post in your incidents channel!

- Visit the incident doc by clicking the Doc link.
- Create a comms channel by clicking the button.
- In the comms channel check out the `@incident` commands.  You can find the ones available by entering `@incident help`.

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
def handle_close_incident(incident: Incident, user_id: str, message: json) -> json:
    incident.end_time = datetime.now()
    incident.save()
```
