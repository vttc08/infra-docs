---
date: 2025-09-25 20:56
update: 2025-09-25T21:13:52-07:00
comments: "true"
---
# Memos
> [!info]- [Docker Apps Rating](02-docker-ratings.md)
> | [U/GID](02-docker-ratings.md#ugid) | [TZ](02-docker-ratings.md#tz)  | [SSO/Users](02-docker-ratings.md#sso) | [Existing FS](02-docker-ratings.md#existing-fs) | [Portable](02-docker-ratings.md#portable) | [Subfolder](02-docker-ratings.md#subfolder) |
> | ----- | --- | --------- | -------- | -------- | ------- |
> | ❎     | ✅  | ✅👪      | ✅        | ✅ | ❌ |

[Memos](https://usememos.com/) is a lightweight, self-hosted, and open-source memo-sharing platform. It's designed for personal knowledge management and quick note-taking, with a focus on simplicity and speed. Key features include:
![](assets/Pasted%20image%2020250925210725.png)
## Install
```yaml
version: '3.9'
services:
  memos:
    user: ${PUID}:${PGID}             # Map container user to host user for permissions
    image: 'neosmemo/memos:stable'    # Use the stable Memos Docker image
    volumes:
      - './memos-data:/var/opt/memos' # Store Memos data in a local 'memos-data' folder
    ports:
      - '5230:5230'                   # Expose Memos on port 5230
    restart: unless-stopped           # Auto-restart container if it stops
    container_name: memos             # Name the container 'memos'
    networks:
      - public                        # Connect to the 'public' network

networks:
  public:
    external: true                    # Use an existing 'public' network
```

## Configuration
On first login, it'll be prompted to ask for a password.
For Dark Mode, go to `Preference` > `Theme`
By default, the database it SQLite, it's only possible to use Postgres.
## Reverse Proxy/Authentication
### Reverse Proxy
Memos only support reverse proxy by subdomain.
### SSO
Memos support OIDC via Authelia. Both in app and Authelia configuration is needed.
https://www.authelia.com/integration/openid-connect/clients/memos/
![](assets/Pasted%20image%2020250925211156.png)

```yaml
      - id: memos
        client_id: 'memos'
        client_name: 'Memos'
        client_secret: '$plaintext${{ env "MEMOS_SECRET" }}'
        authorization_policy: 'one_factor'
        require_pkce: false
        pkce_challenge_method: ''
        redirect_uris:
          - 'https://memos.{{ env "DOMAIN_NAME" }}/auth/callback'
        scopes:
          - 'openid'
          - 'profile'
          - 'email'
        response_types:
          - 'code'
        grant_types:
          - 'authorization_code'
        access_token_signed_response_alg: 'none'
        userinfo_signed_response_alg: 'none'
        token_endpoint_auth_method: 'client_secret_post'
```
