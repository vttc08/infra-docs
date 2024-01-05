---
date: 2024-01-05T08:56:01.000000Z
update: 2024-01-10T03:07:32.000000Z
comments: "true"
---
# Useful Plugins

**[WorldEdit](https://dev.bukkit.org/projects/worldedit/files)**

[**EssentialX**](https://essentialsx.net/downloads.html)

[**CoreProtect**](https://www.spigotmc.org/resources/coreprotect.8631/)

**[ViaVersions](https://www.spigotmc.org/resources/viaversion.19254/) -** allow other similar version to join the server without conflict

**Offline Mode/Mobile Bedrock**

To allow offline play for PC version. Change `server.properties` and edit these lines

```
enforce-whitelist=false
online-mode=false
```

Refer to [Minecraft Prep and Install](/Docker%20Apps/minecraft-prep-and-install "Minecraft Prep and Install") to install offline client.

For bedrock compatibility, need the geyser plugin.

[**Geyser**](https://geysermc.org/download)

To allows offline play for bedrock mobile version. Go to `./plugins/Geyser-Spigot/config.yml` and change these lines. Do not install the plugin floodgate, if it's installed, removed the plugin. ViaVersions is also needed for mobile play.

```
auth-type: offline
enable-proxy-connections: true
```

Now client can play without login to Xbox or Java.

[**WorldGuard**](https://dev.bukkit.org/projects/worldguard)