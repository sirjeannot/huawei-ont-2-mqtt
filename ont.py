#!/usr/bin/python3
import telnetlib
import time
import sys
import paho.mqtt.client as mqtt
#pip install paho-mqtt

user='root'
password='admin'
host='<your_ont_management_ip>'

mqttBroker='<your_mqtt_broker>'
mqttUser='<your_mqtt_broker_user>'
mqttPassword='<your_mqtt_broker_password>'
mqttTopic='<your_mqtt_topic>'

cmds=["display optic","display sysinfo","quit"]
#cmds=["display optic","display sysinfo","display pon statistics","clear pon statisctics","quit"]
fields=["LinkStatus","Voltage","Temperature","RxPower","TxPower","CpuUsed","MemUsed"]

try:
   tn=telnetlib.Telnet(host)
   tn.read_until(b"Login:")
   tn.write(user.encode('ascii') + b"\n")
   tn.read_until(b"Password:")
   tn.write(password.encode('ascii') + b"\n")
   tn.read_until(b"WAP>")
   print("Connection establised")

except Exception:
   print("Connection failed")
   sys.exit()

output=''
for cmd in cmds:
   tn.write(cmd.encode('ascii') + b"\n")
   output+=tn.read_until(b"WAP>").decode('ascii')
   time.sleep(.3)

client=mqtt.Client(mqttTopic)
client.username_pw_set(mqttUser,mqttPassword)
client.connect(mqttBroker)
for line in output.splitlines():
   data=line.split()
   if len(data)>0:
      if data[0] in fields:
         print(data[0] + "\t" + data[2])
         client.publish(mqttTopic+"/"+data[0],data[2])
         time.sleep(0.15)
client.disconnect()
