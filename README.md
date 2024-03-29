# huawei-ont-2-mqtt
Fetch Huawei ONT (Optical Network Terminator, i.e. GPON "media converter" to Ethernet) statistics using telnet and sends the data to a MQTT broker. I've created this script to integrate my Huawei HG8010H (ISP provided) into HomeAssistant through MQTT. HomeAssistant presents the data using an MQTT sensor for each value.
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
Fields to look for displayed by the commands before. The following list is the one I used, but there are more values available. Fields containing spaces should replace these with `-`. Ex: `Bip err` should be listed as `Bip-err` in the `fields[]` array.
```
fields=["LinkStatus","Voltage","Temperature","RxPower","TxPower","CpuUsed","MemUsed"]
```

There are other statistics of interest. However the script splits the line into elements, element 0 being the field name and 2 the value. For names with multiple words, the script should be modified.
```
WAP>display optic
LinkStatus  : ok
Voltage      : 3317 (mV)
Bias         : 7 (mA)
Temperature  : 53 (C)
RxPower      : -19.07 (dBm)
TxPower      :  2.16 (dBm)
RfRxPower    : -- (dBm)
RfOutputPower: -- (dBmV)
VendorName   : HUAWEI
VendorSN     : xxx
VendorRev    :
VendorPN     : xxx
DateCode     : xxx

success!
WAP>display sysinfo
*************** system infomation ***************
CpuUsed  = 4 Percent(s)
MemUsed  = 70 Percent(s)
CurTime  = 2023-xx-xx xx:xx:xx
*************************************************

success!
WAP>display pon statistics
GPON statistic as follow:
Rx unicast packets    : 15450712
Tx unicast packets    : 4902623
Rx broadcast packets  : 0
Tx broadcast packets  : 135
Rx multicast packets  : 488687744
Tx multicast packets  : 0
Dropped packets       : 0

Tx ploam              : 88605
Tx omci               : 20499
Tx gem                : 19992371
Bip err               : 0
Rx ploam right        : 233109
Rx ploam wrong        : 0
Rx ploam drop         : 0
Rx omci               : 20236
Rx gem                : 504158692
Rx mc gem             : 488687744
Ds key switch         : 0
Rx omci overflow      : 0
Tx octets             : 2222947148
Tx packets            : 4902758
Rx oversize           : 5757080
Rx octets             : 2079797555
Rx packets            : 504138456
Rx undersize          : 0
Rx 64 octets          : 354816
Rx 65 to 127 octets   : 1097083
Rx 128 to 255 octets  : 410591
Rx 256 to 511 octets  : 108356
Rx 512 to 1023 octets : 145463
Rx 1024 to 1518 octets: 496265067

success!

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

Upload the saved configuration file to the ONT.

Login using telnet on port 23.

![image](https://user-images.githubusercontent.com/9054080/236683413-d9595b7a-31b5-4123-8985-67e6adf5ceaa.png)

There are several commands for statistics available. Use command `?` to display all commands. `display pon statistics` may also be of interest. Each statistics item has a name, the same name is used for statistics filtering in the `fields[]` in the script.

![image](https://user-images.githubusercontent.com/9054080/236691094-d74611eb-8648-47b4-b7ac-925844984c92.png)

![image](https://user-images.githubusercontent.com/9054080/236691123-3213bc4e-efa8-4af9-9979-2d18b853d880.png)

ONT is now configured.

## Python3 environnment requirement
The script relies on pexpect, paho-mqtt. They can be installed using command:
```
pip3 install pexpect, paho-mqtt
```
As telnetlib is now deprecated, the script uses the system telnet client.

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
