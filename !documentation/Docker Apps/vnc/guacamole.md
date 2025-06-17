---
date: 2025-06-09 13:03
update: 2025-06-11T21:43:12-07:00
comments: "true"
---
# Apache Guacamole
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Existing FS](../02-docker-ratings.md#existing-fs) | [Portable](../02-docker-ratings.md#portable) | Subfolder| [Mobile](../02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ❌     | ✅  | ✅👪       | ❌        | 🟨 | ✅ | ❌* |

![](assets/Pasted%20image%2020250611190112.png)
## Install
Credit from another Github project.
https://github.com/boschkundendienst/guacamole-docker-compose
The Docker compose configuration is too long, it will be added to a separate gist.
https://gist.github.com/vttc08/3b866ff4f71ede8d9bb409e58376402e
There are 3 components that needs to be installed
- `guacd` - backend
- `guacdb` - Postgres Database
- `guacamole` - app/frontend
### Configuration
Configure time zone for all containers
Ensure the `.env` file has the following content, this will be loaded by `env_file`
```toml
DOMAIN_NAME="" # domain name of Guacamole, without the BaseURL
GUACAMOLE_STATE="" # used for Authelia authentication
POSTGRES_PASSWORD='' # postgres password
```
Additional changes
```yaml
# guacamole
      RECORDING_SEARCH_PATH: /record
      WEBAPP_CONTEXT: /remote
```

- `SEARCH_PATH` - path for recording, allow Guacamole to view logs of connections
- `WEBAPP_CONTEXT` - subfolder/baseURL for reverse proxy
#### Volume/Network
The volumes `guacdb_postgres` and `guacamole_recording` needs to be named volumes because of host and container permissions. This script also needs to be run to fix permission, if the volume is `guacamole_recording`
```bash
docker run --rm -v guacamole_recording:/path busybox sh -c 'touch /path && chmod a+w /path'
```
```yaml
volumes:
  guacdb_postgres:
    name: guacdb_postgres
    driver: local
  guacamole_recording:
    name: guacamole_recording
    driver: local

networks:
  guacamole_network:
    name: guacamole_network
    driver: bridge
  public:
    name: public
    external: true
```

- `guacamole_network` - network used for 3 containers communication
- `public` - network for reverse proxy is needed
### Prepare
The container from `boschkundendienst` provided a `prepare.sh` script to initalize the database and make folder, the scripts has been modified and is upload to Gist.
## Usage
### App Configuration
Configuration is done in WebUI
> [!danger] Delete `guacadmin` if exposing to public
> The default username and password is `guacadmin`, even when enabling OIDC/Authelia, the normal login will still show for local logins without reverse proxy.
> 

While it's possible to WebUI for config, it's more convenient to have a script that modify the database and sync it with `ssh_config`. The script and associated SQL files will be in the gist.
### Tabby Incompatibility
Because Tabby uses `PS1` from shell variable for seamless SFTP, it will show some weird like `debian@laptopser:urrentDir=/home/debian`, to workaround this. Use the `GUAC` environment variable and load the normal `PS1` is connecting via guacamole
```bash
if [[ "$GUAC" == "1" ]]; then
   PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
   alias eecho='printf "\n%.0s" {1..30}'
fi
```
Additionally add execute command in guacamole.
The `eecho` alias helps with mobile usability with input text, as it scroll down the terminal by typing text. The command prints 30 empty lines.

```bash
export GUAC=1 && bash
```
### Protocols
VNC is possible but unusable on mobile so it's not tested further. RDP will be reserved for future testing.
As for SSH, it works fine on desktop, but on mobile, its recommend to set default input method to Text input. However, in this mode, when the keyboard is activated, the SSH window will scroll up and not possible to scroll, thus it's unable to see the content of SSH messages on top. 
![](assets/Pasted%20image%2020250611212136.png)
This is fixed using an alias that echo 30 empty lines that brings the terminal down, it works even when blindly typing.
```bash
   alias eecho='printf "\n%.0s" {1..30}'
```
### Recording
This is the configuration that is working for recording, from configuration, the recording path is set to `/record`. Use this Docker command to fix permission issues, it will cause no recordings, this is also included in prepare script.
```bash
docker run --rm -v guacamole_recording:/path busybox sh -c 'touch /path && chmod a+w /path'
```
In the WebUI, enable both typescript and screen recording and check record automatically. The path should be
```bash
${HISTORY_PATH}/${HISTORY_UUID}
```
Once configured, each SSH session will be record and viewable in history.
### Sharing
Sharing are determined by profile, it can be read only or collaborative. The script on Gist setup each connection with 2 sharing profile, read only and normal. This give a link and anyone can access it, however, the link will expire once the session is disconnected and a new link need to be generated.
## Access
This configuration allows both Authelia OIDC and local access or default login (as long as `guacadmin` is disabled). 
### Reverse Proxy
In Nginx Proxy Manager.
```nginx
location /remote/ {
	proxy_set_header Upgrade $http_upgrade;
	proxy_set_header Connection $http_connection;
	include /snippets/proxy.conf;
	proxy_pass http://10.10.120.12:8022/remote/;
}
```
- no Authelia snippet is needed since Authelia is used for OIDC not basic login
- this allows serving guacamole on a custom subpath `/remote`

### SSO
These are all the environment that are needed for main guacamole container for OIDC, assuming the `.env` is loaded.
```yaml
      EXTENSION_PRIORITY: '*, openid'
      OPENID_AUTHORIZATION_ENDPOINT: 'https://auth.${DOMAIN_NAME}/api/oidc/authorization?state=${GUACAMOLE_STATE}'
      OPENID_JWKS_ENDPOINT: 'https://auth.${DOMAIN_NAME}/jwks.json'
      OPENID_ISSUER: 'https://auth.${DOMAIN_NAME}'
      OPENID_CLIENT_ID: 'guacamole'
      OPENID_REDIRECT_URI: 'https://${DOMAIN_NAME}/remote'
      OPENID_USERNAME_CLAIM_TYPE: preferred_username
      OPENID_GROUPS_CLAIM_TYPE: groups
      OPENID_SCOPE: openid profile groups email
```
Authelia
```yaml
      - id: guacamole
        client_name: Guacamole
        client_secret: '$plaintext${{ env "GUACAMOLE_SECRET" }}'
        public: false
        authorization_policy: 'admin_only'
        redirect_uris:
          - 'https://{{ env "DOMAIN_NAME"}}/remote'
        scopes:
          - 'openid'
          - 'profile'
          - 'groups'
          - 'email'
        response_types:
          - 'id_token'
        grant_types:
          - 'implicit'
        userinfo_signed_response_alg: 'none'
```
### SSO Behavior
|                                          | In Guac                           | Not in Guac                                  |
| ---------------------------------------- | --------------------------------- | -------------------------------------------- |
| User exists in Authelia                  | Successful login and user mapping | Auto provision user but it has no permission |
| User not exist/not permitted in Authelia | Must login via guac               | Forbidden                                    |

- by default, Authelia logged in users will have no permissions and cannot be managed by guacamole
- if the user need admin, need to configure guacamole and add an admin user before logging in


