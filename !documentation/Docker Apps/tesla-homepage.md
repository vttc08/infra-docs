---
date: 2023-08-31T00:21:38.000000Z
update: 2023-12-03T04:37:33.000000Z
comments: "true"
---
# Tesla Homepage

This is a homepage that allows Tesla browser to enter full screen mode.

Docker-compose

```yaml
services:
  homepage-for-tesla:
    image: jessewebdotcom/homepage-for-tesla:latest
    container_name: homepage-for-tesla
    environment:
      - DEFAULT_THEME=13
    volumes:
      - ~/docker/tesla/public/bookmarks.json:/app/public/bookmarks.json
      - ~/docker/tesla/public/images:/app/public/images
    ports:
      - "3000:3000"

```