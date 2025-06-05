---
date: 2025-06-04 18:58
update: 2025-06-05T00:06:53-07:00
comments: "true"
---
# Dozzle
> [!info]- [Docker Apps Rating](02-docker-ratings.md)
> | [U/GID](02-docker-ratings.md#ugid) | [TZ](02-docker-ratings.md#tz)  | [SSO/Users](02-docker-ratings.md#sso) | [Existing FS](02-docker-ratings.md#existing-fs) | [Portable](02-docker-ratings.md#portable) | [Subfolder](02-docker-ratings.md#subfolder) |
> | ----- | --- | --------- | -------- | -------- | ------- |
> | 🟨     | 🟨  | ✅👪       | n/a        |✅  | ❌ |

![](assets/Pasted%20image%2020250604233641.png)
## Install
```yaml
services:
  dozzle:
    image: amir20/dozzle:latest
    container_name: dozzle
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - 8020:8080
    environment:
      - DOZZLE_ENABLE_ACTIONS=true
      - DOZZLE_ENABLE_SHELL=true
      - DOZZLE_AUTH_PROVIDER=forward-proxy
    env_file:
      - .env
    secrets:
      - source: cert
        target: /dozzle_cert.pem
      - source: key
        target: /dozzle_key.pem
secrets:
  cert:
    file: ~/docker/dozzle/cert.pem
  key:
    file: ~/docker/dozzle/key.pem
```
Follows [documentation](https://dozzle.dev/guide/getting-started). Changed parts

- `DOZZLE_ENABLE_ACTION` and `DOZZLE_ENABLE_SHELL` set to true allows Dozzle to restart and exec into the container
- `DOZZLE_AUTH_PROVIDER` allows [authelia](Web/authelia.md) support.
- Use Docker secret to load custom TLS keys for Dozzle instances exposed on the internet
## Agents
```yaml
services:
  dozzle-agent:
    image: amir20/dozzle:latest
    container_name: dozzle-agent
    command: agent
    environment:
      - DOZZLE_HOSTNAME=mediaserver
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    ports:
      - 7007:7007
    restart: unless-stopped
```
The bare minimum configuration does not include secrets which needs to be appended manually.

- `DOZZLE_HOSTNAME` determine what it will appear on Dozzle dashboard

> [!warning] All TLS Key or Nothing
> Dozzle can use different TLS certificate rather than the default one for some connection. However, on the main Dozzle instance, if its configured to use custom TLS key, then all the agents that are connected must also use the same key. Either the default self-signed for custom one.

Using a custom key
```bash
openssl genpkey -algorithm Ed25519 -out key.pem
openssl req -new -key key.pem -out request.csr -subj "/C=US/ST=California/L=San Francisco/O=My Company"
openssl x509 -req -in request.csr -signkey key.pem -out cert.pem -days 365
```

When using a custom key, the `key.pem` and `cert.pem` are needed. Even if the instance is exposed on the internet and publicly accessible or scannable, without the custom key, others cannot connect to the instance.

For documentation purpose only. Uses hub and spoke system, the main Dozzle is installed on the server and other server only the agent is installed on it, local or remote VPS.
## Usage
The Dozzle homepage shows overview of all the hosts, CPU/RAM usage and list of containers from all hosts.

On the left, it's all the hosts and to view the logs. For each host it's grouped by Docker compose stacks or individual containers not in a stack. It's the same for grouping log views.
## Authentication
> [!warning] Using Forward Auth Makes Simple HTTP/Port Inaccessible 
> If opting to expose to the internet or make use of Authelia. The simple http:port access is no longer possible, it will show unauthorized since no proxy headers are passed onto it. The only way to access it is via reverse proxy.

The reverse proxy setup is the same as [Apps without Auth on Subdomain](Web/authelia.md#apps-without-auth-on-subdomain), that snippet will work. After applying authelia snippet, Dozzle will recognize the Authelia user that is logged in.

