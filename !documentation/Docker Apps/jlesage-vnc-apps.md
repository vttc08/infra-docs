---
date: 2023-11-09T04:10:51.000000Z
update: 2024-12-10T23:17:39-08:00
comments: "true"
---
# jlesage VNC Apps

VNC apps consists of [desktop applications](https://jlesage.github.io/docker-apps/) that have the GUI in a web browser, mostly from the creator [jlesage](https://github.com/jlesage?tab=repositories). All such VNC apps follow a setup standard with exception to MegaBasterd, refer to [Exception](#Exception).

## Environments
At least for apps from jlesage, it supports an environment variable. Create an environment file called `vnc.env`

The environment file can be reference in many docker images from jlesage using docker-compose. The current environment variable specify U/GID, time zone and make every app dark mode. It is also possible to set VNC passwords. This is the [full list of environment variables](https://github.com/jlesage/docker-baseimage-gui#environment-variables). For supported apps such as avidemux, there is an option `WEB_AUDIO=1` which allow audio to work.

```yaml
USER_ID=1000
GROUP_ID=1001


KEEP_APP_RUNNING=1
```

The jlesage apps have 2 ports, port 5800 for viewing the VNC app on a web browser on desktop; port 5900 is for VNC protocol that can be used in dedicated VNC viewer or mobile viewing.

#### General Bind Mounts

The appdata bind mount is located in the `~/docker/vnc`, as seen from the yml example, the vnc environment file `vnc.env` is placed in the appdata folder. For application requiring access to movie storage, the bind mount is on the corresponding hard drive or pool. As for applications requiring access to storage but not large media, it's best to put the files on a SSD.

This is an example of VNC container of MKVToolNix. The `vnc.yml` file is backed up elsewhere.

```yaml
    mkvtoolnix:
        image: jlesage/mkvtoolnix
        env_file:
            - ./vnc/vnc.env
        volumes:
            - '/mnt/data/nzbget:/storage:rw'
            - '~/docker/vnc/mkvtoolnix:/config:rw'
        ports:
            - '5820:5800'
            - '5920:5900'
        container_name: mkvtoolnix
```

#### Ports

The application port start from 5800/5900 for its corresponding access and add 10 for each application.
- for apps with high idle CPU or RAM, it's best to run the app on-demand and close it when not used

| App             | Port     | Dialog | Idle CPU | RAM  | Additional Config                                      |
| --------------- | -------- | ------ | -------- | ---- | ------------------------------------------------------ |
| JDownloader     | 5800     |        |          |      | [jdownloader](../Cloud%20VPS/jdownloader.md)           |
| Firefox         | 5810     |        |          |      |                                                        |
| MKVToolNix      | 5820     | gtk    |          |      |                                                        |
| MKVCleaver      | 5840     | QT     | High     |      |                                                        |
| ~~MegaBasterd~~ | ~~5860~~ |        |          |      | [Github](https://github.com/vttc08/megabasterd-docker) |
| MCASelector     | 5870     |        | High     | High | [Github](https://github.com/vttc08/docker-mcaselector) |
| Avidemux        | 5880     | QT     | Med      | Med  | `WEB_AUDIO=1`                                          |

### Files
`/config` is the directory which app configuration are stored and should have the correct permission, there are other additional bind mounts for `/storage` which is the default file choose location for some containers.
- any directory from host can be bind mount into anything in container; however if a directory is not created on host and the container has to create it, it's possible it will be owned by `root`

**QT Based**
Apps that use QT based file explorer (eg. Avidemux) has the configuration stored in `${APP_CONFIG}/xdg/config/QtProject.ini`, this is used to setup file explorer shortcuts.
```ini
[FileDialog]
shortcuts=file:, file:///config, file:///storage, file:///mnt/data/nzbget, file:///mnt/data, file:///mnt/data2
```

**GTK Based**
Apps that use GTK based file explorer (eg. MCASelector) has the configuration stored in `${APP_CONFIG}/xdg/config/gtk-3.0/bookmarks`, this is used to setup file explorer shortcuts.
```
file:///world, file:///storage
```

There are also some application specific setup. For applications accessing hard drive or intensive apps, it is best to stop when not used. [Lazytainer ](https://github.com/vmorganp/Lazytainer)and [ContainerNursery](https://github.com/ItsEcholot/ContainerNursery) and possibly using DNS server can help automate this process.
### Exception
**MegaBasterd**
MegaBasterd is now setup alongside gluetun as a part of WARPStack.