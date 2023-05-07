# huawei-ont-2-mqtt
Send Huawei ONT (Optical Network Terminator, i.e. GPON Media converter to Ethernet) info to MQTT broker. I've created this script to integrate my Huawei HG8010H into HomeAssistant through MQTT. HomeAssistant accesses the data using an MQTT sensor for each value.
The script can run anywhere, 

## How it works
1. Connects to Huawei ONT using telnet
2. Sends several commands to get wanted values (`cmd[]` array)
3. Disconnects telnet session
4. Connects to MQTT broker
5. Filters wanted values (`fields[]` array)

## Prerequisites
- MQTT broker (not covered here)
- ONT configuration
  - IP access to ONT management interface (see note below)
  - Enable telnet remote access
- Python3 environnment requirement

IP access to ONT management is also necessary. There are tutorials to do so. In my own case, I do have the ONT and my own firewall. My ISP requires a PPPoE session on the firewall WAN Ethernet interface. A VLAN interface on the required VLAN attached to Ethernet interface does the trick.

## Script variables
ONT Admin credentials. Defaults are `root`/`admin` or `telecomadmin`/`admintelecom`.
```
user='root'
password='admin'
```
ONT management IP address. The default is `192.168.100.1` but it may vary depending on the ISP.
```
host='<your_ont_management_ip>'
```
MQTT configuration.
```
mqttBroker='<your_mqtt_broker>'
mqttUser='<your_mqtt_broker_user>'
mqttPassword='<your_mqtt_broker_password>'
mqttTopic='<your_mqtt_topic>'
```
Commands to use do get required values. There are more commands available using the `?` command. The last command I use is `quit` to close properly the telnet session as the ONT only accepts one telnet session. There are more commands like `display pon statistics` to use along with `clear pon statisctics` to show more info on the GPON transport layer.
```
cmds=["display optic","display sysinfo","quit"]
```
Fields to look for displayed by the commands before. The following list is the one I used, but there are more values available.
```
fields=["LinkStatus","Voltage","Temperature","RxPower","TxPower","CpuUsed","MemUsed"]
```


# ONT Configuration
## Enable telnet
Open the admin interface using http://192.168.100.1 or the IP matching the ISP configuration. Use ONT credentials.
![image](https://user-images.githubusercontent.com/9054080/236683645-c8020422-caa1-4f27-a753-70ef1af6d9a3.png)

Save the configuration file. Remote management can only be enabled using the configuration file `hw_ctree.xml`.
![image](https://user-images.githubusercontent.com/9054080/236683743-4a74df6f-8c5b-4fe8-bfcf-1c9ff6e8ce54.png)

Edit `hw_ctree.xml` as follows. There are two lines to change.
change
```
<X_HW_CLITelnetAccess Access="0" EquipAdminAccess="0" TelnetPort="23"/>
```
to
```
<X_HW_CLITelnetAccess Access="1" EquipAdminAccess="1" TelnetPort="23"/>
```
and
```
<AclServices HTTPLanEnable="1" HTTPWanEnable="0" FTPLanEnable="0" FTPWanEnable="0" TELNETLanEnable="0" TELNETWanEnable="0" SSHLanEnable="0" SSHWanEnable="0" HTTPPORT="80" FTPPORT="21" TELNETPORT="23" SSHPORT="22"/>
```
to
```
<AclServices HTTPLanEnable="1" HTTPWanEnable="0" FTPLanEnable="0" FTPWanEnable="0" TELNETLanEnable="1" TELNETWanEnable="0" SSHLanEnable="0" SSHWanEnable="0" HTTPPORT="80" FTPPORT="21" TELNETPORT="23" SSHPORT="22"/>
```

Login using telnet on port 23.

![image](https://user-images.githubusercontent.com/9054080/236683413-d9595b7a-31b5-4123-8985-67e6adf5ceaa.png)

