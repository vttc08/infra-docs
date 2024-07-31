---
date: 2024-07-23 17:39
update: 2024-07-24T16:16:08-07:00
comments: "true"
---
# Jellystat

> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Portable](../02-docker-ratings.md#portable) | [Subfolder](../02-docker-ratings.md#subfolder) |
> | ----- | --- | --------- | -------- | -------- |
> | ❎     | ✅*  | ❌🤵       | ✅        | ❌ |
https://github.com/CyferShepard/Jellystat
## Install
Docker Compose (minimum viable setup)
```yaml
services:
  jellystat-db:
    container_name: jellystat-db
    image: postgres:15
    user: 1000:1001
    env_file:
      - jellystat.env
    environment:
      POSTGRES_DB: 'jellystat'
      TZ: 'America/Vancouver'
      PGTZ: 'America/Vancouver'
    volumes:
    - ~/docker/jellystat/db:/var/lib/postgresql/data # Mounting the volume

  jellystat:
    image: cyfershepard/jellystat:latest
    container_name: jellystat
    user: 1000:1001
    env_file:
      - jellystat.env
    environment:
      POSTGRES_IP: jellystat-db
      POSTGRES_PORT: 5432
    ports:
      - "5050:3000" #Server Port
    volumes:
      - ~/docker/jellystat/app:/app/backend/backup-data # Mounting the volume
    depends_on:
      - jellystat-db
    restart: unless-stopped
```

The content of `jellystat.env`
```toml
POSTGRES_USER=jellystat
POSTGRES_PASSWORD=
JWT_SECRET=
```
- Use both `PGTZ` and `TZ` to set timezone logging
- The environment `POSTGRES_DB` may not work, the default database is `jfstat`
The secret can be generated with
```bash
openssl rand -base64 64 | tr -d '\ n'
```

## Usage
Jellyfin API key is needed to configure it. The app will show login/configuration screen.
No other configurations are nessecary.
### Backup/Restore
If using bind mount, simply copy the files in the bind mount and everything will work on the new machine without issues. No database dumps, other steps are necessary.
- ensure the username/password/secret in the environments are matching
### Reverse Proxy/SSO
App do not have SSO support. The internal login cannot be disabled, [github issue](https://github.com/CyferShepard/Jellystat/issues/218).
App do not support subfolders, only subpath supported. No special requirements needed when using Nginx Proxy Manager. If the frontend is in the same network as proxy, simply `jellystat:3000` is enough.

![](assets/Pasted%20image%2020240724155641.png)