---
date: 2025-03-27 18:16
update: 2025-04-03T21:14:55-07:00
comments: "true"
---
# Wireguard
Setup Wireguard from scratch on Linux.

```bash
sudo apt install wireguard wireguard-tools -y
```

This documentation will also focus on exposing private LAN devices. It covers IPv4 only.
## Architecture
While using a fast VPN like CloudFlare WARP will significantly improve bad routes, this only works for services that are **exposed on the internet** via a port forward (e.g. Jellyfin). Or local services and LAN devices not exposed on the open internet, WARP cannot access it, this is usually the job of [tailscale](../Docker%20Apps/Web/tailscale-docker.md) and similar. However, because tailscale is "too good" trying a direct connection, hence the traffic gets throttled. Attempts has been made trying to route tailscale over WARP (which we don't control) and without substantial testing, it's not working as expected.

The approach below attempts to connect to a Oracle Cloud Free Tier VPS [Oracle Cloud VPS](../Cloud%20VPS/basic-server-setup-caddy-docker-tailscale.md) which is fully controllable and unthrottled in order to improve the traffic between home LAN and remote devices. Additionally, this Wireguard tunnel is useful for future CG-NAT situations where a public IPv4 is not possible.

![](assets/Pasted%20image%2020250329231532.png)
The overall design of this architecture is to fix network throttling and routing problems. However, due to distance, this greatly increases latency.
![](assets/Pasted%20image%2020250329232213.png)

The architecture contains 3 devices to setup
- VPS - handling routing of all traffic
- LAN - act as local subnet router
- Client(s) - mobile phones, laptops out and about
## Setup
Wireguard configurations are located in `/etc/wireguard` as `wg.conf` where `wg` is the interface name. The command `wg` and `wg-quick` are used to manage it.

- Wireguard commands and config files editing requires root account
### Prep
Must make sure IP forwarding is turned on all machines. Do so by editing the file
```bash
sudo nano /etc/sysctl.conf
sudo sysctl -p
```
Make sure this line in uncommented and available, reboot if necessary.
```bash
net.ipv4.ip_forward=1
```
### Key
Wireguard uses asymmetric key cryptography, each client needs to public and private key.
```bash
for i in vps lan client; do $(wg genkey | tee $i\_private | wg pubkey > $i\_public); done;
```
Manual
```bash
wg genkey | tee privatekey | wg pubkey > pubkey
```
### VPS
```toml
[Interface]
PrivateKey= # private key of VPS
Address={ipv4} # 10.200.200.1/24
ListenPort=51820
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o $IF -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o $IF -j MASQUERADE

# LAN
[Peer]
PublicKey= # public key of LAN
AllowedIPs= # 10.200.200.2/24, or additional networks

# Client
[Peer]
PublicKey=# public key of client
AllowedIPs= # 10.200.200.3/32
```

- the `Address` is interface is the subnet of the Wireguard interface, it can be anything as long as it doesn't conflict
- `ListenPort` needs to be forwarded in the firewall or it to work
- `PostUp` and `PostDown` are commands to execute when the tunnel is setup
- the LAN subnet CIDR goes in `AllowedIPs` of LAN peer only

Do not forget to replace `$IF` with the real network interface of VPS
### LAN
This is the subnet router on the local network
```toml
[Interface]
Address = # 10.200.200.2/24
PrivateKey = # private key of LAN
PostUp = iptables -A FORWARD -i wgnat -j ACCEPT; iptables -t nat -A POSTROUTING -o $IF -j MASQUERADE
PostDown = iptables -D FORWARD -i wgnat -j ACCEPT; iptables -t nat -D POSTROUTING -o $IF -j MASQUERADE

[Peer]
PublicKey = # public key of VPS
Endpoint = # VPS IP and ListenPort
AllowedIPs = # VPS Wireguard IP, must be a /24 not /32
PersistentKeepalive = 60
```

- `PersistentKeepalive` always send a packet to keep the connection for every interval
- no need to put information of the client, just the VPS

Do not forget to replace `$IF` with the real network interface of LAN device
Additional `iptables` rules are required (install if `iptables` not found). Todo later, make the rule available on startup.
```bash
iptables -A FORWARD -i $WGIF -j ACCEPT
iptables -t nat -A POSTROUTING -o $IF -j MASQUERADE
```
### Client
Any laptop, mobile phone connecting from outside
```toml
[Interface]
Address = # 10.200.200.3/24
PrivateKey = # private key of client

[Peer]
PublicKey = # public key of VPS
Endpoint = # VPS IP and ListenPort
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 60
```

- `AllowedIPs` can also be set to CIDR of LAN subnet and Wireguard interface IP only route local traffic

Use [this website](https://www.wireguardconfig.com/qrcode) to generate QR Code from configuration file.
Use this command to add more clients
```bash
sudo wg set wgIF peer $pubkey_of_client allowed-ips $ip # e.g. 10.0.0.2/32
```
Use `qrencode` package
```shell
qrencode -t ansiutf8 < /etc/wireguard/wgX.conf
```
Save as file
```shell
qrencode -t png -o qrcode.png -r /etc/wireguard/wg-client.conf
```
## Usage
Use `wg-quick` to start the service in VPS and LAN
```bash
wg-quick up wg # name of WG .conf file in /etc/wireguard interface
```
Command for quickly restarting WG interface
```bash
alias wgreset="wg-quick down wg && wg-quick up wg"
```
### Port Forwarding

>[!failure] On Oracle Cloud, only `firewall-cmd` works
>`firewall-cmd` or `firewalld` must be installed on Oracle Cloud VPS, `ufw` or plain `iptables` won't work. It is possible to try Docker. More testing are needed.

The commands for opening ports for `firewall-cmd`
```bash
 sudo firewall-cmd --add-port 1234/udp --zone=public --permanent
 sudo firewall-cmd --reload
```

- replace the port with the `ListenPort` of Wireguard

Here are some of the recommended ports; however, these would be futile again DPI.
- 3478/UDP - STUN protocol, usually for video meeting apps like Zoom, Teams
- 443/UDP - QUIC protocol for web browsing
- 53/UDP - Domain Name System
- 123/UDP - Network Time Protocol

Additional `firewall-cmd` commands may be needed. Reference: [tailscale](https://tailscale.com/kb/1019/subnets#enable-ip-forwarding)
```shell
firewall-cmd --permanent --add-masquerade
sudo firewall-cmd --add-interface=$WGIF --zone=trusted --permanent
sudo firewall-cmd --reload
```

## Reference
https://hacdias.com/2020/11/30/access-network-behind-cgnat/
https://blog.alekc.org/posts/how-to-expose-service-behind-nat-with-wireguard-and-vps/