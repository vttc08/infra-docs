---
date: 2024-10-05 19:45
update: 2025-06-05T15:16:40-07:00
comments: "true"
---
# VSCode Server
> [!info]- [Docker Apps Rating](02-docker-ratings.md)
> | [U/GID](02-docker-ratings.md#ugid) | [TZ](02-docker-ratings.md#tz)  | [SSO/Users](02-docker-ratings.md#sso) | [Existing FS](02-docker-ratings.md#existing-fs) | [Portable](02-docker-ratings.md#portable) | [Subfolder](02-docker-ratings.md#subfolder) | [Mobile](02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ❎     | ✅*  | ❎🤵       | ✅        | ✅ | ✔ | ✔ |

![](assets/Pasted%20image%2020241007133530.png)
```yaml
services:
code-server:
    image: lscr.io/linuxserver/code-server:latest
    container_name: code-server
    environment:
      - PUID=1000
      - PGID=1001
      - TZ=America/Vancouver
      - DEFAULT_WORKSPACE=/projects #optional
      - DOCKER_MODS=linuxserver/mods:code-server-python3|linuxserver/mods:universal-docker
      - DOCKER_HOST=socket-proxy
    env_file:
      - .env
    volumes:
      # Master configuration
      - ~/docker/code-server:/config
      # dotfiles
      - ~/.bashrc:/config/.bashrc
      - ~/.bash_aliases:/config/.bash_aliases
      - ~/.ssh:/config/.ssh
      - ~/.gitconfig:/config/.gitconfig
      - ~/Documents/ssh:/config/Documents/ssh # ssh keys
      # Workspace folders (eg. Docker, other projects)
      - ~/docker:/docker
      - ~/projects:/projects
      # Linuxserver mod cache
      - ~/docker/code-server/modcache:/modcache
    ports:
      - 4443:8443
    networks:
      - public
      - socket
    restart: unless-stopped

networks:
  public:
    name: public
    external: true
  socket:
    name: socket
    external: true
```

## Setup
The setup follows the same [01-docker-infra](01-docker-infra.md), since this is externally accessible, it has a network of `public`. It also have a network of `socket` to access Docker socket proxy.
### Environments
`DEFAULT_WORKSPACE` - the directory that VSCode will open to when accessing it, defaults to `/config`
The container is Linuxserver so it follows their standards of PUGID and TZ
The Docker Mods will add python3 into the environment for debugging python files.
### env file
```
HASHED_PASSWORD=
```
The environment file should contain the hashed password, use https://argon2.online/ to generate a hashed password.
Although 2FA and SSO is supported, it is still recommended to put another layer of password since VSCode server have access to very sensitive files.
### Directory
The base configuration is stored in `~/docker/code-server` as usual
- the bind mount `/config` is the container is also the `XDG_HOME` which is the default Linux home directory
Given that the config is also the home directory, many dotfiles such as bash, git and SSH configuration need to be bind mounted from the hosts `~` directory into containers `/config` or home directory.

The **workspace** folder contains `docker` (docker configuration and data) and `projects` (cloned from git repo) which are frequently edited files.

Since Linuxserver mods are used, a `modcache` folder is used.
## Usage
The app functions similarly to VSCode and mostly follows the shortcut of the desktop version. Such as ++ctrl+shift+p++ to open command palette.
The app has high idle usage, try to close workspace/sign out and restart after editing, or use solutions to use on-demand.
The app also have access to Github accounts, first clone a private repo and code-server will prompt for login for Github.
### Problems
Official account sync login doesn't work, third party extensions doesn't work either, so the settings has to be done manually.
- for basic configurations `keybindings.json` and `settings.json` contains all the theme and extension settings for a minimal viable VSCode
- the `json` files are periodically copied from main Desktop and synced to the server via Syncthing

Remote SSH doesn't work, but can be solved by [SSH](#ssh) extension.
Github Copilot doesn't work.
Python syntax highlighting doesn't work.
### Extensions
#### SSH
Since the default Remote SSH doesn't work, the extension [SSH FS](https://open-vsx.org/extension/Kelvin/vscode-sshfs) can be used.
![](assets/Pasted%20image%2020241007135406.png)
The configuration is done in `settings.json` and will show up in UI.
```json
"sshfs.configs": [
    {
        "name": "mediaserver-docker",
        "host": "10.10.120.16",
        "username": "karis",
        "privateKeyPath": "/config/Documents/ssh/openssh_keys/mediaserver.key",
        "root": "~/docker"
    },
    {
        "name": "mediaserver-homeassistant",
        "host": "10.10.120.16",
        "username": "karis",
        "privateKeyPath": "/config/Documents/ssh/openssh_keys/mediaserver.key",
        "root": "/srv/homeassistant"
    }
    ],
```
The options from left to right are
- Open Folder - open the folder (configured as `root`) to workspace for editing, for SSH connections outside the network like VPS, the speed is slow
- Open Terminal - start a terminal session to the remote folder
- Settings
- Disconnect - after editing the remote folder, this will remote the remote folder from the workspace
#### Copilot
Copilot Chat and inline chat feature like ++ctrl+i++ doesn't work. But Copilot completion works on some files. Download [Github Copilot Chat](https://www.vsixhub.com/vsix/143611/) and [Github Copilot](https://www.vsixhub.com/vsix/63883/) VSIX file, drag and drop it into VSCode workspace. Then go to extensions > menu > Install from file and the extensions will be installed.
### Docker
To use Docker and manage containers in code-server, the Linuxserver mod  `linuxserver/mods:universal-docker` must be used. It is possible to simply expose the Docker socket volume, but for security, [socket-proxy](https://docs.linuxserver.io/images/docker-socket-proxy) is used. Hence, the environment `DOCKER_HOST=socket-proxy` is needed. Since code-server has access to the proxy because of named Docker network, the DNS name `socket-proxy` is enough. The following permissions need to be granted.
```
NETWORKS POST ALLOW_START ALLOW_STOP ALLOW_RESTART
```
## Reverse Proxy/Authentication
### Reverse Proxy
The app supports both subdomain and subpath for proxying in Nginx Proxy Manager.
### SSO
For Authelia SSO in Nginx Proxy Manager and custom location support.
```nginx
location /vscode/ {
	proxy_set_header Upgrade $http_upgrade;
	proxy_set_header Connection $http_connection;
	include /snippets/proxy.conf;
	include /snippets/authelia-authrequest.conf;
	proxy_pass http://10.10.120.12:4443/;
}
```
This configuration support all of websocket, subpath and authelia. No additional authelia whitelist is needed.

