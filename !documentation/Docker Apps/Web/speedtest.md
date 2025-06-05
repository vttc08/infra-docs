---
date: 2025-06-01 21:25
update: 2025-06-05T00:06:03-07:00
comments: "true"
---
# Speedtest
## OpenSpeedTest
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Existing FS](../02-docker-ratings.md#existing-fs) | [Portable](../02-docker-ratings.md#portable) | [Subfolder](../02-docker-ratings.md#subfolder) | [Mobile](../02-docker-ratings.md#mobile) |
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ❎     | ✅  | ✅🤵       | ✅        | n/a | ✅ | ✔ |

![](assets/Pasted%20image%2020250602141656.png)
### Install
Docker-compose
https://github.com/openspeedtest/Speed-Test
```yaml
services:
  speedtest:
    restart: unless-stopped
    container_name: openspeedtest
    ports:
    - '3000:3000' # HTTP Port
    image: openspeedtest/latest
    environment:
      - TZ=America/Vancouver
```

The changed items are `TZ` environment variable. Everything else is from documentation. Default port is 3000.
### Post-Install
To serve OST from a subpath, e.g. `my.dynu/speedtest`. Need to move files in the container, where `openspeedtest` is the name of the container.
```bash
docker exec -it openspeedtest mkdir -p /usr/share/nginx/html/speedtest
docker exec -it openspeedtest cp -r /usr/share/nginx/html/assets /usr/share/nginx/html/downloading /usr/share/nginx/html/upload /usr/share/nginx/html/index.html /usr/share/nginx/html/50x.html /usr/share/nginx/html/speedtest
```
### Usage
OpenSpeedTest comes with additional URL parameter options not found in Librespeed.
```js
?T=D // download only
?T=U // upload only
?R=5&T=U // wait for 5 seconds before upload only
```
### Reverse Proxy
The reverse proxying is straightforward.
If using [Authelia](authelia.md), NPM config must be set to force HTTPS.
Authelia snippet
```nginx
include /snippets/authelia-location.conf;
location /speedtest/ {
  include /snippets/proxy.conf;
  include /snippets/authelia-authrequest.conf;
  proxy_pass http://openspeedtest-ip:3000/;
}
```
## Librespeed
![](assets/Pasted%20image%2020250602155943.png)
### Install
Docker-compose
https://github.com/librespeed/speedtest
```yaml
services:
  speedtest:
    container_name: librespeed
    #image: ghcr.io/librespeed/speedtest:latest
    image: vttc08/librespeed-realip
    restart: unless-stopped
    environment:
      MODE: dual
      IPINFO_APIKEY: ""
      DISTANCE: "km"
      TZ: "America/Vancouver"
    volumes:
      - ./servers.json:/servers.json
    ports:
      - "3001:8080" # webport mapping (host:container)
```
Follow the documentation. Changed container name to `librespeed`, the `MODE` to `dual`, setup both frontend and backend, added timezone settings. The volumes include `servers.json` which is used for [multiserver](#multiserver).  For ipinfo API key, create a token https://ipinfo.io/dashboard/token. Librespeed now uses a custom image which modify Apache configuration and trust the reverse proxy.
### Post-Install
Uses the same command as OST to serve librespeed from subdirectory for reverse proxy.
```bash
docker exec -it librespeed mkdir -p librespeed
docker exec -it librespeed cp -r backend/ favicon.ico index.php speedtest.js speedtest_worker.js librespeed/
```
### Usage
Librespeed do not support URL parameters, just navigate to site and start test.
### Multiserver
Librespeed support setting up multiple backends, via `servers.json`. An array of servers and URLs. It will provide a list of selections. The backend server must be publicly accessible either by port or reverse proxy.
![](assets/Pasted%20image%2020250602163726.png)
```json
[
  {
    "id": 1,
    "name": "Home",
    "server": "http://10.10.120.12:3001/",
    "dlURL": "garbage.php",
    "ulURL": "empty.php",
    "pingURL": "empty.php",
    "getIpURL": "getIP.php"
  },
]
```

The other servers must be installed in backend mode, `MODE=backend` environment. The only thing that needed to be changed is the `server` and incrementing the ID, everything else remains the same.
>[!warning] HTTP/HTTPS
>When accessing the site via HTTP, e.g. `10.10.120.12:3001`, only the servers that is `http` can be selected. Vice versa for HTTPS. Since HTTP frontend is not exposed, when needing to test Oracle Cloud, even if the backend is publicly exposed, VPN is needed to access the HTTP frontend first.

>[!note] HTTPS Slowdown
>When using Caddy on Oracle Cloud VPS with ARM, the speedtest result is significantly slower.
### Reverse Proxy
The procedure is same as OST. Nginx custom snippet. Authelia works as expected.
```nginx
location /librespeed/ {
  include /snippets/proxy.conf;
  include /snippets/authelia-authrequest.conf;
  proxy_pass http://10.10.120.12:3001/;
}
```

For documentation only. The remote VPS also have librespeed installed but have Caddy as reverse proxy. Caddy is used for HTTPS only.
```json
        @librespeed host librespeed.{$WEBSITE}
        handle @librespeed {
                reverse_proxy librespeed:8080
        }
```

- uses container networking and addresses by `container:port`
- when used as such, change the `WEBPORT` environment variable, port mapping is not longer relevant
### RealIP
The following Docker modification makes Librespeed Apache show the original IP address from reverse proxy. Otherwise it will show the gateway IP of the specific Docker network its in.
```Dockerfile
FROM ghcr.io/librespeed/speedtest:latest

RUN a2enmod remoteip && \
    echo 'RemoteIPHeader X-Forwarded-For\nRemoteIPTrustedProxy 172.18.0.1' > /etc/apache2/conf-available/remoteip.conf && \
    a2enconf remoteip
```

- assuming the IP of Docker network is `172.18.0.1` otherwise use a CIDR range

Build and publish the container image (support both AMD and ARM).
```bash
docker buildx create --use --name multiarch-builder
docker buildx inspect --bootstrap
docker buildx build --platform linux/amd64,linux/arm64 \
  -t vttc08/librespeed-realip:latest \
  --push .
```