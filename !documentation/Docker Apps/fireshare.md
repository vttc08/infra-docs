---
date: 2024-08-22 16:33
update: 2024-10-24T12:59:24-07:00
comments: "true"
---
# Fireshare
> [!info]- [Docker Apps Rating](02-docker-ratings.md)
> | [U/GID](02-docker-ratings.md#ugid) | [TZ](02-docker-ratings.md#tz)  | [SSO/Users](02-docker-ratings.md#sso) | [Existing FS](02-docker-ratings.md#existing-fs) | [Portable](02-docker-ratings.md#portable) | [Subfolder](02-docker-ratings.md#subfolder) | [Mobile](02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ❎     | ✅*  | ❌🤵       | ✅        | ✅ | ❌ | ✔ |

## Configuration
```yaml
services:
  fireshare:
    image: shaneisrael/fireshare:develop
    container_name: fireshare
    environment:
      - MINUTES_BETWEEN_VIDEO_SCAN=30
      - PUID=1000
      - PGID=1001
    env_file:
      - .env # admin password
    volumes:
      - ~/docker/fireshare/data:/data:rw
      - ~/docker/fireshare/processed:/processed:rw
      - /mnt/nvme/share/gaming:/videos:rw
    networks:
      public:
    ports:
      - 8080:80
    restart: unless-stopped
  
networks:
  public:
    name: public
    external: true
```
### Environments
Content of `.env` 
```env
ADMIN_PASSWORD=
DOMAIN=
```
Setup user and group ID accordingly; more environment options are available https://github.com/ShaneIsrael/fireshare/wiki/Fireshare-Configurables
### Other
The software can also be configured via `config.json` located in `/data/config.json`. It's configuration is same as the WebUI. 
`Default Video Privacy`: `false` set all the videos public viewable without sharing manually
`Default Video Privacy`: `false` public user cannot upload videos
`Sharable Link Domain`: link which fireshare append to when sharing files
`Upload Folder`: folder that will be created in `/videos` directory when file is uploaded
## Usage
![](assets/Pasted%20image%2020240822173743.png)
By default, can view videos, admin and share links and the link will show preview and viewable in Discord. Admin can also upload directly in web interface. All the uploaded files are located in `/videos/uploads`
- when uploading files through filesystem with a changed date via `touch` the changed date will also be reflected in the app
#### Workflow
https://github.com/vttc08/fireshare-import
Refer to this Github repo to setup. For personal documentation

- setup the project directory into `~/Documents/Projects`
