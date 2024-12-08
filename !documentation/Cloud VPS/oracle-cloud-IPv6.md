---
date: 2024-12-06 23:05
update: 2024-12-08T00:38:52-08:00
comments: "true"
---
# IPv6 Oracle Cloud
### VCN Settings
https://cloud.oracle.com/networking/vcns?region=ca-toronto-1
Navigate to the main VCN, then under CIDR Blocks and Prefixes, click `Add CIDR Block`
![](assets/Pasted%20image%2020241207225444.png)
A GUA IPv6 range will be assigned by Oracle.

Go to Route Tables and click the default one.
![](assets/Pasted%20image%2020241207225647.png)
- choose `IPv6`
- type is `Internet Gateway`
- enter `::/0` for all IPv6 addresses

Go to Security Lists and click the default one
Ingress Rules
- IPv6-ICMP to allow pings to the server
- The ingress ports are applied since without it the server cannot access IPv6 websites
![](assets/Pasted%20image%2020241207231447.png)
![](assets/Pasted%20image%2020241207231012.png)
Egress Rules
- same as IPv4, allow all egress
![](assets/Pasted%20image%2020241207232328.png)
### Instance Settings
https://cloud.oracle.com/compute/instances?region=ca-toronto-1
Click on the instance name, and scroll down until `Attached VNIC` and click on the default
Under resources there is `IPv6 Addresses` and click on `Assign IPv6 Address`
![](assets/Pasted%20image%2020241207234053.png)

- multiple addresses can be assigned to the same machine, however these are single `/128` and it can only be added via Oracle cloud console

After adding the address, refresh network service in Ubuntu.
```bash
sudo systemctl restart systemd-networkd
```
