# Response Demo App

This is an example Django project using the django-incident-response package that you can use to test drive `response` locally. You'll need access to be able to add and configure apps in a Slack workspace of your choosing - you can sign up for a free account, if necessary.

All commands should be run from this directory (`demo`).

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

## 2. Configure the demo app

The demo app is configured using environment variables in a `.env` file. Create your own:
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


