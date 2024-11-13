# Docker Setup On Linux Server
## Networking/Environments
By default when mapping a port on Docker, it will bind to all the interfaces, this is fine for home user behind a firewall but not suitable for VPS as all ports will be wide open on the internet. To fix this, only bind to tailscale IP when mapping ports. For convenience, setup PUID and PGID for future container setups.
- put this in the `bashrc` for automatic loading of Tailscale IP variable
- now the docker compose, all the environment variables can be used.

```bash
export TAILSCALE_IP=$(tailscale ip --4)
export PUID=$(id -u)
export PGID=$(id -g)
```
```yaml
	ports:
	  - ${TAILSCALE_IP}:8080:8080
```
## Logs
Change this in `/etc/docker/daemon.json`
```json
{
  "log-driver": "local",
  "log-opts": {
    "max-size": "10m",
    "max-file": 10
  }
}
```
These options limit the max size of each uncompressed log to 10MB and only keep 10 more compressed logs in `.gz` format, in total each container have 100MB of historical data.
The options are useful for container that log a lot and prevent log size on system too large. This will apply to every container, to apply to a single container, use `logging` in the compose file.