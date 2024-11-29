---
date: 2024-05-07T18:06:07.000000Z
update: 2024-11-15T10:50:54-08:00
comments: "true"
---
# Samba(SMB) Setup

## Setting up SMB Server on Linux

Install the samba tool on Linux.

```bash
sudo apt update
sudo apt install samba -y
```

Edit the `/etc/samba/smb.conf`

```yaml
[nvme_share]
   comment = NVMe Share
   path = /mnt/nvme/share
   browseable = yes
   read only = no
```

`nvme_share` is the name of the Samba path which will appear in SMB clients and its path is accessed by `\\192.168.0.1\nvme_share`

![](assets/gallery/2024-05/image.png)

`path` is the location where the files are stored

`browseable` and `read only` are flags that are needed to make sure read/write access on the SMB share

Lastly, add the user and password for the SMB share

```bash
sudo smbpasswd -a $USER # enter the password twice
```

In the case when Windows fail to write files in the samba share for odd reason. Go to `Manage Credentials` -> `Windows Credentials` -> `Add a Windows Credential` and fill the necessary address, username and password.
## Setting SMB Client in Linux
Install required apps
```sh
sudo apt-get install cifs-utils -y
```
Make the required folders for mounting SMB drive.
```sh
sudo mkdir -p /mnt/vifs/nvme
```
Create a credential file for the server.
- put it in a root folder directory eg `/root/.server-smbcred`
- the file must be owned by root with 600 permission
```python
username=user
password=password
```
```sh
sudo chown root: /root/.smbcred
sudo chmod 600 /root/.smbcred
```
Test the mount
```sh
sudo mount -t cifs -o credentials=/root/.mediaserver-smbcred,uid=1000,gid=1001,dir_mode=0755,file_mode=0755 //serverip/nvme_share /mnt/cifs/nvme
```
- make sure to set the `uid,gid,dir_mode,file_mode` so the files are not owned by root and not writable

FSTAB permeant mount `/etc/fstab`
```sh
//10.10.120.16/tv_2_share  /mnt/cifs/tv2  cifs  credentials=/root/.mediaserver-smbcred,uid=1000,gid=1001,file_mode=0755,dir_mode=0755 0 0
```
