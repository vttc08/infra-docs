---
date: 2024-06-30T18:05:19-07:00
update: 2024-06-30T19:48:30-07:00
comments: "true"
---
# Dynamic DNS Updater Docker
Official Image: https://hub.docker.com/r/linuxserver/duckdns
Custom Github Page: https://github.com/vttc08/docker-duckdns-dynu

This is a docker container that automatically updates the public IPv4 address of the server every 5 minutes to dynamic DNS services Dynu and DuckDNS. It is the fork of Linuxserver DuckDNS container.

### Docker Compose
```yaml
  services:
	  duckdns:
	    image: vttc08/docker-duckdns-dynu:latest
	    container_name: duckdns
	    env_file: ddns.env
	    environment:
	      - TZ=America/Vancouver
	      - PUID=1000
	      - PGID=1001
	    restart: unless-stopped
```

These need to be filled in the `ddns.env`
```bash
DYNU_HOST= # full name of dynu domains
DYNU_PASS= # md5 hashed dynu login pass
SUBDOMAINS= # DuckDNS domains without the duckdns.org part
TOKEN= # DuckDNS token 
```
- token will be visible in DuckDNS dashboard
- Dynu pass is the same as login; alternatively, it is possible to create a [dedicated password](https://www.dynu.com/ControlPanel/ManageCredentials)  just for IP update 
[MD5 generator](https://www.md5hashgenerator.com/)
```bash
echo -n "password" | md5sum
```
- when setting the IP to `10.0.0.0` in Dynu update API, dynu will automatically update the IP address to the IP address making that request

### Other Usage
`docker restart duckdns` will manually run IP update
`docker exec -it duckdns /app/debug.sh` or other scripts, debug script will print out IP address of subdomains resolved by Cloudflare
