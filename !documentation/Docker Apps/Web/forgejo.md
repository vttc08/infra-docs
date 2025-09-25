---
date: 2025-09-17 22:21
update: 2025-09-23T14:47:17-07:00
comments: "true"
---
# Forgejo
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Existing FS](../02-docker-ratings.md#existing-fs) | [Portable](../02-docker-ratings.md#portable) | Subfolder| [Mobile](../02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ✅     | ✅ | ✅👪       | ✅        | ✅ | ✅ | ✅ |


## Install
```yaml
services:
  forgejo:
    image: codeberg.org/forgejo/forgejo:12
    container_name: forgejo
    environment:
      - USER_UID=${PUID}
      - USER_GID=${PGID}
      - SSH_PORT=222
      - FORGEJO__server__SSH_DOMAIN=forgejo
    restart: unless-stopped
    networks:
      - public
    volumes:
      - ~/docker/forgejo:/data
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
    ports:
      - '3022:3000'
      - '222:222'

networks:
  public:
    external: true
```

- the `SSH_PORT` and `222:222` are used so the display clone URL work as expected
- similarly the `FORGEJO__server__SSH_DOMAIN=forgejo` 

## Configuration
Follow the GUI for configs (e.g. username, password, base URL)

### SSH
Fix permission issue on Windows
```bash
ssh-keygen -f forgejo -e -m pem
```

SSH config file for Forgejo
```
Host forgejo
  User git
  Hostname 10.10.120.12
  Port 222
  IdentityFile C:\\Users\\hubcc\\.ssh\\forgejo
```

Simply clone the SSH repo URL is enough
```bash
git clone ssh://git@forgejo/user/ACIT-2520.git
```
### Mirror to Github
https://forgejo.org/docs/latest/user/repo-mirror/#setting-up-a-push-mirror-from-forgejo-to-github
This is done per project.
![](assets/Pasted%20image%2020250923143946.png)
- `Settings` > `Repository` > `Mirror Settings`

![](assets/Pasted%20image%2020250923144558.png)
