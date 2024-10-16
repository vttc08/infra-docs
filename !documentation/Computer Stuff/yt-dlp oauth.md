---
date: 2024-09-25 22:56
update: 2024-10-14T23:49:01-07:00
comments: "true"
---

# yt-dlp oauth
Using yt-dlp may need [oauth2](https://github.com/coletdjnz/yt-dlp-youtube-oauth2) plugin in order to use on VPS or download private videos.

## Linux
Download https://github.com/coletdjnz/yt-dlp-youtube-oauth2/releases
Add the zip file into this folder, make it if not exist `mkdir -p`
```shell
~/.yt-dlp/plugins
```
Then run `yt-dlp -v` and make sure `oauth2` appears in the log.

### Setup
```shell
yt-dlp --username oauth2 --password '' https://youtube.com/private-video
```
It will prompt to go to https://www.google.com/device to enter a code.

After registered device, setup `.netrc` and add these contents
```shell
touch ${HOME}/.netrc
chmod a-rwx,u+rw ${HOME}/.netrc
```
```c
machine youtube login oauth2 password ""
```

Now every-time when running the program, must append `--netrc` as an option
```shell
yt-dlp --netrc https://youtube.com/watch?v=private
```

## Window
Similar setup to Linux, except the recommendation location of plugins and `netrc` file
Install the plugins into 
```powershell
$env:appdata/yt-dlp/plugins
```
Similarly, the `.netrc` file can be created in home directory so it's picked up by yt-dlp
```powershell
$env:userprofile
```
