# Automated_Iperf
Building Iperf server/client and measuring a throughput automatically with a logging

## Summary
Iperf is a tool for throughput measurements on IP networks especially TCPm UDP bandwidth. If you are not familiar with Iperf tool, please refer to the link below.
[link to Iperf GitHub!](https://github.com/esnet/iperf)

Iperf is currently widely used in Wireless communication in order to measure maximum througputs between AP and stations or peer devices. For examples, the througputs will be decreasing as the stations is moving away from a connected AP. This can be evaluated through RvR measurement, which measure the througput as RSSI, Received Signal Strength Indicatior, decrease or the distance from a connected device increase. Iperf is a tool used for this througput measurement.

To run iperf, we need to set up iperf server and client at host and client side.
you can confing manyally options and run server and client respectively, but it is a little trouble some to do.

This automated Iper setup and running scripts which is made by Python can help you config iperf server and clinet, start automatically, and loggging that you want to collect in your control PC. 
It doesn't require extra hands to sync the time between Server and Clent. 

Also, it is useful for getting logs that needs time sync between server and client. 


## Usage
