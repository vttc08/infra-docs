---
date: 2024-11-09 13:45
update: 2024-11-10T19:36:11-08:00
comments: "true"
---
# Aria-NG Downloader
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Existing FS](../02-docker-ratings.md#existing-fs) | [Portable](../02-docker-ratings.md#portable) | [Subfolder](../02-docker-ratings.md#subfolder) | [Mobile](../02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ✅     | ❌  | ❎🤵       | ✅        | ✅ | ❌ | ✔ |

https://github.com/hurlenko/aria2-ariang-docker
## Installation
```yaml
services:
  ariang:
    container_name: ariang
    image: hurlenko/aria2-ariang
    networks:
      - public
    # Port 8080 default
    volumes:
      - ./dl:/aria2/data
      - ./config:/aria2/conf
    # use .env file for secret
    environment:
      - PUID=1000
      - PGID=1001
      - ARIA2RPCPORT=443
    restart: unless-stopped

networks:
  public:
    external: true
```
### Environments
```toml
RPC_SECRET=
EMBED_RPC_SECRET=${RPC_SECRET}
```
The content of `.env`file include password needed to connect to the jsonrpc aria. The embed RPC option also changes the frontend code to automatically fill in secret when it starts up. 
- `ARIA2RPCPORT` is set as 443 for reverse proxy
- if not using reverse proxy, require a port to map to 8080 which is by default what the container images exposes, also set `ARIA2RPCPORT` to the exposed port (if that doesn't work try 8080)

The container also support `BASIC_AUTH_USERNAME/PASSWORD`, or use an external authentication provider such as [authelia](../Web/authelia.md) or reverse proxy.

## Usage
The files are located in `./config`, it include `aria2.conf` for detailed aria configuration. Since ariang is just a frontend, the browser portion is not persistent. Any configuration done on the browser do not get saved to the filesystem.
![](assets/Pasted%20image%2020241110185925.png)
### Downloading
Aria2 support HTTP, and FTP downloads. To download, click New and add a download. For FTP downloads, use the URL in this format.
```toml
ftp://user:pass@url/path/to/file
```
### Troubleshooting
In firefox, clear data and cache or use a private window and errors will likely disappear. Especially after reconfiguring environments/passwords.
## Security
It is possible to put this behind Authelia and whitelist the jsonrpc for third party apps while protecting the web interface. Since the option `EMBED_RPC_SECRET` is used, it will automatically connect to aria2 once web interface load, password on the web interface is required.
### Caddy
The following in Caddy sets a basic authentication password for the main ariang web interface while allowing `/jsonrpc` endpoint for third-party apps.
```
        @aria host aria.{$WEBSITE}
        handle @aria {
                @jsonrpc path /jsonrpc
                handle @jsonrpc {
                        reverse_proxy ariang:8080
                }
                handle {
                        basicauth /* {
                                admin $bcrypthashedpass
                        }
                        reverse_proxy ariang:8080
                }
        }
```
- the Caddyfile uses `basicauth` and a password which needs [bcrypt](https://bcrypt.online/) hashed
- the reverse proxy bypass `jsonrpc` and points to port 8080 in the container
### Tailscale
For internal use without public access, tailscale can be used. For cloud servers using Docker, using the port mapping will override any firewall rules on the server. Binding the tailscale machine IP to the port is needed.
```bash
tailscale ip --4 # 100.100.123.100
```
```yaml
	ports:
	  - 100.100.120.100:8080:8080
```
When accessing via ddns or direct IP is not possible, only possible to access port 8080 with tailscale.