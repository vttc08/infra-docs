---
date: 2024-07-05 17:59
update: 2024-07-05T22:56:49-07:00
comments: "true"
---
# 01 Docker Infrastructure

### Filesystem
##### Compose
All `docker-compose.yml` files are stored in `~/docker` folder, which then by default is under the network `docker_default`.
- by default for newly created apps, a new folder is created and `docker-compose.yml` is created for that app for testing
	- once app testing is complete, the compose file can be moved docker root folder if appropriate or remain
- some apps can be grouped together and these compose files are in the root docker folder such as `media.yml`, `network.yml`, the grouping allows multiple services to be managed by a single compose. For grouping, some of the property can include
	- the apps share common properties such as `arrs` apps
	- it is preferable for apps to live in same network, eg. `teslamate`
	- a large app requiring multiple containers eg. `frontend`, `mysql` etc..
	- apps share similar/same [category](#Categories), such as `qBittorrent` and `nzbget` can be put together in `downloader.yml` even though they do not have common properties or require same networking
##### Storage
The storage used for all containers are bind mount.
- application configs are stored in `~/docker/[app]`
	- if an app has multiple components needing persistence (eg. app with database, helpers), a folder will be created as such `~/docker/[app]/postgres` etc.
- apps that also store non-config data (such as music, documents etc.) and not using a lot of space can bind mount `/mnt/nvme/share` (a directory on local or another SSD) for fast data access and without spinning up HDD
- exceptions are home assistant or its related home automation containers and these are stored at `/srv/homeassistant`
##### Backup
The entire docker root folder is copied to a NFS share on another computer. With exception of [minecraft](Minecraft/minecraft-prep-and-install.md) and home assistant which a specialized method is used.
### Network
With `docker-compose`, a new network is created with the name of folder the compose is located, while it's possible to change network, it is not straightforward, therefore, there is no points in manually defining networks unless required.

**Public** `172.80.0.0/16` - bridge network for public facing applications with reverse proxy, this way when configuring Nginx Proxy Manager, all it need is to enter `container_name:80` rather than IP address.
- Nginx Proxy Manager - `172.80.44.3`
- Other containers will use docker DHCP to get address
- Containers that need to public facing can attach to this network
**Media** `172.96.0.0/16` - bridge network for arrs, downloader and management applications for easy interconnection when configuring
**Minecraft**  `172.255.255.0/24` - bridge network for Minecraft related networks
- Minecraft server (mcserver) - `172.255.255.65`

### Categories
Media Apps - apps related to media acquisition, curation and other functions services for Jellyfin
Networking - reverse proxy, DNS, VPN and related services
Home Automation - home assistant and its associated functions
VNC - containers based on [jlesage-vnc-apps](jlesage-vnc-apps.md) or Linuxserver Kasm images, usually desktop apps run in a browser via noVNC
Management - tools for managing docker containers or entire server
Games - game servers and associated tools
Filesharing - apps that share files to other clients
Documentation - notes and operation procedures for server infrastructure
Authentication - services that handle single sign-on (SSO) with users