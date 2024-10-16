---
date: 2024-10-07 19:48
update: 2024-10-15T21:51:16-07:00
comments: "true"
---
# Authelia Single Sign On (SSO)
> [!info]- [Docker Apps Rating](../02-docker-ratings.md)
> | [U/GID](../02-docker-ratings.md#ugid) | [TZ](../02-docker-ratings.md#tz)  | [SSO/Users](../02-docker-ratings.md#sso) | [Existing FS](../02-docker-ratings.md#existing-fs) | [Portable](../02-docker-ratings.md#portable) | Subfolder| [Mobile](../02-docker-ratings.md#mobile)
> | ----- | --- | --------- | -------- | -------- | ------- | -------- |
> | ❎     | ✅  | ✅👪       | ✅        | n/a | ✅ | ✅ |

Configuration example of Authelia https://gist.github.com/vttc08/cfa1f15c662ccddc1af2dcca3ed7009d
The files regarding ldap and SSO will be placed in the docker folder `authentication` as such
```
├── authelia
│   ├── configuration.yml
│   ├── db.sqlite3
│   ├── notification.txt
│   └── private.pem
├── lldap
│   ├── lldap_config.toml
│   └── users.db
├── auth.env
├── compose.yml
├── oidc.env
```
- a subfolder for each service's configuration and data files
- environments and compose are at the root folder
The authentication stack will have it's own Docker bridge network `auth`
## Secrets
To generate some alphanumeric strings for secret, this command is also set in `bash_aliases` as `secret`.
```bash
tr -dc A-Za-z0-9 </dev/urandom | head -c 24; echo
```

The secrets are stored in `.env` files, alternatively Docker secrets can be used. There are 2 files
- `auth.env` - secrets regarding Authelia and lldap
- `oidc.env` - client secrets for Authelia OIDC supported apps

```js title="auth.env"
DOMAIN_NAME="domain.mywire.org"
BASE_DN="dc=domain,dc=mywire,dc=org"

LLDAP_JWT_SECRET="sdafasdfasdfs"
LLDAP_LDAP_USER_PASS="securepassword"

AUTHELIA_JWT_SECRET="dfasdfasdfasd"
AUTHELIA_STORAGE_ENCRYPTION_KEY="dfsadfsadfasdfsd"

MAILUSER="thepartbefore_gmail_dot_com"
AUTHELIA_NOTIFIER_SMTP_PASSWORD="dsafasdfasdfsadf"

AUTHELIA_SESSION_DOMAIN=${DOMAIN_NAME}
AUTHELIA_AUTHENTICATION_BACKEND_LDAP_PASSWORD=${LLDAP_LDAP_USER_PASS}
AUTHELIA_TOTP_ISSUER=${DOMAIN_NAME}
AUTHELIA_AUTHENTICATION_BACKEND_LDAP_BASE_DN=${BASE_DN}
AUTHELIA_AUTHENTICATION_BACKEND_LDAP_USER="uid=admin,ou=people,${BASE_DN}"

LLDAP_LDAP_BASE_DN=${BASE_DN}
```
```js title="oidc.env"
PORTAINER_SECRET="sdfasdfasdfsad"
ANOTHER_APP_SECRET="dsfasdfasdfasdf"
```
### [lldap Config](#lldap)
- `DOMAIN_NAME` is the full domain name
- `BASE_DN` is the domain name but split by `.`
- `JWT_SECRET` randomly generated secret
- `USER_PASS` the admin password used to login to admin interface 
	- ==Special characters not allowed==
Since some configs such as `DOMAIN_NAME` is shared between Authelia and lldap, it is reused
### [Authelia Config](#authelia)
- `JWT_SECRET`, `ENCRYPTION_KEY` - randomly generated secret
- `MAILUSER` the username before Gmail for SMTP email, in Authelia if `@` is provided in environment variable, it will crash
- `SMTP_PASSWORD` - Gmail app password, [Setup Gmail App Password](#smtp)
- `ANOTHER_APP_SECRET` - for client secret of [OIDC](#oidc)
Authelia configuration options all start with `AUTHELIA`, the full list is [here](https://www.authelia.com/configuration/methods/environment/)
## lldap
https://github.com/lldap/lldap
### Setup
```yaml title="compose.yaml"
  lldap:
    container_name: "lldap"
    image: "nitnelave/lldap:latest"
    restart: unless-stopped
    networks:
      - auth
      - public
    expose: # lldap only needed in the same docker network
      - 3890 # LDAP service
    ports: # can't expose because reverse proxy is running on another server
      - 17170:17170 # Web service
    env_file:
      - auth.env
    environment:
      - UID=1000
      - GID=1001
      - TZ=America/Vancouver
    volumes:
      - ~/docker/authentication/lldap:/data:rw
```
![](../assets/Pasted%20image%2020241008161213.png)
Most of the configuration is already done with [environment variables](#secrets), it is also possible to configure options via `./lldap/lldap_config.toml`.
Given the reverse proxy is located on another server and does not utilize Docker network and Authelia do utilize docker networks. The WebUI port is forwarded while LDAP is not.

The configuration of users and groups are done in WebUI.
- only users in `lldap_admin` is allowed to login and manage users in WebUI
## Authelia
### Setup
```yaml
  authelia:
    container_name: authelia
    image: "authelia/authelia:latest" # optional: pin version for stability
    restart: unless-stopped
    networks:
      - auth
      - public
    ports: # has to be exposed because reverse proxy is running on another server
      - 9091:9091
    env_file:
      - auth.env
      - oidc.env
    environment:
      - PUID=1000
      - PGID=1001
      - TZ=America/Vancouver
      - X_AUTHELIA_CONFIG_FILTERS=template
    volumes:
      - ~/docker/authentication/authelia:/config:rw
```
### Environments
Most of the environment variables and secrets are listed [here](#secrets) and utilize `.env` files.
The environment variable `X_AUTHELIA_CONFIG_FILTER=template` makes it possible to use environment variables in [configuration](#configuration)

- to check the configuration is valid, use this Docker image
```shell
docker exec -it --rm authelia authelia config template --config.experimental.filters template
```
### Files
The folder  `./authentication/authelia` contain all the files

- `configuration.yml` master configuration file, will be autogenerated by Authelia
	- ==MUST BE in `yml` format not `yaml`==
- `notification.txt` created by Authelia, in case [SMTP](#smtp) setup is not possible
- `private.pem` private key pair file required for [OIDC](#oidc)

### Configuration
All the configuration in Authelia is done via `configuration.yaml`. A lot of configurable options are adapted from [EasySelfHost](https://github.com/easyselfhost/self-host/tree/main/docker/authentication).
#### Environment Variables
The configuration can include sensitive values that is stored in [Environments](#environments). This makes it safe to upload to public sites. The syntax are as follows:
```yaml
    - domain:
        - 'auth.{{ env "ENV_NAME" }}'
```
- the variable is templated with `{{ env`
- when parsed this will result in `auth.yourdomain.tld`
#### Use LDAP
```yaml
authentication_backend:
  ldap:
    url: "ldap://lldap:3890"
    implementation: "custom"
    timeout: "5s"
    start_tls: false
    additional_users_dn: "ou=people"
    users_filter: "(&({username_attribute}={input})(objectClass=person))"
    additional_groups_dn: "ou=groups"
    groups_filter: "(member={dn})"
    group_name_attribute: cn
    mail_attribute: mail
    display_name_attribute: displayName
```
#### SMTP
Before enabling SMTP, need to uncomment `filesystem` section in `notifier`
```yaml
notifier:
  disable_startup_check: false
  smtp:
    address: "smtp://smtp.gmail.com:587"
    sender: '{{ env "MAILUSER" }}@gmail.com'
    username: '{{ env "MAILUSER" }}@gmail.com'
```
Gmail app password created at https://myaccount.google.com/apppasswords, requires 2FA on Google account.
#### Sessions
```yaml
session:
  name: "authelia_session"
  same_site: "lax"
  inactivity: "5m"
  expiration: "1h"
  remember_me: "2M"
```
Extend the session so user stay logged in for longer.
### Integrate to Reverse Proxy (Nginx Proxy Manager)
Make a folder in NPM's data folder called `snippets`
https://github.com/easyselfhost/self-host/tree/main/docker/authentication/authelia_snippets

Use these snippets, `proxy.conf`, `authelia-location.conf` `authelia-authrequest.conf`
- for `location.conf` - change the [first line](https://github.com/easyselfhost/self-host/blob/main/docker/authentication/authelia_snippets/authelia-location.conf#L1) to the IP address and port of Authelia
- for `authrequest.conf` - change the [last line](https://github.com/easyselfhost/self-host/blob/main/docker/authentication/authelia_snippets/authelia-authrequest.conf#L25) to the domain of authentication portal
Mount the snippet folder to NPM
```yaml
      - ~/docker/nginx-pm/snippets:/snippets
```

## Providing Access to Apps
The code snippets are for Nginx Proxy Manager only. Other reverse proxies not tested.
### Access_Control
The `access_control` [section](https://www.authelia.com/configuration/security/access-control/) in Authelia define who and which are allowed access.
```yaml
access_control:
  default_policy: "deny"
```
- this is the Authelia default and best option as everything not mentioned will result in 403 also makes it easier to debug
- other policies include `one/two_factor` and `bypass`
- the policies are parsed from top to bottom, so `bypass` rules should be placed first; the rules should go from specific to general
#### Example
```yaml
    - domain:
        - 'files.{{ env "DOMAIN_NAME" }}'
        - 'files.{{ env "DOMAIN_NAME" }}'
      policy: one_factor
      resources:
        - "^.*/api/public/.*" # File Browser bypass rules
        - "^/api([/?].*)?$" # arrs API whitelisting rule
      subject:
        - ['group:admin', 'group:minecraft']
        - 'group:family'
        - 'user:admin'
```

In this example configuration, only the specified are given the `one_factor` login, otherwise the default policy will apply
- access to `files.domain` and only if path contains `/api/` (the resources matching is also useful for bypass rules for APIs)
	- the example above is for `one_factor`, to whitelist APIs use `bypass`
- if the authenticated user belongs to family group **or** belongs to both admin **and** minecraft group
For internal documentation use only. The Authelia environment will have a section for Minecraft friends, family members and bypass rules for anyone.
### Authentication Portal
`auth.domain.tld`
```nginx
location / {
    include /snippets/proxy.conf;
    proxy_pass $forward_scheme://$server:$port;
}
```
### Apps without Auth on Subdomain
`app.domain.tld`
Protect applications (usually single user single session only) without internal authentication or it can be disabled (eg. Radarr, Kasm VNC), more definition [here](../02-docker-ratings.md#sso).
```nginx
include /snippets/authelia-location.conf;

location / {
  include /snippets/proxy.conf;
  include /snippets/authelia-authrequest.conf;
  proxy_pass $forward_scheme://$server:$port;
}
```

### Apps without Auth on Subfolder
`domain.tld/app`
```nginx
include /snippets/authelia-location.conf;

location /baseurl/ {
  include /snippets/proxy.conf;
  include /snippets/authelia-authrequest.conf;
  proxy_pass http://ip:port/;
}
```
If the app require websocket support, use these lines before `proxy_pass`
```nginx
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection $http_connection;
```

### OIDC
[Configure OIDC (OpenID Connect) in Authelia](https://www.authelia.com/configuration/identity-providers/openid-connect/provider/)
```yaml
identity_providers:
  oidc:
    access_token_lifespan: 1h
    authorize_code_lifespan: 1m
    id_token_lifespan: 1h
    refresh_token_lifespan: 90m
    enable_client_debug_messages: false
    enforce_pkce: public_clients_only
    jwks:
      - key: {{ secret "/config/private.pem" | mindent 10 "|" | msquote }}
    cors:
      endpoints:
        - authorization
        - token
        - revocation
        - introspection
        - userinfo
      allowed_origins:
        - https://auth.{{ env "DOMAIN_NAME" }}
      allowed_origins_from_client_redirect_uris: false
```

OIDC require generating a key for `jwks`
```sh
openssl rsa -in private.pem -outform PEM -pubout -out public.pem
```
The private key will be used as in `/config/private.pem`, use bind mounts accordingly
#### Clients
The example configuration for Portainer
```yaml
    clients:
      - id: portainer
        client_name: Portainer
        client_secret: '$plaintext${{ env "PORTAINER_SECRET" }}'
        public: false
        authorization_policy: 'admin_only'
        redirect_uris:
          - 'https://portainer.{{ env "DOMAIN_NAME"}}'
        scopes:
          - 'openid'
          - 'profile'
          - 'groups'
          - 'email'
        userinfo_signed_response_alg: 'none'
```
Every client need an ID, secret (randomly generated). The secrets are loaded from `oidc.env`. Authorization policy can be one/two factor or a [custom policy](#custom_policy). 

Configuring on Portainer side (every clients are different):
- Go to Settings - Authentication - OAuth
![](../assets/Pasted%20image%2020241011170202.png)
The URLs for these are located in `auth.domain/.well-known/openid-configuration`

For clients to use Authelia that natively support OIDC, no special reverse proxy snippet is needed.
#### Custom_Policy
The [OIDC policies](https://www.authelia.com/configuration/identity-providers/openid-connect/provider/#authorization_policies) is different compared to standard [ACL](#access_control).
It is a setting under  `identity_providers` -> `oidc`, the syntax is similar.
```yaml
    authorization_policies:
      admin_only:
        default_policy: 'deny'
        rules:
          - policy: 'one_factor'
            subject: 
            - 'group:admin'
```

- the `admin_only` is the name of the rule will can be used for OIDC clients
- when logging in via OIDC with that rule, all users are not allowed to access except those belonging in admin group whom will get one factor
