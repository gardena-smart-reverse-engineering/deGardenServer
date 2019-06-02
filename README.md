# deGardenServer
Local Gardena Seluxit Cloud Replacement 

Still in development. Currently only a pseodo Server saving all data to disk.

# Preparation
## Root the gateway
[Follow the instructions here](https://github.com/gardena-smart-reverse-engineering/gateway-19000/wiki/Rooting-the-Gardena-Smart-Gateway-19000)
## Install the entware opkg repository on the gateway (optional)
If you want to use the gateway as the deGardenServer you can install python3 directly on the gateway. Therefor you need an up to date repo which you will get from entware.

Just download the armv5 standard installation script and run it on the gateway and you are done.
[Install armv5 standard](https://github.com/Entware/Entware/wiki/Alternative-install-vs-standard)

## Install python3
Run `/opt/bin/opkg install python3` on the gateway to install python3. This may be different on your device you want to use as server.

### Needed python3 dependecies
Install the following dependencies with pip3
1. fs
2. xmltodict
3. flask
4. Flask-UUID

## Open firewall on the gateway (optional)
You need to open the port 5000 on the gateway. For that you can easily add the eth0 interface to the unfiltered_interfaces in the seluxit firewall script `/usr/lib/seluxit/scripts/firewall`
`unfiltered_interfaces="ppp0 vpn0 eth0"`

## Reroute the traffic
To reroute the traffic from the cloud to our script you will have to change the [Shadoway config](https://github.com/gardena-smart-reverse-engineering/gateway-19000/wiki#shadoway) on the gateway. You will find it here: `/usr/lib/shadoway/shadoway.conf`. Edit the parameters `REPORT_ENDPOINT` + `CONTROL_ENDPOINT` to match your deGardenServers Host IP. Ports stay the same.