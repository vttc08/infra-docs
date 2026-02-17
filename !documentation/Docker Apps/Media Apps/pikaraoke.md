---
date: 2026-01-17 21:26
update: 2026-01-20T22:12:26-08:00
comments: "true"
---
# PiKaraoke
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Portable](../02-docker-ratings.md#portable) | [Subfolder](../02-docker-ratings.md#subfolder) |
> | ----- | --- | --------- | -------- | -------- |
> | ❎     | ✅  | ❌🤵       | ✅        | ❌ |
https://github.com/vicwomg/pikaraoke
## Install
Docker Compose
```yml
services:
  pikaraoke:
    image: vicwomg/pikaraoke:latest
    container_name: pikaraoke
    user: ${PUID}:${PGID}
    command: ${command}
    env_file:
      - .env
    environment:
      - TZ=${TZ}
    volumes:
      - /mnt/nvme/share/karaoke:/app/pikaraoke-songs # Songs
      - ./config.ini:/app/config.ini
    restart: unless-stopped
    ports:
      - "5555:5555"
```

Environments 
Configuration options: https://github.com/vicwomg/pikaraoke/wiki
```
youtubedl_proxy=""
url_host=""
command="--headless --youtubedl-proxy ${youtubedl_proxy} --url ${url_host}"
```

- `youtubedl_proxy` - HTTP proxy used for downloading YouTube videos
- `url_host` - the URL to show the QR Code and the application

`config.ini` is used by the app for settings. These are configured via the WebUI, and the file saved locally is for persistence. When bind mounted, the instance will load the config from file.
```ini
[USERPREFERENCES]
disable_score = True
high_quality = True
volume = 1
```
- disable the score at the end
- download high quality YouTube video

## Usage
When starting the karaoke, must have the main screen (TV/Browser) connect to `/splash` before any operations.

>[!warning]
>When the splash page is closed prematurely, the queue's in the song may be skipped, when rejoining.

>[!warning]
>Pikaraoke splash is not multi-session. When another user join splash on another device, the previous session will be ended.

### Adding a Song
![](assets/Pasted%20image%2020260120203622.png)
Click the username at the top right, the browser will prompt for a name.
#### From YouTube
![](assets/Pasted%20image%2020260120203415.png)
1. Search the song
2. Click download, it will download and automatically queue the song

> Note: the search query will be automatically converted to `song name karaoke`, there is no need to to manually add "karaoke, instrumental" to the search query.

>Warning: YouTube download may be slow or rate limited, need to restart Gluetun/Proxy every once in a while.

![](assets/Pasted%20image%2020260120203809.png)

The application also support inputting any YouTube videos via URL. Or use `Include non-karaoke matches`, which will search YouTube as is, without adding karaoke to the query.
#### Local File
The application support both MP3+CDG and video files. As long as it's uploaded to `/app/pikaraoke-songs`. ![](assets/Pasted%20image%2020260120213530.png)

Click `Rescan song directory` to update the library.
The songs will appear in the browser section.
![](assets/Pasted%20image%2020260120213745.png)

>Note: It's possible to edit/trim any imported videos by editing the directly in the pikaraoke folder, as long as the filename is the same, the changes will be reflected.

### Music Management
Go to splash on the main screen.
To queue, for local/downloaded songs, click the queue button next to the song name. Or search YouTube for the song and it will be downloaded.

![](assets/Pasted%20image%2020260120214148.png)
Pikaraoke offers ability to move items up or down.

![](assets/Pasted%20image%2020260120214228.png)
At the homepage, it has the ability to pause or skip the song.
### Manage Library
Under Browse
![](assets/Pasted%20image%2020260120215258.png)
The edit button edit a single song and give options such as rename and delete
- Auto format - rename automatically based on `SONG - ARTIST`

![](assets/Pasted%20image%2020260120215529.png)
The Edit all songs bring up the batch song rename which will use 3rd-party services to get the song and artist name based on filename, and then clicking the checkmark will rename the song.
## Deployment
User simply need to connect to the main app at in order to queue, there is no password, everything is based on trust. The deployment adds additional security with Nginx Proxy Manager without complicated user action or SSO.
- IP whitelisting to local subnet
- blocking access to `/splash` when using the reverse proxy

Due to limitation with guest network, it cannot access LAN devices that's by design. Therefore for guest connecting to this WiFi, a reverse proxy and publicly accessible domain/IP is needed, the router will utilize NAT hairpin to connect to the service. Nginx Proxy Manager
1. under `Access List`, add a new list
2. Add any name
3. in `Authorization`, remove username and password
4. in `Access`, enter the IP range in `allow` section
5. with any proxy host, under `Detail`, change the `Access List` from `Publicly Accessible` to the newly created one.

Custom Location
![](assets/Pasted%20image%2020260120220338.png)

Additional configuration
```nginx
# Make nginx serve our custom page when NPM denies (403)
error_page 403 = /__wifionly/karaoke.html;
error_page 502 = /__splash/splash.html;

# Local files live here
location ^~ /__wifionly/ {
  internal;
  alias /data/html/;
  default_type text/html;
}

location ^~ /__splash/ {
  internal;
  alias /data/html/;
  default_type text/html;
}
```

This is effective, since despite on guest WiFi and NAT hairpin, the router does NAT and to NPM, the source IP address will be the IP of the router. But if anyone tries to access outside of the network (mobile data, VPN, hacker), the IP address will be a public one. The only possible access is for user who are currently joined on guest WiFi or main LAN.
- denied access results in 403 -> `karaoke.html`
- bad gateway 502 -> `splash.html`
	- since in custom location, the `/splash` was proxied to a non-existent port, bad gateway is raised

The `/splash` is only meant to be accessed on the main screen, not client devices, so it's blocked by NPM. Since guest devices are in Guest WiFi and they cannot connect to the main LAN and access the app by direct IP.

### Patch
Due to CORS origin issues with URL, it's not possible to use a different URL (public domain) for QR Code but different URL (local one + port) for WebSocket. Unless this file is changed.
```bash
docker cp pikaraoke:/app/pikaraoke/app.py app.py
```
Edit the [file#L50](https://github.com/vicwomg/pikaraoke/blob/ad9640eb557f91b92a65da85e9489cd5790213a5/pikaraoke/app.py#L50) and change the following 
```python
socketio = SocketIO(async_mode="gevent", cors_allowed_origins="*")
```
```bash
docker cp app.py pikaraoke:/app/pikaraoke/app.py 
```

In the future, a patch specifying a custom QR Code URL may be useful.