---
date: 2023-12-26T04:57:20.000000Z
update: 2024-10-14T23:49:56-07:00
comments: "true"
---
# Filebrowser

Filebrowser app on a web browser, port 4455. o

Docker-compose deployment

```yaml
version: '3.9'
services:
    filebrowser:
        container_name: filebrowser
        image: filebrowser/filebrowser
        ports:
            - '4455:80'
        user: 1000:1001
        restart: unless-stopped
        volumes:
            - '~/docker/filebrowser/.filebrowser.json:/.filebrowser.json'
            - '~/docker/filebrowser/filebrowser.db:/filebrowser.db'
            - '~/docker/filebrowser/config:/config' 
            - '~/docker/filebrowser/branding:/branding'
            - '~/docker:/srv/docker'
            - '/mnt/data:/srv/data'
            - '/mnt/nvme/share:/srv/nvme-share'
```

The first 3 bind mount are for configuration of filebrowser, eg. config, database and branding files. On first deployment, need to create an empty `database.db` file. The remaining bind mount are for the folders that need to be accessed, the folders should be bound under `/srv`. Filebrowser by default create a volume under `/srv`, in this setup where folders are bind mount to subfolders in `/srv` and nothing bind mount directly, it could create a specific volume under docker just for `/srv` which is unavoidable.

Additionally, a `config` folder is mounted, this is a write-accessible folder for both host and filebrowser. Since the [CLI app](https://filebrowser.org/cli) does not work when filebrowser is running, a new database needs to be created but the filebrowser root folder is not write accessible, the config folder allow the database folder to be copied there and changes will be made into that instead. Example of CLI app.
```bash
./filebrowser -d /config/filebrowser.db commands_here
```

This is the content of `.filebrowser.json`

```json
{
    "port": 80,
    "baseURL": "",
    "address": "",
    "log": "stdout",
    "database": "/filebrowser.db",
    "root": "/srv",
    "baseURL": "/baseurl",
  }
```

```yaml
        healthcheck:
            test: ["CMD", "/healthcheck.sh", "||", "exit", "1"]
            interval: 1h
            timeout: 10s
            retries: 2
```
This change makes the healthcheck less aggressive as by default the [healthcheck occurs every 5 seconds](https://github.com/filebrowser/filebrowser/blob/master/Dockerfile#L10).
### Share

The user and share management in filebrowser is simple. The shares have a expiring time, and can optionally have a password. The recipient can view and download files in the share but cannot upload.

### User Management

To create a new user, it's under settings `User Management`, and add a user and password accordingly, and give appropriate permission. The scope is where the root folder where the user have access to, since the docker data folder is bound at `/srv/docker` and /srv is defined as root folder in config, the folder name to put in scopes would be `/docker`. Only one scope is allowed.

![](assets/gallery/2023-12/image.png)

It is also possible to add rules to prevent user access of files within a scope. Under rules, enter the path that is relative to the scope, for example `/docker/minecraft/config` would be `/config`, the default behavior for the folder added is block, unless allow is checked.

![](assets/gallery/2023-12/5lSimage.png)

It is also possible to to add users via [CLI](https://filebrowser.org/cli/filebrowser-users)
```bash
./filebrowser -d /config/filebrowser.db users export config/users.json
```
This will create a json file, create a copy of a user that needs to be duplicated, remove all existing users (because duplicate users cannot be imported), make sure the new user has a unique ID.
```
./filebrowser -d /config/filebrowser.db users import config/users.json
```
After importing, copy the database from `/config` to the root folder.
### Personalization

Enable dark theme - Setting - Global Settings - Branding

- also change the branding directory path to /branding which is bind mount in docker

Under the branding folder, create a file `custom.css`which is used for css customization. Then create a folder img and place logo.svg in it for custom icon. The icon is the same as egow entertainment and stored in OliveTin icon PSD file. Under the folder img, create a folder icons and use [favicon generator site](https://realfavicongenerator.net/) to create an icon archive and put all the content of that archive in the icons folder, the result should look like this.

![](assets/gallery/2023-12/dDRimage.png)

### Proxy/SSO

Reverse proxy is normal procedure using NPM. To add bookmark to a file location, use browser/homepages bookmark function.
#### Authelia
To enable Authelia, it is not possible to do so via configuration file, need to use the CLI app.
First in file browser, create the appropriate users. The users must match the name that is created in Authelia, give admin if necessary. The password doesn't matter when using Authelia. Then use the command to change the database to allow external authentication.
```bash
docker exec -it filebrowser /filebrowser -d config/filebrowser.db config set --auth.method=proxy --auth.header=Remote-User
```
- because of the database situation, copy the temporary database to the main one.

Authelia requires additional whitelisting rules for filebrowser to work properly. The rules works for both subdomain or subfolder.
```yaml
    - domain:
        - 'files.{{ env "DOMAIN_NAME" }}'
      resources:
        - "^.*/api/public/.*"
        - "^.*/share/*"
        - "^.*/static/(js|css|img|themes|fonts|assets)/*"
      policy: bypass
```
- the bypass rule must be placed before the one/two factor rule for it to take effect
#### Subfolder
The subfolder can be done via `.filebrowser.json` and adding `baseurl`, make sure to add `/`. To add the subfolder location, go to Nginx Proxy Manager and advanced config.
```nginx
location /baseurl/ {
  include /snippets/proxy.conf;
  include /snippets/authelia-authrequest.conf;
  proxy_pass http://10.10.120.16:4455/;
}
```
#### SSO Behavior
|                                          | In FB                                      | Not in FB                                       |
| ---------------------------------------- | ------------------------------------------ | ----------------------------------------------- |
| User exists in Authelia                  | Successful login to FB as the correct user | Double login and FB local password doesn't work |
| User not exist/not permitted in Authelia | Forbidden                                  | Forbidden                                       |
For users not in Authelia but exist in FB, they can only login locally (bypass reverse proxy).
User cannot logout if authenticated via Authelia, they cannot access filebrowser at all.