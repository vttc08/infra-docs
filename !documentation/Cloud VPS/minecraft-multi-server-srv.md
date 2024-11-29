---
date: 2024-11-27 19:40
update: 2024-11-28T23:10:52-08:00
comments: "true"
---
# Multiple Minecraft Server on Same IP with SRV Record
Overall architecture
![](assets/Pasted%20image%2020241128230413.png)
## Dynu Settings
Go to https://www.dynu.com/en-US/ControlPanel/DDNSRecord
- click the edit icon
- Manage DNS Records
- click Edit to add a SRV record

> [!warning] Dynu or DDNS SRV records are different
> Since with Dynu, it gives a subdomain `sub.dynu.ddns`, it's different than owning a full domain `dynu.ddns`. The settings are different compared to when using a real domain registrar.

Node Name - this should be `_minecraft._tcp.newserver` where `newserver.my.dynu.ddns` is what the user will enter when reaching secondary server
Type - `SRV`
Priority/Weight - not tested, setting it to 0 will work
Port - the secondary port of Minecraft server
Target - `my.dynu.ddns`, this should be the base domain

This is all the entries in screenshot
![](assets/Pasted%20image%2020241128230646.png)
## Results
![](assets/Pasted%20image%2020241127194207.png)