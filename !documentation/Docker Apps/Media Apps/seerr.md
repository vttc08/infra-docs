---
date: 2026-02-16 00:19
update: 2026-05-01T15:34:13-07:00
comments: "true"
---
# Seerr
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Portable](../02-docker-ratings.md#portable) | [Subfolder](../02-docker-ratings.md#subfolder) |
> | ----- | --- | --------- | -------- | -------- |
> | ❌*     | ✅  | ❌👪       | ✅        | ❌ |
https://docs.seerr.dev/
## Install
```yaml
services:
  seerr:
    image: ghcr.io/seerr-team/seerr:latest
    init: true
    container_name: seerr
    environment:
      - LOG_LEVEL=info
      - TZ=America/Vancouver
      - PORT=5055
    ports:
      - 5055:5055
    volumes:
      - seerr_data:/app/config
    healthcheck:
      test: wget --no-verbose --tries=1 --spider http://localhost:5055/api/v1/status || exit 1
      start_period: 20s
      timeout: 3s
      interval: 15m
      retries: 3
    restart: unless-stopped

volumes:
  seerr_data:
    name: seerr_data
```

- Docker volumes used for permission
- changed healthcheck intervals
## Usage
Follow the onboarding process
- Jellyfin settings
- Radarr settings
### Arrs
Multiple Arrs Server can be added
By default Seerr mark request as monitored
If a movie is added to Seerr, but deleted in Radarr manually, it will still show in Seerr and have to be re-requested
- clear the data first (if the movie is already in a watchlist, must be re-added)
### Status
Request
- 1 = PENDING APPROVAL, 2 = APPROVED, 3 = DECLINED, 5=AVAILABLE/DELETED

Media
- 1 = UNKNOWN, 2 = PENDING, 3 = PROCESSING, 4 = PARTIALLY_AVAILABLE, 5 = AVAILABLE, 6 = DELETED, 7 = DELETED?

>[!warning] Manual Modification (available, deletion)
>When a movie has been marked as available (in Seerr), even if it doesn't exist in Jellyfin/Radarr, it will be marked with status of 5, or available. Later during a scan

**Other Behavior**
If a movie exists in Jellyfin, but has been deleted from disk
- it will be of status `deleted` on the next scan

However to trigger a `deleted` status on movie not available in the library (e.g. for watched media tracking), workaround

Alternative Approach: database?
- better to update the DB
- **requires docker cp and full restart** (stop/start, restart is not sufficient)
- `/app/config/db/db.sqlite3`

```sql
insert into media (mediaType,tmdbId,status,createdAt,updatedAt,lastSeasonChange,mediaAddedAt) values ("movie",347375,7,"2023-01-01 00:00:00","2023-01-01 00:00:00","2023-01-01 00:00:00","2023-01-01 00:00:00");
```
```sql
insert into media (mediaType,tmdbId,status,createdAt,updatedAt,lastSeasonChange,mediaAddedAt) select "movie",7444,7,"2023-01-01 00:00:00","2023-01-01 00:00:00","2023-01-01 00:00:00","2023-01-01 00:00:00" WHERE NOT EXISTs (SELECT 1 FROM media WHERE tmdbId=7444);
```

- parameters: `tmdbId`, date it was watched (use for all 4)
- the 2nd SQL do not insert new value if a key already exist
### States
![](assets/Pasted%20image%2020260313004312.png)

On these events, notifications can be sent, some useful ones include
- pending requests (manual or auto approved)
- when request is available
- when an issue is raised or closed

There are 2 flows of requests processing. It ensures both manual control for admin with unique movie requirements and instant availability for non-technical users.
- for family members flow
	- requests required manual processing and sent to Radarr for immediately processing when approved
	- default location set to movie directory and will download instantly with `Any` profile to optimize fast availability
- for personal admin flow
	- requests are automatically approved but uses a `manual` tag and unmonitored for manual processing
	- default location set to SSD scratch disk ([for more manual processing](https://github.com/vttc08/movie-renamer)), it uses 4K profile and do not auto download
## User Flow
To use Seerr, login to the Seerr account with your Jellyfin username.
![](assets/Pasted%20image%2020260313002320.png)

On the left, the tabs are broken into
- Discover: a overview page that consists of a mixture of popular, trending movies and TV series
- Movies: dedicated section just for movies
- Requests: pending or approve requests you've made

To make a request
- click the `Request` icon and it will be processed
- the request may need manual approval

To raise an issue regarding playback
![](assets/Pasted%20image%2020260313003042.png)
- search for the movie
- click the yellow icon to report issue
- describe and issue and submit
## Scripting
For documentation only, scripts used to integrate with Seerr and Arrs. These are handled via Radarr, not Seerr and not included in documentation. These are Radarr `Connect` manual scripts that occurs when an event has happened, and are placed in Radarr folder. These environment variables are needed (for the Radarr container).
```bash
SEERR_BASE_URL=""
SEERR_API_KEY=""
RADARR_API_KEY=""
```

Automatically delete watchlist items (admin only) and requests once a movie is available, `seerr.py`
- movies that are in watchlist still persist even when it became available
- delete these from watchlist once available

Unmonitor movies in Radarr for requests of specific tags `added.py`
- by default, when Seerr requests, it will be added as monitored
- scripts will trigger on Radarr movie add and change these to unmonitored, but only if `manual` tag has been applied

From [yamtrack](yamtrack.md), import all tracked items as Seerr deleted (status 7)
- use `yamtrack2seerr.py`

## Backup Restore Upgrade
Backing up the volume, specifically the `db.sqlite3` which contains everything.
```bash
docker run --rm -v seerr_data:/data   -v $(pwd)/seerr_data:/backup busybox   /bin/sh -c "tar -czvf /backup/seerr_data.tar.gz /data; chown -R ${PUID}:${PGID} /backup"
```
The result folder structure
```
./seerr_data/seerr_data.tar.gz
```
### Restore
```bash
docker run --rm -v seerr_data:/data -v $(pwd)/seerr_data:/backup busybox /bin/sh -c "tar xvf /backup/seerr_data.tar.gz -C /data --strip-components=1; chown -R 1000:1000 /data"
```

- the `strip-components=1` ensure data is saved to `/data/*` not `/data/data/*` which is require for Seerr to function
- Seerr requires `1000` for UID and GID
### Update
```bash
docker compose pull
docker compose up -d
docker image prune -f
```
## Deployment
Seerr do not support base URL for reverse proxying, a subdomain is needed.
Seerr do not support Authelia or OIDC as of now. Only Jellyfin accounts are allowed.
The process for Nginx Proxy Manager is the same. However, change this after running the site in HTTPS
- `General` > `Application URL`
