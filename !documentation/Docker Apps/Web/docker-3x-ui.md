---
date: 2025-04-19 20:23
update: 2025-04-19T21:50:07-07:00
comments: "true"
---
# 3x-ui V2Ray
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Existing FS](../02-docker-ratings.md#existing-fs) | [Portable](../02-docker-ratings.md#portable) | Subfolder| [Mobile](../02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ❌     | ?  | ❌👪       | ✅        | ✅ | ✅ | ✅ |
https://github.com/MHSanaei/3x-ui
The UI uses Xray for its core.
## Install
Using compose
```yaml
services:
  3x-ui:
    image: ghcr.io/mhsanaei/3x-ui:latest
    container_name: 3x-ui
    volumes:
      - ~/docker/db/:/etc/x-ui/
      - ~/docker/cert/:/root/cert/
    environment:
      XRAY_VMESS_AEAD_FORCED: "false"
      X_UI_ENABLE_FAIL2BAN: "true"
    tty: true
    network_mode: host
    restart: unless-stopped
```

Create the folders in the current folder beforehand
```bash
mkdir db cert
```

## Configuration
![](assets/Pasted%20image%2020250419210643.png)

This is the default configuration
```yaml
Port: 2053
User: admin
Password: admin
Path: /
```

The configuration for the administration are changed under `Panel Settings`
- Port: `General` > `Listen Port`
- Path: `General` > `URI Path`, it can be anything for easy memorization
- User/Pass: `Authentication` > `Admin credentials`
By default the UI is served over HTTP, this is fine for LAN access; but on public access VPS, it's recommended to use a reverse proxy for TLS. Without TLS, the page will show `Security Alert` warning in red.
### LAN Access
To achieve similar level of access as Tailscale for secure LAN access, this must be changed

- `Xray Configs` > `Basic Routing` > `Blocked IPs` and uncheck LAN
## Inbounds
This is where the V2Ray endpoints are added. For the purpose of

- allowing LAN access like Tailscale and Wireguard
- TLS termination via a reverse proxy already running on 443
Only these options are possible, VMESS/VLESS + WebSocket (WS) + TLS
Additional options such as Trojan, Shadowsocks, VLESS + XTLS (Vision or Reality) and more, but these would require additional port forwarding or not compatible with existing reverse proxy setup.

To add a compatible inbound
![](assets/Pasted%20image%2020250419212154.png)
- Protocol: choose either `vless` or `vmess`
- choose any port
- under Transmission, choose `WebSocket`
- change the Path to `/anything`
- do not enable TLS for now

After adding, click the add arrow, and there is a QR Code button, click to copy, it will show a QR code and copy to clipboard. (The QR Code might need to be expanded for 180% for mobile camera to see)
## Reverse Proxy
### Nginx Proxy Manager
Under proxy hosts, add a new one or an existing one and adapt the config to the following
![](assets/Pasted%20image%2020250419212606.png)
- the first page host and port doesn't matter, except **Websockets Support** must be checked
- add the `/anything` path as a custom location and the forwarded port is the same as the one chosen in 3x-ui
	- more VL/Mess path can be added
- under SSL, choose a self-signed cert or one that is verified and enable HTTP/2 
#### Self-Signed
ChatGPT reference: https://chatgpt.com/share/67fa180a-4e28-800b-a7b4-8f379a9d0556
Under Nginx Proxy Manager, `add SSL certificate` and choose `custom`

- the Certificate Key is the **Private Key**
- the Certificate is the **Fullchain File**
### Caddy
The configuration for websocket is straightforward
```nginx
fake.or.real.sni.com {
        tls /usr/local/etc/v2ray/fullchain.pem /usr/local/etc/v2ray/privkey.pem
        reverse_proxy http://localhost:11111
        handle /wp-content {
                reverse_proxy localhost:10181
        }
}
```

- the `handle /path` must match the WS path and port
- `tls fullchain privkey` is only necessary when using a self-signed cert, when using a real name, Caddy will automatically issue certs
## Clients
> [!danger] Self-Signed certs in Android are subject to MITM attacks
> In Windows, self-signed CA can be added to **ROOT** authority while on Android it's only possible as user. Even after installing self signed certs, it's installed as user rather than system. The TLS library in V2RayNG and any other Android app does not trust it. Hence, to use SNI names, the `allowInsecure` must be turn OFF, making it vulnerable to MITM. Only the app developers can fix this. It is unlikely firewalls will willingly MITM whitelisted SNI so this could be safe, but more testing is needed.
### Android V2RayNG
Use the clipboard link. But change the port to 443, and add the appropriate SNI. **Disable allowInsecure is used a fake SNI.**
In the App

- `Settings` > `Does VPN Bypass Lan` -> `Not Bypass`
- `Routing Settings`, and if a rule called `绕过局域网IP`, exists, turn it off.

After configuration, the Android phone on mobile data will be able to access locally hosted services, including UDP traffic like game streaming.
In other Android clients

![](assets/Pasted%20image%2020250419220810.png)
## Backup/Maintenance
In normal 3x-ui, the master `config.json` is located in `/usr/local/x-ui/bin/config.json`, which is the same in Docker, but this is not exposed and doesn't need to be, this the `x-ui.db` is the master file that is needed to recreate everything.
The files created by 3x-ui are owned by root, use `chown` before moving to another server, otherwise, the files can be transferred directly to another server simple by copy/paste. 
## Todo
DNS
**MITM Proof of Concept**
Advanced Routing
iOS apps
Clash/NekoBox
Subscription
Convenience