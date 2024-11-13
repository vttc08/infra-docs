---
date: 2024-07-31 18:51
update: 2024-11-10T18:35:11-08:00
comments: "true"
---
# Custom Caddy Lego
https://github.com/vttc08/caddy-lego
Customized caddy docker container that has Dynu support for wildcard certificates.
## Install
Create a Docker network specific to publicly accessible container.
```bash
docker network create public --subnet 172.80.0.0/16
```

- the Caddy container will have IP address of `172.80.44.3`
```yaml
services:
  caddy:
    image: vttc08/caddy
    container_name: caddy
    ports:
      - 80:80
      - 443:443
    volumes:
      - ~/docker/caddy/Caddyfile:/etc/caddy/Caddyfile
      - ~/docker/caddy/www:/www
    env_file:
      - .env
    environment:
	  - WHITELIST=${WHITELIST}
    networks:
      public:
        ipv4_address: 172.80.44.3
    restart: unless-stopped

networks:
  public:
    external: true
    name: public

```
- the volume of caddy follows all other docker apps which is at `~/docker`
- `.env` file for `DYNU_API_KEY` which will be used for SSL
- create a network `public` with the IP address
- it is not the best idea to use `user:` since it may break container function; however, it all the files are present when mounted Caddy should not change the permissions
- `WHITELIST` is an environment variable that contains the IP address that can be only allowed on certain services
	- this can be created in `~/.bashrc` and sourced
```bash
export WHITELIST=123.456.789.0
```

The content of `.env`
```
DYNU_API_KEY=
WEBSITE=
HTTPS=
EMAIL=
```
- `HTTPS` list of domains so Caddy doesn't error when parsing comma; `"*.website.dynu.com, website.dynu.com"`
- `WEBSITE` just the website name `website.dynu.com`
### Dockerfile
If the provided image doesn't work, need to build a image on the server itself.
``` dockerfile
FROM caddy:2.7.5-builder-alpine AS builder

RUN xcaddy build \
    --with github.com/caddy-dns/lego-deprecated

FROM caddy:2.7.5

COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```
Then modify the `image` part of `compose.yml`
```yaml
    build:
      context: .
      dockerfile: Dockerfile
```
## Caddyfile
```
{
    email {$EMAIL}
}
```
### Basic Website
```
:80 {
        root * /usr/share/caddy
        file_server
}
```
### HTTPS
```
{$HTTPS} {
        tls {
                dns lego_deprecated dynu
        }

        # Standard reverse proxy
        @web host web.{$WEBSITE$}
        handle @web {
                reverse_proxy mynginx:80
        }
}
```
- start with `*.website` to indicate wildcard
- the tls block uses dynu
- declare `@web host` with the subdomain name 
	- this is later used in `handle @web`
	- use `reverse_proxy` block to define the port to be reverse proxied
In this method, only Docker containers that is in the same Docker network of `public` can be reverse proxied. By the internal port and via container names. Tailscale IP entries should also work.
### HTML File Server
If caddy uses bind mount and access to the root of HTML files, it can be file server. First need to create the bind mount in `/www` of the container. Then edit the Caddyfile
```
        @fs host fs.{$WEBSITE}
        handle @fs {
                root * /www
                file_server
                encode gzip
        }
```
### Environment Variables
The previous codeblock already utilize environment variables. The syntax is `{$NAME}`.
### Whitelisting
```
                @blocked not remote_ip {$WHITELIST}
                respond @blocked "Unauthorized" 403
```
This respond 403 unauthorized on any IP addresses not in whitelist.
### HTTP Auth
The option puts a simple HTTP login screen on endpoint.
```json
        handle @secure {
            basicauth {
                admin bcrypthashedpassword
            }
            reverse_proxy ariang:8080
        }
```

## Usage
### Reloading
```bash
docker exec -w /etc/caddy caddy caddy reload
```