# Automated_Iperf
Building Iperf server/client and measuring a throughput automatically with a logging

## Summary
Iperf is a tool for throughput measurements on IP networks especially TCP, UDP bandwidth. If you are not familiar with Iperf tool, please refer to the link below.
[link to Iperf GitHub!](https://github.com/esnet/iperf)

Iperf is currently widely used in Wireless communication in order to measure maximum througputs between AP and stations or peer devices. For examples, the througputs will be decreasing as the stations is moving away from a connected AP. This can be evaluated through RvR measurement, which measure the througput as RSSI, Received Signal Strength Indicatior, decrease or the distance from a connected device increase. Iperf is a tool used for this througput measurement.

To run iperf, we need to set up iperf server and client at host and client side.
you can confing manyally options and run server and client respectively, but it is a little trouble some to do.

This automated Iper setup and running scripts which is made by Python can help you config iperf server and clinet, start automatically, and loggging that you want to collect in your control PC. 
It doesn't require extra hands to sync the time between Server and Clent. 

Also, it is useful for getting logs that needs time sync between server and client. 


## Iperf Throughput Automatic Running Configuration
The following picture is describing the overall configuration of iperf auto measurement.
![Iperf Measurement Configuartion](./images/iperf_config.png)


Iperf server will be running on the server pc, remote device and client will be running on DUT or vice versa. It depends on your configuration on what the server/client will be.
Anyway, the remote device and DUT are connected via the AP here, it is a wireless connection. so the iperf will measure a wireless throughput between a remote pc and DUT.

The control pc control all programs which will be running on the server side and client side. It will also collect the logs from server and client at the same time. It is connected via IP hub which is connected with a remote pc.

* Control PC
  * Server (Remote PC), Client (DUT)
    * Set iperf server to PC and client to DUT
    * Running iperf as a server through remote commands using "sshpass
      exec sshpass -p 'password' ssh -o StrictHostKeyChecking=no 'userid'@remote_ip.address commands shell=True"
    * Run iperf client on DUT via 'adb shell' command
    * Extracting logs from remote pc using proc.stdout.readline()
  * Server (DUT), Client (Remote PC)
    * Same as the above except changing the server, client and commands

                        
The AP distribute IP address two connected devices, 192.168.1.x and 192.168.1.x1 respectively. It is different from ip addresses distributed to a remote device and control pc from a ip router.

# Usage

