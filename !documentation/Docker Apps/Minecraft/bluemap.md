---
date: 2024-07-26 15:33
update: 2024-07-30T22:00:14-07:00
comments: "true"
---
# Bluemap
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Portable](../02-docker-ratings.md#portable) | [Subfolder](../02-docker-ratings.md#subfolder) |  [Mobile](../02-docker-ratings.md#mobile) |
> | ----- | --- | --------- | -------- | -------- | ----- |
> | n/a     | n/a  | ❎🤵       | n/a        | ✅ | ✔ |
https://bluemap.bluecolored.de/wiki/

## Installation
Download [bluemap](https://github.com/BlueMap-Minecraft/BlueMap/releases) and place it in minecraft plugin folder, Docker version also available.
### Configuration
Config files are located in `plugins/Bluemap`
Change the line in `core.conf` so the app functions
```conf
accept-download: true
```
- `data: "bluemap"` the data location is not in `plugins` base folder but relative to base folder of the minecraft docker container
	- the default is located in `<docker_mc_folder>/bluemap`
- Default port is 8100, change in `webserver.conf`
#### Resource pack
Add a `.zip` into `plugin/Bluemap/packs`
The `.zip` folder should have on the files in its root folder

- `.zip` -> `resource_pack\` -> `[pack.mcmeta, assets ...]` ==not OK==
- `.zip` -> `[pack.mcmeta, assets ...]` ==OK==
## Markers
To see the changes `docker attach mcserver` then execute `bluemap reload`
### Marker Set
https://bluemap.bluecolored.de/wiki/customization/Markers.html
```json
debug-set: {
          label: "Debug Set"
          toggleable: true
          default-hidden: false
          sorting: 1
          markers: {
             
          }
    }
```

- multiple sets can be added in this format
![](assets/Pasted%20image%2020240726201820.png)
- `label` the name that is will appear (the `debug-set` is just an identifier)
- `sorting` the order which it will appear
### HTML
Marker that shows an HTML element, for example a text label.
```json
 marker-html: {
     type: "html"
     position: { x: -132, y: 72, z: -202 }
     label: "Karis"
     html: "<html code>"
     anchor: { x: 0, y: 0 }
     sorting: 0
     listed: true
     min-distance: 50
     max-distance: 750
            }
```

- `type` set to `html`

HTML Code
```html
<div style='line-height: 1em; font-size: 1.2em; color: black; font-weight: bold; background-color: white; transform: translate(-50%, -50%);'>Karis</div>
```
This HTML code have black text with white background, bolded
![](assets/Pasted%20image%2020240726203018.png)
To have a multiline text, just copy the `<div>` part again
### Line
Marker is a 3D line that can be clicked to show `label` or `detail`, color can be customized.
```json
line-marker: {
      type: "line"
      position: { x: -42, y: 70, z: -340 }
      label: "Text to Display"
      line: [
        { x: -42, y: 70, z: -340 },
        { x: 37, y: 90, z: -325 },
        { x: 102, y: 115, z: -312 }
      ]
      line-color: {r: 255, g: 0, b: 0, a: 1}
      line-width: 3
      detail: "HTML code"
      max-distance: 1500
    }
```
![](assets/Pasted%20image%2020240726204821.png)

- `position` - the starting position
- `line` - array of xyz coordinates (can include starting position)
- `line-color` - RGBA value
- `label` and `detail` will both display the name of the line marker
	- setting anything in detail will override label
It good idea to set the y above the value that is appears on map, if a line is covered by a block, that part of the line will not show.
### POI
 Marker that can be clicked and shows the `label` text, with option to add custom icons.
```json
        poi-marker-1: {
          type: "poi"
          position: { x: 273, y: 62, z: 640 }
          label: "Village Marker 1"
          icon: "assets/poi.svg"
          max-distance: 400
        } 
```
 ![](assets/Pasted%20image%2020240726211823.png)

`icon` - can be any HTML image type
- the default icon size is `50px` as shown in preview
- icons must be stored in `/blue/web/assets` to be used 
- `svg` vector type is preferred over `png` due to small size constraint
	- `svg` created in illustrator need `width="50px" height="50px"` for it to work properly

> [!bug]- Weird behavior with dark mode/different browsers
> On Brave browser mobile dark mode, icons do not show.
> On Chrome Windows, while markers works, the text style such as `bold` do not work
### Shape
Flat, 2D only box that covers an area.
![](assets/Pasted%20image%2020240730212230.png)
```json
        terrain-park: {
          type: "shape"
          label: "Example Shape Marker"
          position: { x: 186, z: -321 }
          shape: [
            { x: 186, z: -321 }
            { x: 184, z: -374 }
            { x: 168, z: -368 }
            { x: 169, z: -316 }
            { x: 186, z: -308 }
          ]
          line-width: 2
          line-color: { r: 255, g: 0, b: 0, a: 1.0 }
          fill-color: { r: 200, g: 0, b: 0, a: 0.3 }
          shape-y: 86
          max-distance: 1400
        }
```
- `shape`, only the x and z values are needed, no height
- `shape-y` the height which the shape appears
	- if there are blocks above the plane of `shape-y`: part of that shape will be covered
	- if there are no blocks below the plane of `shape-y`: the shape will appear floating (refer the image above)
- `color`, has a line and fill component, a fill with `a:` less than 1 decrease the opacity
### Render Distance
![](assets/Pasted%20image%2020240730215818.png)

- for flat view, any view distance below 400 would not show
- as the view distance increase, the icon/html/line will gradually fade out
## Reverse Proxy/SSO
The reverse proxy and authentication setup for subdomain is as usual in Nginx Proxy Manager. App has no built-in authentication so Authelia SSO is supported.
#### Subpath with SSO
=== "Nginx Proxy Manager" 
	The custom locations tab do not work, need to add it manually.
	Go to `Advanced` and edit these in the custom Nginx configuration.
	```
	location /map/ {
		include /snippets/proxy.conf;
		include /snippets/authelia-authrequest.conf;
		proxy_pass http://10.10.120.16:8100/;
	  }
	```
=== "Caddy"
	- Not tested yet 

## Internal Use Only
For public viewer, these parts are not relevant for setup. This is for setup of my specific server and guidelines.

**Ski Slopes**
Red - default color
Black - default color
Green -  `line-color: {r: 40, g: 255, b: 40, a: 1}`
Blue - `line-color: {r: 0, g: 100, b: 200, a: 1}`

**Roads**
Roads- `line-color: {r: 240, g: 220, b: 150, a: 1}`
