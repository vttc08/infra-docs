---
date: 2024-11-12 21:25
update: 2024-11-12T22:10:38-08:00
comments: "true"
---
# Apprise API
https://github.com/caronc/apprise-api
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Existing FS](../02-docker-ratings.md#existing-fs) | [Portable](../02-docker-ratings.md#portable) | [Subfolder](../02-docker-ratings.md#subfolder) | [Mobile](../02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ✅     | ✅  | ❌🤵       | ❌        | ✅ | n/a | ❌ |

## Install
App is installed on port 7000 as port 8000 is taken.
```yaml
services:
  apprise-api:
    image: lscr.io/linuxserver/apprise-api:latest
    container_name: apprise-api
    environment:
      - PUID=${PUID}
      - PGID=${PGID}
      - TZ=America/Vancouver
      - APPRISE_ATTACH_SIZE=500
    volumes:
      - ~/docker/apprise-api/config:/config
      - ~/docker/apprise-api/attachments:/attachments
    ports:
      - 7000:8000
    restart: unless-stopped
```

> [!bug]+ Attachment Folder
> To use attachments, a local folder that is bind mount to `/attachments` must be created before spinning up the container otherwise there will be permission issues, despite PUGID, the `/attachments` folder permission is not set by the container. 

The option `APPRISE_ATTACH_SIZE` is the maximum size the server will accept for attachments and sending it, by default it's 200MB or other number in MB.
## Usage
For a list of endpoints
https://github.com/caronc/apprise?tab=readme-ov-file#productivity-based-notifications
Specifics about endpoints will be used in internal documentation, this is for API server only.
### Adding Endpoint
To add a configuration entry, navigate to the IP:Port running the API and add `cfg/<your-apprise-id>` to create a new configuration.
- the same id is used for checking and editing configuration

Example configuration
```python
apprise,discord=discord://<userid>/<webhook>/?avatar_url=https%3A//raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/apprise.png
newapp=slack://<>/<>/#channel
admin=apprise,newapp
```
### Tags
https://github.com/caronc/apprise-api/blob/master/README.md#screenshots
After configuring API, apprise tags can be used, in above example.
- apprise or discord tag will send discord notification; while newapp tag will send slack notification
- with tag admin, both apprise and newapp tag are included

### Sending Notifications
https://github.com/caronc/apprise/wiki/Notify_apprise_api
Everything in single URL (to put into app configuration)
```
apprise://10.10.120.12:7000/<my-id>?tags=tags
```

Apprise CLI
```bash
apprise --config=http://10.10.120.12:7000/get/apprise -b "" -a "/path/to/attachment" --tag=tags
```
Alternative, apprise configuration files can be used to include the API configuration.

Standard cURL
```bash
curl -X POST -F "body=Test Message" -F "tags=all" \
    http://10.10.120.12:7000/notify/apprise
```

### Maintenance
Backup and restore is simple although the configurations are encrypted and not viewable, all it's needed is to copy the entire Docker folder to another folder and ensure volume mappings are correct. All the configurations are located.

For internal documentation:
The Apprise-API include a configuration with the id `apprise` which include all the internal Discord, Telegram and other endpoints. It is mostly for easy use with third-party apps and to send a notification, just put this URL in the supported applications as there is no need to remember all the Discord API webhooks.
```
apprise://10.10.120.12:7000/apprise?tags=discord
```