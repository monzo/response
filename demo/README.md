# Response Demo App

This is an example Django project using the django-incident-response package that you can use to test drive Response locally. You'll need access to be able to add and configure apps in a Slack workspace of your choosing - you can sign up for a free account, if necessary.

All commands should be run from this directory (`demo`).

---

# Quick Start

The following steps explain how to create a Slack app, run Response locally, and configure everything to develop and test locally.

Broadly speaking, this sets things up as below:
<p align="center">
  <img width="600px" src="../docs/response.svg">
</p>

## 1. Create a Slack App

Follow [these instructions](../docs/slack_app_create.md) to create a new Slack App.

## 2. Configure the demo app

The demo app is configured using environment variables in a `.env` file. Create your own:
```
$ cp env.example .env
```
and update the variables in it:

| Environment Variable  | Descriptions |
|---|---|
| `SLACK_TOKEN`  |  Response needs an OAuth access token to use the Slack API.<br /><br />Copy the Bot Token that starts `xoxb-...` from the OAuth & Permissions section of your Slack App and use it to set the `SLACK_TOKEN` variable. |
|  `SLACK_SIGNING_SECRET` | Response uses the Slack signing secret to restrict access to public endpoints.<br /><br />Copy the Signing secret from the Basic Information page and use it to set the `SIGNING SECRET` variable.  |
| `INCIDENT_CHANNEL_NAME`  |  When an incident is declared, a 'headline' post is sent to a central channel.<br /><br />The default channel is `incidents` - change `INCIDENT_CHANNEL_NAME` if you want them to be sent somewhere else (note: do not include the #). |
| `INCIDENT_BOT_NAME`  | We want to invite the Bot to all Incident Channels, so need to know its ID. You can find/configure this in the App Home section of the Slack App.<br /><br />The default bot name is `incident` - change the `INCIDENT_BOT_NAME` if your app uses something different.<br /><br />⚠️ If your chosen username has ever been used on your Slack workspace, Slack will silently change the underlying username and won't show you the actual name in use anywhere. The easiest way to find the exact name you need to use is to make the API call directly [here](https://api.slack.com/methods/users.list/test), using your bot token from above, and searching the response for you APP ID, which is shown in the Basic Info page.  |

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


You can tail the logs of all containers with:
```
docker-compose logs -f
```

Ngrok establishes a new, random, URL any time it starts.  You'll need this to complete the Slack app setup, so look for an entry like this and make note of the https://abc123.ngrok.io address - this is your public URL.

```
ngrok       | The ngrok tunnel is active
ngrok       | https://6bb315c8.ngrok.io ---> response:8000
```

If everything has started successfully, you should see logs that look like this:

```
response    | Django version 2.1.7, using settings 'response.settings.dev'
response    | Starting development server at http://0.0.0.0:8000/
response    | Quit the server with CONTROL-C.
```

## 4. Complete the Slack App Setup

Head back to the Slack web UI and complete the configuration of your app, as [described here](../docs/slack_app_config.md).

## 5. Test it's working!

In Slack, start an incident with `/incident Something's happened`.  You should see a post in your incidents channel!

- Visit the incident doc by clicking the Doc link.
- Create a comms channel by clicking the button.
- In the comms channel check out the `@incident` commands.  You can find the ones available by entering `@incident help`.
