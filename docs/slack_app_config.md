# Configuring your Slack app

The steps here outline how to complete the Slack side setup for Response.  The app will need to be running, and accessible on a public domain to complete these steps as Slack validates the URL before it'll accept the change.

## Slash Command

- In the Slash commands page click `Create New Command`.

- Enter the following info:
  - Command:  `/incident`
  - Request URL: `https://<public-url>/slack/slash_command`
  - Short Description: `Trigger an incident`
  - Usage Hint: `What's the problem?`

## Event Subscriptions

In the Event Subscriptions page we need to configure the following:

- Toggle `Enable Events` to On
- In the Request URL enter: `https://<public-url>/slack/event`
- You need to have the server running and available as Slack sends a challenge to this address and expects a specific response.

- Under the Subscribe to Bot Events section, add the following:
  - `app_mention`
  - `pin_added`
  - `pin_removed`
  - `message.channels`
  - `channel_rename`

## Configure interactive components

- In the Interactive Components page, enable and set the URL to `https://<public-url>/slack/action`.

## Bot Users

- In the Bot Users page, configure the Display Name and Default Username to `incident`.
- Toggle 'Always Show My Bot as Online' to On.
