"""
This is a script to run iperf and collect wl counters data every x seconds automatically
"""

import os
import subprocess
import signal
import sys
import argparse
import time
import shlex
import multiprocessing
import datetime

class DutDevice(object):

    def __init__(self, ip_address, type, role):
        self.ip_address = ip_address
        self.type = type
        self.role = role
    
    def command(self, command):
        print('device type is', self.type, self.role.upper())
        if self.type == 'PHONE':
            if self.role == 'client': # Tx
                cmdsub = "date; adb shell "
                command_p = subprocess.Popen(cmdsub + command, shell=True, \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            else: # Rx
                command_p = subprocess.Popen("exec adb shell " + command, shell=True, \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE ,universal_newlines=True)
    
        elif self.type == 'REMOTE':
            command_p = subprocess.Popen("exec sshpass -p '"+self.remote_pw+"' ssh -o StrictHostKeyChecking=no "+self.remote_id +"@"+ self.remote_ip_address \
                        + " \"" + "date; " + command + "\"", shell=True, \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        elif self.type == 'LOCAL':
            command_p = subprocess.Popen([command], shell=True, \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return command_p

    def command_local(self, command):
        #print('command local type is', self.type)
        if self.type == 'PHONE':  # for wl commands
            command_p_local = subprocess.Popen([command], shell=True, bufsize=-1,  \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            return command_p_local

    def command_remote(self, command):
        if self.type == 'REMOTE':
            command_p_remote = subprocess.Popen("exec sshpass -p '"+self.remote_pw+"' ssh -o StrictHostKeyChecking=no "+self.remote_id +"@"+ self.remote_ip_address \
                        + " \"" + command + "\"", shell=True, \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            return command_p_remote

    def set_remote_info(self, remote_id, remote_pw, remote_ip_address):
        self.remote_id = remote_id
        self.remote_pw = remote_pw
        self.remote_ip_address = remote_ip_address

class ServerClient(object):
    iperf_option = {
        "tcp_udp"    : "", # tcp/udp
        "direction"  : "", # Tx/Rx
        "run_time"   : "", # run time
        "wsize"      : "", # window size
        "interval"   : "", # interval
        "bandwidth"  : "", # UDP bandwidth
		"qos"        : "", # QoS value
    }
    def __init__(self, role, device):
        self.role = role
        self.device = device
        self.ip_address = device.ip_address
        
    def iperf_setup(self, tcp_udp, direction, run_time="60", interval="1", wsize="8M", bandwidth="80M", qos=""):
        self.iperf_option["tcp_udp"] = tcp_udp
        self.iperf_option["direction"] = direction
        self.iperf_option["run_time"] = run_time
        self.iperf_option["wsize"] = wsize
        self.iperf_option["interval"] = interval
        self.iperf_option["bandwidth"] = bandwidth
        self.iperf_option["qos"] = qos
    
    def iperf_start(self, tcp_udp, host_ip_address='192.168.1.1'):
        extra_cmd = {"server":"", "client":""}

        tcp_udp = self.iperf_option["tcp_udp"]
        direction = self.iperf_option["direction"]
        run_time = self.iperf_option["run_time"]
        wsize = self.iperf_option["wsize"]
        interval = self.iperf_option["interval"]
        bandwidth = self.iperf_option["bandwidth"]
        qos = self.iperf_option["qos"]
        host_ip_addr = host_ip_address

        if tcp_udp == 'udp':
            extra_cmd["server"] = " -u "
            extra_cmd["client"] = " -u -b " + bandwidth
        
        cmd_str = ''
        if self.role is 'server':
            cmd_str = "iperf -s -w " + wsize + " -i " + interval + extra_cmd["server"]
        else:
            cmd_str = "iperf -c " + host_ip_addr+ " -w " + wsize + " -t " + run_time + " -i " + interval +" -P 2 " + extra_cmd["client"]
            #cmd_str = "iperf -c " + host_ip_addr+ " -w " + wsize + " -t " + run_time + " -i " + interval + extra_cmd["client"]

        print('\n')
        print(cmd_str)
        iperf_p = self.device.command(cmd_str)

        return iperf_p

def proc_readline(proc, logfile):
    while True:
        data = proc.stdout.readline()
        if len(data) == 0:
            break
        else:
            print(data.rstrip().rsplit('\n'))
            logfile.write(data)


def kill_wlcmdlog(shellname='wlcmds'):
    proc = subprocess.Popen("ps -ef | grep " + shellname + " | grep -v grep", shell=True, \
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    lines = proc.stdout.read()
    lines = lines.split('\n')
    for line in lines:
        print(line)
        pid = line.split()
        if pid:
            print("kill -9 ", pid[1])
            subprocess.run("kill -9 " + pid[1], shell=True, check=True)
    proc.kill()

def main():
    """
    iperf execution with wl commands logging
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-ipd", "--ipd_address", \
                    action="store", dest="ipd_address", default='192.168.1.3', \
                    help="dut ip address")
    parser.add_argument("-ipp", "--ipp_address", \
                    action="store", dest="ipp_address", default='192.168.1.8', \
                    help="peer device ip address")
    parser.add_argument("-t", "--tcp_udp", \
                    action="store", dest="tcp_udp", default='tcp', \
                    help="tcp or udp")
    parser.add_argument("-d", "--duration", \
                    action="store", dest="duration", default='30', \
                    help="duration")
    parser.add_argument("-x", "--direction", \
                    action="store", dest="direction", default='rx', \
                    help="directon 'tx' or 'rx' ")
    parser.add_argument("-b", "--band", \
                    action="store", dest="band", default='a', \
                    help="band a(5GHz) or b(2.4GHz) ")

    parser.add_argument("-lc", "--lc_type", \
                    action="store", dest="local_type", default='LOCAL', \
                    help="local dut device is 'LOCAL' or 'PHONE' ")
    parser.add_argument("-s", "--sleep", \
                    action="store", dest="sleep_time", type=float, \
                    help="Sleep duration between wl commands, need to adjust every time")

    args = parser.parse_args()
    print(args)

    ipd_address = args.ipd_address
    ipp_address = args.ipp_address
    duration = args.duration
    band = args.band
    direction = args.direction
    tcp_udp = args.tcp_udp
    local_type = args.local_type

    # set default sleep time
    if args.sleep_time is not None:
        sleep_time = args.sleep_time
    else:
        if direction == 'rx' and band == 'a':
            sleep_time = 0.80
        elif direction == 'tx' and band == 'a':
            sleep_time = 0.72
        else:
            sleep_time = 0.75

    if direction == 'rx': # DUT is Server (RX)
        local_dut = DutDevice(ipd_address, local_type, 'server')
        peer_pc = DutDevice(ipp_address, 'REMOTE', 'client')

        server = ServerClient('server', local_dut)
        client = ServerClient('client', peer_pc)

    else: # DUT is Client (TX)
        local_dut = DutDevice(ipd_address, local_type, 'client')
        peer_pc = DutDevice(ipp_address, 'REMOTE', 'server')

        server = ServerClient('server', peer_pc)
        client = ServerClient('client', local_dut)

    
    peer_pc.set_remote_info('ethan', 'ethan', '192.168.0.2')

    server.iperf_setup(tcp_udp, direction)
    client.iperf_setup(tcp_udp, direction, run_time=duration)

    # iperf server start
    server_p = server.iperf_start(tcp_udp)

    # Let's wait for server to be started especially in remote.
    if server.device.type is 'REMOTE':
        data = server_p.stdout.readline()
        if len(data) != 0:
            print('remote iperf server started!!')

    time.sleep(1)

    curtime = datetime.datetime.now()
    curtime_str = curtime.strftime("%Y-%m-%d_%H%M%S")
    file_name_prefix = '_' + band + '_' + tcp_udp + '_' + direction + '_' + curtime_str
    log_iperf_name = './log/iperf' + file_name_prefix + '.txt'
    wlcnt_name = './log/wlcnt' + file_name_prefix + '.log'
    
    log_iperf = open(log_iperf_name, 'a')

    wlsleep_seconds = str(sleep_time)
    #print('sleep_seconds =', wlsleep_seconds)
    if local_type == 'PHONE':
        os.system("adb shell wl scansuppress 1")
        wlcnt_p = local_dut.command_local("./wlcmds.sh " + wlsleep_seconds + " > " + wlcnt_name)

    # iperf client start
    client_p = client.iperf_start(tcp_udp, server.ip_address)

    #print('iperf operation is on going......please wait !!')
    #client_p.wait()
    proc_readline(client_p, log_iperf)

    client_p.kill()
    server_p.kill()

    if local_type == 'PHONE':
        time.sleep(1)
        wlcnt_p.kill()
        kill_wlcmdlog('wlcmds')

    server_out = server_p.stdout.read()
    client_out = client_p.stdout.read()

    # Kill remote iperf server
    if server.device.type == 'REMOTE':
        server_rp = server.device.command_remote("killall -9 iperf")
        server_rp.wait()
        print('remote iperf server stopped')

    log_iperf.write(server_out)
    log_iperf.write(client_out)
    log_iperf.close()

    if local_type == 'PHONE':
        os.system("adb shell wl scansuppress 0")

if __name__ == '__main__':
    main()