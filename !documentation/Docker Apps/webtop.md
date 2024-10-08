---
date: 2024-01-23 08:35
update: 2024-09-09T21:44:11-07:00
comments: "true"
---
# Webtop (openbox-ubuntu)

```yaml
version: "2.1"
services:
  webtop:
    image: lscr.io/linuxserver/webtop:amd64-ubuntu-openbox
    container_name: webtop-openbox
    security_opt:
      - seccomp:unconfined #optional
    environment:
      - PUID=1000
      - PGID=1001
      - TZ=America/Vancouver
      - SUBFOLDER=/ # For reverse proxy
      - TITLE=WebtopMate # The title as it shown in browser
    volumes:
      - ~/docker/webtop/config:/config # default home folder
      - /mnt/data:/mnt/data
      - /var/run/docker.sock:/var/run/docker.sock # Run docker inside docker
    ports:
      - 3050:3000
    shm_size: "1gb" #optional
    restart: unless-stopped
```

The default installation with config folder copied is not usable. Packages to be installed
```python
apt update
apt install wget terminator rsync ntp spacefm compton tint2 nitrogen nano lxappearance mousepad unrar unzip xarchiver mono-complete libhunspell-dev p7zip libmpv-dev tesseract-ocr vlc ffmpeg fonts-wqy-zenhei language-pack-zh-hans mediainfo mediainfo-gui p7zip
```

Packages that has to be installed manually
`lxappearance, spacefm, tint2, nitrogen`

Desktop (tint2, nitrogen)
- nitrogen cannot keep `scaled` option after restarting and needs to change it manually
- nitrogen wallpaper are found in `/config/Pictures/wallpaper.jpg`

### Customization
**lxappearance**
- theme: `Quixotic-blue`; location `.themes`
- icon: `Desert-Dark-icons`; location `.icons`
**tint2**
- tint2 with copied config, located in `.config/tint2`

### Firefox Browser
**policies.json**
```json
// force install ublock, disable annoyances, add bookmarks
{
  "policies": {
    "ExtensionSettings": {
      "uBlock0@raymondhill.net": {
        "installation_mode": "force_installed",
        "install_url": "https://addons.mozilla.org/firefox/downloads/latest/ublock-origin/latest.xpi"
      }
    },
    "NoDefaultBookmarks": true,
    "DisableTelemetry": true,
    "Bookmarks": [
      {
        "Title": "zmk",
        "URL": "https://zmk.pw",
        "Placement": "toolbar"
      },
      {
        "Title": "SubHD",
        "URL": "https://subhd.tv",
        "Placement": "toolbar"
      } // Add more bookmarks like this
    ],
    "FirefoxHome": {
      "Search": true,
      "TopSites": true,
      "SponsoredTopSites": false,
      "Pocket": false,
      "SponsoredPocket": false,
      "Locked": false
    }
  }
}

```
- it is not possible to backup bookmarks on the pinned menu via policies (only way is to restore from home folder)
- it's not possible to remove `import bookmarks` and `getting started` bookmarks with `policies.json` as documented [here](https://mozilla.github.io/policy-templates/#nodefaultbookmarks), it has to be removed manually
**Manual Configs**
- ublock add Chinese filter
- pin bookmarks
- remove default bookmarks and getting started from toolbar
### Files

SpaceFM
- upon installing, with config copied over, everything works fine
- configuration is stored in `~/.config/spacefm`

Movie-Renamer Script
- works after copying

### Subtitles
#### Subtitle Edit
Install [dependencies](https://www.nikse.dk/subtitleedit/help#linux)
Download subtitle-edit
```bash
curl -s https://api.github.com/repos/SubtitleEdit/subtitleedit/releases/latest | grep -E "browser_download_url.*SE[0-9]*\.zip" | cut -d : -f 2,3 | tr -d \" | wget -qi - -O SE.zip
unzip SE.zip -d /config/subtitle-edit
```
Subtitle-Edit Dark theme has to be changed manually
- `Options` -> `Settings` -> `Appearance` -> `Use Dark Theme`
- `Options` -> `Settings` -> `Syntax Coloring` -> `Error color` and change to `27111D`
- `Options` -> `Settings` -> `Appearance` -> `UI Font` -> `General` and change to `WenQuanYi Zen Hei`
## Obsidian Webtop

Make sure to close everything in Obsidian to reduce CPU usage.

```yaml
services:
  obsidian:
    image: lscr.io/linuxserver/obsidian:latest
    container_name: obsidian
    security_opt:
      - seccomp:unconfined #optional
    environment:
      - PUID=1000
      - PGID=1001
      - TZ=America/Vancouver
      - SUBFOLDER=/obsidian/
      - TITLE=Obsidian
    volumes:
      - ~/docker/obsidian-webtop:/config
      - ~/Documents/notes:/notes
    networks:
      - public
    ports:
      - 3010:3000
    devices:
      - /dev/dri:/dev/dri
    shm_size: "1gb"
    restart: unless-stopped

networks:
  public:
    name: public
    external: true
```

- standard procedure for PUGID, TZ and docker networks
- optional environment variable `PASSWORD` for HTTP basic auth
- `SUBFOLDER` can be used for reverse proxy with custom location
### Authentication
Setup of webtop with Authelia require more configurations. Needs to manually configure the custom location in Nginx Proxy Manager just like [bluemap](Minecraft/bluemap.md).
```nginx
location /obsidian/ {
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection $http_connection;
  include /snippets/proxy.conf;
  include /snippets/authelia-authrequest.conf;
  proxy_pass http://10.10.120.12:3010/obsidian/;
}
```

- the `proxy_set_header` lines are required because of websocket

Authelia configuration (need whitelist VNC assets)
```yaml
    - domain: "basedomainforsubfolder.mywire.org"
      resources:
        - "socket.io/*"
        - "public/*"
        - "vnc/*"
      policy: bypass
    - domain: "basedomainforsubfolder.mywire.org"
      policy: one_factor

```

