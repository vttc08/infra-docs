---
date: 2022-11-10T02:24:02.000000Z
update: 2024-06-01T18:03:26-07:00
comments: "true"
---
# Bookstack

## **Installation**

Change port to **6975**

Add in docker-compose: **restart: unless-stopped**

$docker directory = /home/docker .... etc

Docker-Compose file reference

[https://github.com/solidnerd/docker-bookstack/blob/master/docker-compose.yml](https://github.com/solidnerd/docker-bookstack/blob/master/docker-compose.yml)

```yaml
version: '2'
services:
  mysql:
    image: mysql:8.0
    environment:
    - MYSQL_ROOT_PASSWORD=secret
    - MYSQL_DATABASE=bookstack
    - MYSQL_USER=bookstack
    - MYSQL_PASSWORD=secret
    volumes:
    - mysql-data:/var/lib/mysql
    restart: unless-stopped

  bookstack:
    image: solidnerd/bookstack:22.10.2
    depends_on:
    - mysql
    environment:
    - DB_HOST=mysql:3306
    - DB_DATABASE=bookstack
    - DB_USERNAME=bookstack
    - DB_PASSWORD=secret
    #set the APP_ to the URL of bookstack without without a trailing slash APP_URL=https://example.com
    - APP_URL=http://xxx.xxxmydomainxxx.duckdns.org
    volumes:
    - $docker/public-uploads:/var/www/bookstack/public/uploads
    - $docker/storage-uploads:/var/www/bookstack/storage/uploads
    ports:
    - "6975:8080"
    restart: unless-stopped
```

**Notice:** The default password for bookstack is

<admin@admin.com>

password

**Permissions**: remember the set write permission on public-uploads folder so users can upload photos.

## **Backup and Restore**

Files Backup:

```shell
tar -czvf bookstack-files-backup.tar.gz public-uploads storage-uploads
```

Restore:

```shell
tar -xvzf bookstack-files-backup.tar.gz
```

Database backup:

```shell
sudo docker exec bookstack_mysql_1 /usr/bin/mysqldump -u root --password=secret bookstack > ./bookstack/bookstack_db.sql
```

Restore:

```shell
sudo docker exec -i bookstack_mysql_1 mysql -u root --password=secret bookstack < /$docker/bookstack/bookstack_db.sql
```

- bookstack\_mysql1 is the container name
- password is secret or the database password

### **Reverse Proxy**

Use subdomain in proxy manager.

**Backing Up and Restoring with LinuxServer.io container**

Due to limits or Oracle Cloud free tier. The only arm image is from linuxserver io container, and it is different than solidnerd image.

Docker-Compose file

```yaml
version: "2"
services:
  bookstack:
    image: lscr.io/linuxserver/bookstack
    container_name: bookstack
    environment:
      - PUID=1001
      - PGID=1001
      - APP_URL=https://wiki.xxx.duckdns.org
      - DB_HOST=bookstack_db
      - DB_USER=bookstack
      - DB_PASS=secret
      - DB_DATABASE=bookstackapp
    volumes:
      - /home/ubuntu/bookstack:/config
    ports:
      - 6975:80
    restart: unless-stopped
    depends_on:
      - bookstack_db
      
  bookstack_db:
    image: lscr.io/linuxserver/mariadb
    container_name: bookstack_db
    environment:
      - PUID=1001
      - PGID=1001
      - MYSQL_ROOT_PASSWORD=secret
      - TZ=Europe/London
      - MYSQL_DATABASE=bookstackapp
      - MYSQL_USER=bookstack
      - MYSQL_PASSWORD=secret
    volumes:
      - /home/ubuntu/bookstack:/config
    restart: unless-stopped

```

<span style="color: rgb(224, 62, 45);">Notice: In Oracle cloud free tier, the default ubuntu user is 1001, not 1000. For database name, it it <span style="text-decoration: underline;">bookstackapp</span>, keep in mind when executing restore command. The folder structure is also different. In the solidnerd container, the images are stored at /public-uploads while in LSIO container it is stored at /www/uploads</span>

### **Backing Up (from home PC)**

Images

cd into /public-uploads and make a tar archive

```shell
tar -czvf images.tar.gz images
```

Backup the database

```shell
sudo docker exec bookstack_mysql_1 /usr/bin/mysqldump -u root --password=secret bookstack > ./bookstack_db.sql
```

Transfer to Oracle Cloud Server

```shell
scp -i oracle-arm-2.key images.tar.gz bookstack_db.sql ubuntu@$IPADDR:/home/ubuntu/bookstack/www/uploads
```

Take in consideration the location where LSIO image stores the images.

### **Restore (into Oracle Cloud)**

Images (/home/ubuntu/bookstack/www/uploads)

```shell
tar -xvzf images.tar.gz
```

**Database**

The image url in the database still refers to old server url, it needs to be changed. The following command replace the subdomain in the sq1 dump.

```bash
sed -i 's/wiki.$home.duckdns.org/wiki.$oracle.duckdns.org/g' bookstack_db.sql
```

**Restore the database.**

```bash
sudo docker exec -i bookstack_db mysql -u root --password=secret bookstackapp < /home/ubuntu/bookstack/www/uploads/bookstack_db.sql
```

### **Crontab**

On Home PC

```bash
0 23 * * 2,5 /home/karis/bookstack.sh
```

```bash
#!/bin/bash

cd ~/docker/bookstack/public-uploads #location of bookstack public uploads
tar -czvf images.tar.gz images
sudo docker exec bookstack_mysql_1 /usr/bin/mysqldump -u root --password=secret bookstack > ./bookstack_db.sql
scp -i oracle-arm-2.key images.tar.gz bookstack_db.sql ubuntu@$ORACLEIP:/home/ubuntu/bookstack/www/uploads
```

Make sure to copy the oracle-arm-2.key to the appropriate location (~/docker/bookstack/public-uploads)

**Also make sure the permission of oracle-arm-2.key is in correct permission (600). Especially changing the permission of public-uploads folder to allow write access.**

Do a backup sequence in crontab at 11pm every Tuesday and Friday.

Oracle Cloud Server

```bash
0 8 * * 3,6 /home/ubuntu/bookstack.sh
```

```bash
#!/bin/bash

cd ~/bookstack/www/uploads #directory where bookstack files scp from home are located
tar -xvzf images.tar.gz
sed -i 's/wiki.$homeip.duckdns.org/wiki.$oracle.duckdns.org/g' bookstack_db.sql
sudo docker exec -i bookstack_db mysql -u root --password=secret bookstackapp < /home/ubuntu/bookstack/www/uploads/bookstack_db.sql
```

Restore the sequence after backup, every Wednesday and Saturday at 8am (need to consider the TZ between Vancouver, Edmonton and Toronto, or any the time zone of the remote server)