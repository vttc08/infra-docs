---
date: 2024-09-14 22:35
update: 2024-10-24T12:59:34-07:00
comments: "true"
---
# Uptime Kuma
> [!info]- [Docker Apps Rating](02-docker-ratings.md)
> | [U/GID](02-docker-ratings.md#ugid) | [TZ](02-docker-ratings.md#tz)  | [SSO/Users](02-docker-ratings.md#sso) | [Existing FS](02-docker-ratings.md#existing-fs) | [Portable](02-docker-ratings.md#portable) | [Subfolder](02-docker-ratings.md#subfolder) | [Mobile](02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ❎     | ✅*  | ❌🤵       | ✅        | ✅ | ❌ | ✔ |

## Install
**Docker Compose**
```yaml
services:
  uptime-kuma:
    container_name: uptime-kuma
    image: louislam/uptime-kuma
    ports:
      - 3001:3001
    environment:
      - PUID=1001
      - PGID=1001
    volumes:
      - ~/docker/uptime-kuma:/app/data
    restart: unless-stopped
```

- Container support non-root users  via `PUID/PGID`
- default port 3001

## Monitoring
To add a monitor, follow the GUI
- Friendly name is what is displayed on the dashboard
- There is an option to define how often to check, recheck and how many times to recheck
- Setup [notification]
### HTTP
![](assets/Pasted%20image%2020240916122455.png)
For HTTP monitoring, it will monitor a HTTP site and give out metrics as such up/down, and the response time.
- accepted response code: eg. 200-299 anything that is not accepted will be considered as down
- option to check HTTPS certificate expiration
### Docker
> [!warning]+ Docker Health
> Uptime Kuma does not notify if a Docker container is unhealthy, it will show as pending. No notification will be sent. [Github Issue](https://github.com/louislam/uptime-kuma/issues/4369)

Go to `Settings` -> `Docker Hosts` to create a Docker host.
Under `Add a new monitor`, select `Docker container` and choose the corresponding Docker host
#### Remote Hosts
By default, it requires mounted Docker sockets. It also supported socket over tcp or a socket proxy. For remote hosts it's best to use [tailscale](../Cloud%20VPS/basic-server-setup-caddy-docker-tailscale.md) and expose the appropriate docker socket to tailscale only.
### Notification
Configured under `Settings` -> `Notifications`
- it's possible to apply a newly added notification to all existing monitors
- when it's set as default, all new monitors will have this notification
### Tags
Tags can be added in `Settings` -> `Tags`, it can be applied to monitors. In the main page, tags can be filtered.
- tags cannot be used as a filter for status page or maintenance
![](assets/Pasted%20image%2020240916145549.png)
![](assets/Pasted%20image%2020240916145631.png)
## Status Page


Status page
Maintenance
Tags
SSO
Monitor services behind Authelia
Remote Docker Hosts
Autokuma

