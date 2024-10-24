---
date: 2024-10-17 23:36
update: 2024-10-23T23:51:28-07:00
comments: "true"
---
# SponsorBlock API Mirror Server
> [!info]- [Docker Apps Rating](02-docker-ratings.md)
> | [U/GID](02-docker-ratings.md#ugid) | [TZ](02-docker-ratings.md#tz)  | [SSO/Users](02-docker-ratings.md#sso) | [Existing FS](02-docker-ratings.md#existing-fs) | [Portable](02-docker-ratings.md#portable) | [Subfolder](02-docker-ratings.md#subfolder) | [Mobile](02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ❌    | ❌  | n/a       | ❌*        | 🟨 | n/a | n/a |

>[!failure]+ #1 Sponsorblock Mirror Servers Usability and Extensibility is Crippled b/c of Clients
>Almost all relevant clients utilizing SponsorBlock (ReVanced, NewPipe, Extension, FreeTube, SmartTube) uses hash lookup. Where the client sha256 hashes the videoID then lookup from the server, the server then return all videoIDs that matches the first 4 letters of the hash. There could be hundreds of videos that has matching hash, it is impossible for the server to know the videoID requested. While it improves "pRiVaCy", it severely degrades functionality. What if the database does not contain sponsor segments for a video? The server can't do anything about it. Client behavior should not be modified because many clients exists and written in different language, it's not feasible to modified all clients and have all of it up-to-date. For the mirror to be useful whether main SponsorBlock server is down or not, **the database must contain every single submission for all the video that ever existed and updated in real-time**. Which is not possible as in #2 and #3. 
>![](assets/Pasted%20image%2020241023161925.png)

>[!failure]- #2 This Server Works in Reverse
>The server first queries the local database for video data, and only queries the main server if no data is found. This works well for `videoID` queries but causes issues with hashed `videoID`.
>
>For example, suppose Video A has `videoID` `aabbcc` and Video B has `videoID` `112233`, and both videos have sponsor segments. Video A's segments are in the local database, while Video B's segments are only on the main server (due to great difficulty in syncing database in #3). Both video hashes start with `abcd`, the client querying for Video B (`/api/skipSegments/abcd`) will get nothing. Since data is found when the server searches for `abcd`, the server doesn't query the main server for Video B's segments, returning incomplete results.
>
>The better option is to query the main server first since it's the most accurate, then lookup the local database when the main server is down. This increase the usefulness and accuracy of the mirror server.
>![](assets/Pasted%20image%2020241023164629.png)

>[!failure]- The sb-mirror Project or Rsync is not Incremental nor Consistent Making it Difficult to Sync Data (extensive testing required)
>The submitted SponsorBlock segments are periodically dumped in a very large (4GB) csv file. CSV text based files are not easy for machine to process. It also takes a long time to import to the compatible Postgres database (500-800s). Other have proposed the solution of rsync using `sb-mirror`, but that is problematic too. There are only 2 rsync providers `sponsorblock.kavin.rocks` and `sponsor.ajay.app` official. The one provided by `kavin` does not appear to be updated or the timestamping is broken. The official one is the most accurate and updated frequently. However, it is slow and inconsistent. It constantly have issues such as 200 max limit reached, when it did connect, the speed is 300-1000 kbps, which takes hours to sync `sponsorTimes.csv`. While rsync can be incremental, `sponsorTimes.csv` is not, every time it updates, the whole thing has to be downloaded. Again... Fast updates are impossible due to connection limits and slow speed and a huge amount of bandwidth is used because of non-incremental updates.
>
>The way SponsorBlock clients function in #1 require the mirror server to have everything that ever existed and updated frequently. The current way of `.csv` dumps are inefficient and not practical.

> [!tip]- Modified Approach and Other Compromises
> The project in this documentation uses a modified approach. It uses another mirror `sb.minibomba.pro`, while it still requires downloading every time it updates, the server is much faster and provided 1GB compressed files (takes only 2 min to download). Instead of importing everything in the DB which is intensive, this approach query the existing DB and get the latest timestamp, then filters the new csv file for entries above that timestamp, create a diff and import into database; the whole compute takes 15s. It will import any new segments in the new csv file, but older entries that was updated will not be reflected. A full DB reset is performed every week for clean start. This is a compromise, others include
> - mirror server cannot provide non-sponsor segments (selfpromo, intros etc..)
> - any disruptions to the mirror server will trigger full DB rebuild
## gosb
Simple implementation of SponsorBlock in Go.
https://github.com/wereii/gosb
Not working 404
## SponsorBlock Mirror
https://github.com/TeamPiped/sponsorblock-mirror
Rust implementation of mirror server. It consists of 3 services

- Mirror server
- Postgres database
- ~~- Rsync Mirror~~

### Configuration
```yaml
  postgres:
    image: postgres:16-alpine
    container_name: postgres-sb-mirror
    shm_size: 1g
    volumes:
      - ~/docker/sponsorblock/db:/var/lib/postgresql/data
      - ~/docker/sponsorblock/mirror:/mirror
    env_file:
      - .env
    restart: unless-stopped

  sponsorblock-mirror:
    image: 1337kavin/sponsorblock-mirror:latest
    container_name: sponsorblock-mirror
    user: 1000:1001
    volumes:
      - ~/docker/sponsorblock/mirror:/app/mirror
    ports:
      - 6969:8000
    restart: unless-stopped
    depends_on:
      - postgres
```
Content of `.env` contains
```python
POSTGRES_DB=sponsorblock
POSTGRES_PASSWORD=
POSTGRES_USER=sponsorbl
```

### DB Dumps
The dumps are stored locally at  `./mirror/sponsorTimes.csv`
#### HTTP/Manual
https://wiki.sponsor.ajay.app/w/API_Docs
https://sb.ltn.fi/database/ ~ up to 1 week delay
https://sb.minibomba.pro/mirror/ ~ 3hrs delay
#### Rsync
```shell
rsync --list-only rsync:///rsync.sponsor.ajay.app:31111/sponsorblock
rsync --list-only rsync://sponsorblock.kavin.rocks/sponsorblock
```
### Behavior
It's not ready to test the resiliency of server when SponsorBlock goes down yet.
It is not feasible to use this in restricted network where dynamic DNS are blocked unless used via tailscale exit node.

| Main Server (row) / CSV (col) | segment exist        | does not exist                                                                                                                                                                                                                                                                   |
| ----------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| segments exist                | CSV takes precedence | depends, if there is not another video that has the first 4 letters of sha256 that exist in database -> **query main server for segments**; if there is another video id that has the same sha256 as this one and that exist in the database -> **no segments will be provided** |
| does not exist                | CSV segments         | no segments                                                                                                                                                                                                                                                                      |

For the server to be useful, it must have an up-to-date csv dump.
Any interruptions to the mirror server container will trigger a full database re-import which could take a long time.
- eg. reboot host, reboot/start container, container crash
- the re-import require 2x the database storage, the database will be shrunk once import is done
- for a 4.5GB csv file, the Postgres takes up 8.5GB space.
### Postgres
To execute Postgres commands.
```sh
docker exec -it postgres-sb-mirror psql -U sponsorblock
```

The following SQL will manually add an entry to the database, any updates to the database is immediate.
```sql
INSERT INTO "sponsorTimes" 
("videoID", "startTime", "endTime", "votes", "locked", "incorrectVotes", "UUID", "userID", "timeSubmitted", "views", "category", "actionType", "service", "videoDuration", "hidden", "reputation", "shadowHidden", "hashedVideoID", "userAgent", "description")
VALUES 
('videoID', 699.111start, 893.201end, 10, 0, 0, 'UUID', 'userID', 1658232826797, 0, 'sponsor', 'skip', 'YouTube', 3839.661duration, 0, 0, 0, 'hashedvideoID', 'psqlmirror/v4.6.4', '');
```
- `videoID`, `startTime`, `endTime`, `timeSubmitted` are configurable
- `hashedVideoID` is required and can be generated from the `videoID` in sha256
- `UUID` is required and has to be unique
- the attributes `shadowhidden`, `hidden` and `locked` must be 0

When manually importing, if there are overlapping sponsorship entries, the entry that have the longer end time will take precedence, not the one that is imported last.
### SB Mirror
```yaml
  sb-mirror:
    image: mchangrh/sb-mirror:latest
	user: 1000:1001
    environment:
      - MIRROR_URL=mirror.sb.mchang.xyz # override to set upstream mirror
    volumes:
      - ./mirror:/mirror
```
For additional options: https://github.com/mchangrh/sb-mirror
Although rsync is used, the transfer is not incremental, hence downloading from a fast compressed archive is preferred. eg. `sb.minibomba.pro`
### Modified Implementation
The following modifications drastically speed up database refresh (from 500-800s to 10-15s) excluding download. It only import new entries (after the last database update). The [full implementation is a bash script](https://gist.github.com/vttc08/c179e959255381a30f9ccd7b924a64dc) that can be automated using crontab, OliveTin or Home Assistant.

Download and extract the database (use `aria2` for even faster downloads)
```sh
wget https://sb.minibomba.pro/mirror/sponsorTimes.csv.zst
zstd -d sponsorTimes.csv.zst -o sponsorTimes.new.csv
rm sponsorTimes.csv.zst
```
```shell
sudo apt install aria2 -y
aria2c -x 10 https://sb.minibomba.pro/mirror/sponsorTimes.csv.zst
```

Find the latest item's time submitted in Postgres
```shell
docker exec -it postgres-sb-mirror psql -U sponsorblock -d sponsorblock -t -c 'SELECT "timeSubmitted" FROM "sponsorTimes" ORDER BY "timeSubmitted" DESC LIMIT 1;' | tr -d '[:space:]'
```
- this also trim whitespace

Create the diff
```sh
awk -F, -v val="$val" '$9 > val' sponsorTimes.new.csv | grep -v "hashedIP" > diff.csv
```
- command also remove entries with `hashedIP` which can create errors with `awk` and the import

Import the difference
```sh
docker exec -it postgres-sb-mirror psql -U sponsorblock -d sponsorblock -c 'COPY "sponsorTimes" FROM '\''/mirror/diff.csv'\'' WITH (FORMAT csv, HEADER true);'
```

Cleanup
```shell
mv sponsorTimes.new.csv sponsorTimes.csv
rm diff.csv
```
### Future Considerations
Reverse the server logic, first query the official SponsorBlock server, if it times out, then lookup the database.
Script/program that utilize YouTube RSS feed, subscriptions or other libraries to get the sponsor segments from popular or channels that is most likely to be watched more frequently and update the database.