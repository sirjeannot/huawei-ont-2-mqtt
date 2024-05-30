#!/usr/bin/python3
import pexpect
import time
import sys
import paho.mqtt.client as mqtt

user='root'
password='admin'
host='<your_ont_management_ip>'

mqttBroker='<your_mqtt_broker>'
mqttUser='<your_mqtt_broker_user>'
mqttPassword='<your_mqtt_broker_password>'
mqttTopic='<your_mqtt_topic>'

#cmds=["display optic","display sysinfo","quit"]
cmds=["display optic","display sysinfo","display pon statistics","clear pon statisctics","quit"]
fields=["LinkStatus","Bias","Voltage","Temperature","RxPower","TxPower","CpuUsed","MemUsed","Bip-err"]

try:
   tn = pexpect.spawn("telnet " + host, timeout=2)
   tn.expect ("Login:")
   tn.sendline (user)
   tn.expect ("Password:")
   tn.sendline (password)

except Exception:
   print("Connection failed")
   sys.exit()

if tn.expect(["WAP>", pexpect.TIMEOUT]) == 1:
   print("Connection failed")
   sys.exit()

output=''
for cmd in cmds:
   tn.sendline(cmd.encode('ascii') + b"\n")
   tn.expect("WAP>")
   output += tn.before.decode('ascii')
   time.sleep(.3)

client=mqtt.Client(mqttTopic)
client.username_pw_set(mqttUser,mqttPassword)
client.connect(mqttBroker)
for line in output.splitlines():
   data=' '.join(line.split()) #remove all multispaces
   data=data.replace('=',':').split(":") #normalize separator and split
   if len(data)>1:
      data[0]=data[0].replace(' ','-',data[0].count(' ')-1).replace(' ','') #replace spaces in names and remove last space
      if data[0] in fields:
         data[1]=data[1].split()[0]  #data[0] is field name, data[1] is value with unit which should be removed
         print(data[0] + "\t" + data[1])
         client.publish(mqttTopic+"/"+data[0],data[1])
         time.sleep(0.15)
client.disconnect()
