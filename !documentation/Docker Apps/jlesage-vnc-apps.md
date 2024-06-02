---
date: 2023-11-09T04:10:51.000000Z
update: 2024-02-13T02:38:50.000000Z
comments: "true"
---
# jlesage VNC Apps

VNC apps consists of [desktop applications](https://jlesage.github.io/docker-apps/) that have the GUI in a web browser, mostly from the creator [jlesage](https://github.com/jlesage?tab=repositories).

t least for apps from jlesage, it supports an environment variable. Create an environment file called `vnc.env`

The environment file can be reference in many docker images from jlesage using docker-compose. The current environment variable specify U/GID, time zone and make every app dark mode. It is also possible to set VNC passwords. This is the [full list of environment variables](https://github.com/jlesage/docker-baseimage-gui#environment-variables).

```yaml
USER_ID=1000
GROUP_ID=1000
TZ=America/Vancouver
DARK_MODE=1
```

The jlesage apps have 2 ports, port 5800 for viewing the VNC app on a web browser on desktop; port 5900 is for VNC protocol that can be used in dedicated VNC viewer or mobile viewing.

**General Bind Mounts**

The appdata bind mount is located in the `~/docker/vnc`, as seen from the yml example, the vnc environment file `vnc.env` is placed in the appdata folder. For application requiring access to movie storage, the bind mount is on the corresponding hard drive or pool. As for applications requiring access to storage but not large media, it's best to put the files on a SSD.

This is an example of VNC container of MKVToolNix. The vnc.yml file is backed up elsewhere.

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

**Application Port Procedure**

The application port start from 5800/5900 for its corresponding access and add 10 for each application.

JDownloader: 5800

Firefox: 5810

MKVToolNix: 5820

MKVCleaver: 5840

MegaBasterd: 5860 (no VNC viewer 59xx port)

There are also some application specific setup. For applications accessing hard drive or intensive apps, it is best to stop when not used. [Lazytainer ](https://github.com/vmorganp/Lazytainer)and [ContainerNursery](https://github.com/ItsEcholot/ContainerNursery) and possibly using DNS server can help automate this process.

**JDownloader**

[JDownloader Setup](/Cloud%20VPS/basic-server-setup-caddy-docker-jdownloader#bkmrk-configuring-jdownloa "Basic Server Setup, Caddy, Docker, JDownloader")
