---
date: 2024-09-12 21:47
update: 2024-09-13T13:11:51-07:00
comments: "true"
---
# YouTube Archive
## Pinchflat
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [ExistingFS](../02-docker-ratings.md#existing-fs) | [Portable](../02-docker-ratings.md#portable) | [Mobile](../02-docker-ratings.md#mobile) |
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ❎     | ✅*  | n/a      | ❌        | ✅ | ✔ |

YouTube archiving solution. Default port `8945`. Default credential `none`.
### Install
```yaml
services:
  pinchflat:
    container_name: pinchflat
    image: ghcr.io/kieraneglin/pinchflat:latest
    user: 1000:1001
    environment:
      - TZ=America/Vancouver
    ports:
      - '8945:8945'
    networks:
      - archive
    volumes:
      - ~/docker/pinchflat:/config
      - /mnt/nvme/share/youtube:/downloads
    restart: unless-stopped

networks:
  archive:
    name: archive
```

- `user` definition to fix permission issues, container will run fine
- app uses `sqlite` database for volumes in `/config`
- create custom network `archive` to easy container access with other apps

### Usage
#### Media Profile
The profile eg. resolution sponsorblock settings that is used to download videos also consist of renaming. The syntax are listed like such `/{{ source_custom_name }}/{{ channel }}/{{ upload_yyyy_mm_dd }} - {{ title }}.{{ ext }}`. More templates are available for customization. The example above shows a good naming for Jellyfin.
#### Sources
The sources are YouTube playlist or channels. To download a [Media Profile](#Media%20Profile) must be applied for the source. 
- each source can have a custom name that can be applied as `{{ source_custom_name }}`
The preferred method for indexing is `fast indexing`
The `Download Cutoff Date` can be set and only videos uploaded after that day will be downloaded.
>[!danger] Cutoff Date != Index 
>The cutoff date set there does not prevent indexing. When a source is added, everything will be indexed even before the cutoff date. This will take a very long time on a big channel.
#### Cookies
~~The app support downloading private playlists via YouTube cookies.~~
Cookies appears to be short-lived, more observations needed. (maybe use oauth2 plugin)
#### API Key
https://github.com/kieraneglin/pinchflat/wiki/Generating-a-YouTube-API-key
API key can be used to for fast indexing.
### Behavior
Pinchflat is not a media server, it only manage downloads not the files. Hence previous media cannot be imported. Everything is stored in its internal database.

Deleting or managing the file in other applications will not get reflected by the app.
- if the file is deleted in the filesystem, it will still exist in app but no video will exists and the video needs to be redownloaded
- the only way to delete files is to delete via the app

Media profile for each sources only have 1 chance of settings it right
- when changing media profile or editing profiles after a source is added and downloaded, even refreshing the metadata does not work

New changes to sources are not reflected immediately
- eg. when changing the cutoff date or when a new video is added to playlist or channel
- to have it download new videos immediately, need to manually `force index`