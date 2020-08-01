# Adeept_AWR
Adeept Wheeled Robot with Google Assistant

create ramdisk record in fstab

```
vi /etc/fstab
tmpfs                 /home/pi        tmpfs   defaults          0       0
```

autostart pi directory from ramdisk

```
#!/bin/bash

sleep 5
sudo rsync -a /home/rampi/ /home/pi
sudo chown -R pi:pi /home
sleep 5
sudo nohup /usr/bin/python3 /home/pi/Adeept_AWR/server/webServer.py&

exit 0
```