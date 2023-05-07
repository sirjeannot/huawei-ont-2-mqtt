# huawei-ont-2-mqtt
Send Huawei ONT (Optical Network Terminator, i.e. GPON Media converter to Ethernet) statistics to MQTT broker. I've created this script to integrate my Huawei HG8010H (ISP provided) into HomeAssistant through MQTT. HomeAssistant presents the data using an MQTT sensor for each value.
The script can run anywhere, as long as the ONT management interface and the MQTT are reachable. I've crontab'ed it to run every 10 minutes.

# How it works
1. Connects to Huawei ONT using telnet
2. Sends several commands to get wanted values (`cmds[]` array)
3. Disconnects telnet session
4. Connects to MQTT broker
5. Filters wanted values (`fields[]` array)
6. Disconnects from MQTT broker

Script produces the following terminal output. It may vary depending on the parameters monitored.
```
user@host:~ $ ./ont.py
Connection establised
LinkStatus      ok
Voltage 3317
Temperature     53
RxPower -19.07
TxPower 2.10
CpuUsed 5
MemUsed 67
user@host:~ $
```

The statistics are sent to the MQTT broker.

![image](https://user-images.githubusercontent.com/9054080/236691722-fc228e54-4a85-44e2-944f-65b299ef9c93.png)


# Prerequisites/Steps
- MQTT broker (not covered here)
- ONT configuration
  - IP access to ONT management interface (not covered here, see note[^1] below)
  - Enable telnet remote access
- Python3 environnment requirement
- HomeAssistant Sensor

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


## ONT Configuration
The goal is to enable telnet for remote access.
Open the admin interface using http://192.168.100.1 or the IP matching the ISP configuration. Use ONT credentials.

![image](https://user-images.githubusercontent.com/9054080/236683645-c8020422-caa1-4f27-a753-70ef1af6d9a3.png)

Save the configuration file. Remote management can only be enabled using the configuration file `hw_ctree.xml`.
![image](https://user-images.githubusercontent.com/9054080/236683743-4a74df6f-8c5b-4fe8-bfcf-1c9ff6e8ce54.png)

Edit `hw_ctree.xml` as follows. There are two lines to change to enable telnet.
before
```
<X_HW_CLITelnetAccess Access="0" EquipAdminAccess="0" TelnetPort="23"/>
<AclServices HTTPLanEnable="1" HTTPWanEnable="0" FTPLanEnable="0" FTPWanEnable="0" TELNETLanEnable="0" TELNETWanEnable="0" SSHLanEnable="0" SSHWanEnable="0" HTTPPORT="80" FTPPORT="21" TELNETPORT="23" SSHPORT="22"/>
```
after
```
<X_HW_CLITelnetAccess Access="1" EquipAdminAccess="1" TelnetPort="23"/>
<AclServices HTTPLanEnable="1" HTTPWanEnable="0" FTPLanEnable="0" FTPWanEnable="0" TELNETLanEnable="1" TELNETWanEnable="0" SSHLanEnable="0" SSHWanEnable="0" HTTPPORT="80" FTPPORT="21" TELNETPORT="23" SSHPORT="22"/>
```

Login using telnet on port 23.

![image](https://user-images.githubusercontent.com/9054080/236683413-d9595b7a-31b5-4123-8985-67e6adf5ceaa.png)

There are several commands for statistics available. Use command `?` to display all commands. `display pon statistics` may also be of interest. Each statistics item has a name, the same name is used for statistics filtering in the `fields[]` in the script.

![image](https://user-images.githubusercontent.com/9054080/236691094-d74611eb-8648-47b4-b7ac-925844984c92.png)

![image](https://user-images.githubusercontent.com/9054080/236691123-3213bc4e-efa8-4af9-9979-2d18b853d880.png)

ONT is now configured.

## Python3 environnment requirement
The script relies on telnetlib and paho-mqtt. They can be installed using command:
```
pip install paho-mqtt telnetlib
```

# HomeAssistant sensor
The following `configuration.yaml` mqtt section matches the default script `cmds[]` and `fields[]` configuration. The MQTT integration shall already be set up.

```
mqtt:
  sensor:
    - name: "ONT Linkstatus"
      state_topic: "ont/LinkStatus"

    - name: "ONT Voltage"
      state_topic: "ont/Voltage"
      device_class: voltage
      unit_of_measurement: "mV"

    - name: "ONT Temperature"
      state_topic: "ont/Temperature"
      device_class: temperature
      unit_of_measurement: "C"

    - name: "ONT RxPower"
      state_topic: "ont/RxPower"
      device_class: signal_strength
      unit_of_measurement: "dBm"

    - name: "ONT TxPower"
      state_topic: "ont/TxPower"
      device_class: signal_strength
      unit_of_measurement: "dBm"

    - name: "ONT CPU"
      state_topic: "ont/CpuUsed"
      unit_of_measurement: "%"

    - name: "ONT Memory"
      state_topic: "ont/MemUsed"
      unit_of_measurement: "%"
```

Shown as a card.

![image](https://user-images.githubusercontent.com/9054080/236692518-3e176cd1-95a3-4564-8adc-9b5b20bc36cc.png)

# Notes

[^1]: IP access to ONT management is  necessary. There are tutorials to do configure routing and interface configuration if necessary. In my own case, I do have the ONT and my own firewall, the ISP box is absent. My ISP requires a PPPoE session on the firewall WAN Ethernet interface. A VLAN interface (id depends on the ISP) attached to Ethernet interface with an IP in the same subnet as the ONT does the trick.
