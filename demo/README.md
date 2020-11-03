# Response

The easiest way to get started is with docker! 

## 1. Create a Slack App

Follow [these instructions](../docs/slack_app_create.md) to create a new Slack App.

## 2. Configure Response!

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

## 3. Start Postgres

```bash
docker-compose up -d db
```

## 4. Run Response

```bash
docker run -it --rm --env-file .env --ports 8000:8000 response
```

## 5. Complete the Slack App Setup

Head back to the Slack web UI and complete the configuration of your app, as [described here](../docs/slack_app_config.md).

## 6. Test it's working!

In Slack, start an incident with `/incident Something's happened`.  You should see a post in your incidents channel!

- Visit the incident doc by clicking the Doc link.
- Create a comms channel by clicking the button.
- In the comms channel check out the `@incident` commands.  You can find the ones available by entering `@incident help`.
