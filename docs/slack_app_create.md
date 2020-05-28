# Creating your Slack App

- Navigate to [https://api.slack.com/apps](https://api.slack.com/apps) and click `Create New App`.
- Give it a name, e.g. 'Response', and select the relevant workspace.

- In the OAuth and Permissions page, scroll down to Bot Token Scopes.

- Add the following scopes:
  - `app_mentions:read`
  - `channels:history`
  - `channels:join`
  - `channels:manage`
  - `channels:read`
  - `chat:write`
  - `chat:write.public`
  - `reactions:write`
  - `users:read`
  - `users:read.email`

- At the top of the page, the `Install App to Workspace` button is now available.  Click it!