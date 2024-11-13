---
date: 2023-09-23T05:03:35.000000Z
update: 2024-11-12T16:36:51-08:00
comments: "true"
---
# Free Games Claimer

[https://github.com/vogler/free-games-claimer](https://github.com/vogler/free-games-claimer)

This is the Github repo for the new and advanced free games claimer. This is implemented after Epicgames FreeGames keeps failing.

### Configuration

Using Docker-Compose

In the folder structure

```powershell
server: ~/docker/fgc$
./data
docker-compose.yml
fgc.env
```

fgc.env is the environment file for all the password/keys to login to different game services, fill it in manually or use a backup.

```powershell
EG_OTPKEY=
EG_EMAIL=
EG_PASSWORD=
NOTIFY=discord://123456/ABCD
PG_EMAIL=
PG_PASSWORD=
GOG_EMAIL=
GOG_PASSWORD=
TIMEOUT=300
```

`NOTIFY=discord://123456/ABCD` if the webhook looks like this `https://discord.com/api/webhooks/123456/ABCD`

`TIMEOUT=300` sets the timeout to 300s before the container skip and error out due to EpicGames captcha problems. However, the impact on prime gaming and GOG are not tested.

docker-compose.yml

```yaml
services:
  free-games-claimer:
    container_name: FGC # is printed in front of every output line
    image: ghcr.io/vogler/free-games-claimer # otherwise image name will be free-games-claimer-free-games-claimer
    build: .
    user: ${PUID}:${PGID}
    ports:
      - "5990:5900" # VNC server
      - "5890:6080" # noVNC (browser-based VNC client)
    volumes:
      - ~/docker/fgc:/fgc/data
      - ~/docker/fgc/epic-games.js:/fgc/epic-games.js
      - ~/docker/fgc/prime-gaming.js:/fgc/prime-gaming.js
      - ~/docker/fgc/gog.js:/fgc/gog.js
    command: bash -c "node epic-games; node prime-gaming; node gog; echo sleeping; sleep 1d"
    env_file:
      - fgc.env
    restart: unless-stopped

```

This docker-compose file use the environment file `fgc.env` as indicated above and runs once every day. It also contains VNC server/web based client.

### Missing Captcha Session

This should no longer be needed. Edit the line to [epicgames.js](https://github.com/vogler/free-games-claimer/blob/5919d37efaabad98c303e087c4874cffb58b3cb9/epic-games.js#L231) code and replace with the following message. When the captcha is missed, it will send a notification for manual claiming.

```javascript
await notify(`epic-games: got captcha challenge right before claim. Use VNC to solve it manually. Game link: \n ${url}`)
```

<s>EpicGames require a captcha to claim free games. If the 5 minute timeout window for EpicGames is missed, it is no longer possible to claim the games unless waiting for the next day, which due to the nature of discord notifications, there is a slim to none chance of catching the captcha at next day. To continuing claiming after acknowledging the missed session, use portainer, ConnectBot Android to temporarily restart the container to restore VNC session.</s>

<s>In order to restore the default time of claiming the games. Eg. waking up on Thurs or Fri and a predictable time and claim games, use the linux at command.</s>
~~Need to install `at` using `apt`.~~
```bash
at 9:20
> docker restart FGC
> <EOT>
```

<s>This will run the command at 9:20 AM the next day. Ctrl-D to exit at prompt and verify the time is correct.</s>

### Login Session Problem
After not logging in the VNC browser for a long time, it cannot login again, but without VNC in local environment it will work. Need to login locally and copy the files to the Docker server.
- download [Node](https://nodejs.org/en/learn/getting-started/how-to-install-nodejs) and clone repo, configure everything as in remote server
- run `npm install` in the cloned repo and run `node epic-games.js`
- login normally

The app will create `./data` folder in the current directory and a `./browser` folder inside it. Copy the files into the remote server's same location via WinSCP. Permission changes may be required.
```bash
sudo chown -R $PUID:$PGID ./data
rm ./data/browser/compatibility.ini
```
If Firefox error occurs, need to delete the `compatibility.ini` file and the Firefox session should resume normally again.