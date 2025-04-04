---
date: 2025-02-25 21:47
update: 2025-02-27T21:34:46-08:00
comments: "true"
---
# Tailscale in Docker
## Tailscale Cloudflare Warp
> [!warning]- When subnet routing to Warp, latency is high
> When tailscale residing in the Gluetun container and tailscale is advertising the routes (provided via GlueTun container) of local network. There will be high latency since all traffic even DNS are routed through Cloudflare and back to local subnet. Only use it when nessecary. It may be possible to change the route settings via API.

