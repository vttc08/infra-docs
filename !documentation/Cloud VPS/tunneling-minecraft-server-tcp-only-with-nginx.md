---
date: 2023-01-11T05:32:42.000000Z
update: 2025-06-05T00:11:42-07:00
comments: "true"
---
# Tunneling Minecraft Server TCP/UDP Geyser with Nginx
After [setting up the VPS](basic-server-setup-caddy-docker-tailscale.md) and configuring [Tailscale](tunneling-basic-services-jellyfin-web-with-caddy-and-tailscale.md#tailscale). Ensure hosts are connectible via `ping <tailscale-ip>`.

## Nginx
```bash
sudo apt install nginx # Install Nginx
```
Change default port to listen to `81` (this is not needed if another reverse proxy is installed or needed). Edit the `listen 80` to `listen 81`. The line after is not relevant if not using IPv6. In the case of Oracle Cloud, only IPv4 is used.
```bash
sudo nano /etc/nginx/sites-enabled/default
```
```nginx
server {
        listen 81 default_server;
        listen [::]:81 default_server;
```

### Configuration
Edit `/etc/nginx/nginx.conf` add these these `stream` lines
```bash
sudo nano /etc/nginx/nginx.conf
```
```nginx
stream {
     server {
           listen 25565;
           proxy_pass <tailscale_ip>:25565;
    }
    server {
           listen 19132 udp;
           proxy_pass <tailscale_ip>:19132;
    }
}
```
- it is also possible to add `25565 udp`

Reload nginx if required.
```bash
sudo service reload nginx
```
### Firewall
Allow firewall connection. First ensure [firewall-cmd](basic-server-setup-caddy-docker-tailscale.md#port-forwarding) is installed. If not, install the package `firewalld`.
```bash
sudo firewall-cmd --zone=public --add-port 19132/tcp --permanent
sudo firewall-cmd --zone=public --add-port 19132/udp --permanent
sudo firewall-cmd --zone=public --add-port 25565/tcp --permanent
sudo firewall-cmd --zone=public --add-port 25565/udp --permanent
sudo firewall-cmd --reload
```
## Results
In Minecraft client, by typing the public IP address of the Oracle Cloud it will connect. It's also an option to use [Duckdns](https://duckdns.org) to make the cloud IP address more recognizable. 

> The server address is permanent and unchanging.

The **performance** depends on the location of VPS. There will be significant loss in responsiveness if the tunnel VPS is far away from the host server.
![](assets/Pasted%20image%2020240913223835.png)
In this example, the host server is in Vancouver while the VPS is located in Toronto (3500/7000km). The round-trip to connect to the tunneled server added 150ms of latency (from Minecraft mobile app), the speed difference is also visualized in the image above. There is no difference between the `/tps` command as in both cases it's 20 all around.