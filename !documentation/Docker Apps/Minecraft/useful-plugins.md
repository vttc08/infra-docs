---
date: 2024-01-05T08:56:01.000000Z
update: 2026-03-11T13:01:33-07:00
comments: "true"
---
# Useful Plugins

**[WorldEdit](https://dev.bukkit.org/projects/worldedit/files)**

[**EssentialX**](https://essentialsx.net/downloads.html)

[**CoreProtect**](https://www.spigotmc.org/resources/coreprotect.8631/)

**[ViaVersions](https://www.spigotmc.org/resources/viaversion.19254/) -** allow other similar version to join the server without conflict

**[bluemap](bluemap.md)**

[**Geyser**](https://geysermc.org/download)

[**WorldGuard**](https://dev.bukkit.org/projects/worldguard)

### Offline Mode/Mobile Bedrock
To allow offline play for PC version. Change `server.properties` and edit these lines
```
enforce-whitelist=false
online-mode=false
```
Refer to  [Minecraft Prep and Install](minecraft-prep-and-install.md) to install offline client.

For bedrock compatibility, need the geyser plugin.

To allows offline play for bedrock mobile version. Go to `./plugins/Geyser-Spigot/config.yml` and change these lines. Do not install the plugin floodgate, if it's installed, removed the plugin. ViaVersions is also needed for mobile play.

```
auth-type: offline
enable-proxy-connections: true
```

Now client can play without login to Xbox or Java.

## Client Plugins
### Litematica
Litematica is a client side plugin that allows you to save and load schematics of your build. It must be installed using Fabric.

Install official Minecraft client: https://fabricmc.net/
Install on MultiMC: https://wiki.fabricmc.net/player:tutorials:install_multimc:windows

Here are the following Java client files needed (choose the correct client e.g. 1.21.11)
- [Fabric API](https://modrinth.com/mod/fabric-api/versions?g=1.21.11)
- [Litematic Main Plugin](https://modrinth.com/mod/litematica/versions?g=1.21.11&l=fabric)
- [MaLiLib](https://modrinth.com/mod/malilib/versions?g=1.21.11&l=fabric)

These files need to be placed in
```batch
%appdata%\.minecraft\mods
```

### Litematica Usage
1. Use a stick
2. **CTRL-Scroll** to switch modes

Area Selection (1/9)
- works the same as world edit, left and right click
- use **ALT-Scroll** to expand/contract selection
- use **Middle Click** to select which corner to move

Once the area has been selected, press ++M++ to load the manager
- `Area Editor`
- save schematic and provide a name

Paste Schematics (5/9)
- press ++M++ and `Load Schematics`
- the schematics will be placed  as ghost

Require configurations