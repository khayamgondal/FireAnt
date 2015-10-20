#!/usr/bin/env python
import sys, subprocess, time, os, datetime, signal, json
from pprint import pprint
import urllib2
import ConfigParser
#----------------------------------
# Fireant working environment setup
#----------------------------------
config = ConfigParser.ConfigParser()
config.read('/etc/nova/fireant.conf')
folder_path = config.get('directory','path')

#Also invoke this script on requesting cluster
try:
  fo = open(folder_path+'maciptable','r')
  for line in fo:
    parts = line.split('_')
    ip = parts[0]
    urllib2.urlopen('http://'+ip+'/html/startflows')
except:
 print 'maciptable doesnot exist'
time.sleep(7) #Waiting to make sure that VM is up and port is created
import MySQLdb
dip=config.get('Local', 'ip')
dbase=config.get('sql', 'db') 
duser=config.get('sql', 'user') 
dpass=config.get('sql', 'pass') 
db = MySQLdb.connect(host=dip, # your host, usually localhost
                     user=duser, # your username
                     passwd=dpass, # your password
                     db=dbase) # name of the data base
cur = db.cursor()
local=config.get('Local','ip')
cur.execute('select vlan,mac,virshname,cluster from vms')
table0=""
for row in cur.fetchall():
    tap = row[2]
    tap = "tap"+tap[10:]
    cluster_name=row[3]
    cluster_ip = cluster_name.split('_')
    if cluster_ip[1] == local:
       out=os.popen("ovs-vsctl get Interface "+tap +" ofport").read()
       out = ''.join(out.splitlines())
       flow = "table=0, in_port="+str(out)+",actions=set_field:"+str(row[0])+"->tun_id,resubmit(,1)\n"
       table0 = table0 + flow
table0 = table0 + "table=0,actions=resubmit(,1)\n"
print table0
table1=""
cur.execute('select vlan,mac,virshname,cluster,ip from vms')
for row in cur.fetchall():
    tap = row[2]
    cluster_name=row[3]
    cluster_ip = cluster_name.split('_')
    if cluster_ip[1] == local:
       port_name = "tap"+tap[10:]
    else:
       port_name = 'vx'+cluster_ip[1]
    out=os.popen("ovs-vsctl get Interface "+port_name +" ofport").read()
    out = ''.join(out.splitlines())
    flow = "table=1, tun_id="+str(row[0])+",dl_dst="+row[1]+",actions=output:"+str(out)+"\n"
    table1 = table1 + flow
try:
  fo = open(folder_path+'maciptable','r')
  for line in fo:
    parts = line.split('_')
    port_name='vx'+parts[0]
    out=os.popen("ovs-vsctl get Interface "+port_name +" ofport").read()
    out = ''.join(out.splitlines())
    parts[3]=''.join(parts[3].splitlines())
    flow = "table=1, tun_id="+str(parts[3])+",dl_dst="+parts[2]+",actions=output:"+str(out)+"\n"
    table1 = table1 + flow
except:
  print 'ipmactable not found'
cur.execute('select vlan,ip,virshname, cluster from vms')
for row in cur.fetchall():
    tap = row[2]
    cluster_name=row[3]
    cluster_ip = cluster_name.split('_')
    if cluster_ip[1] == local:
       port_name = "tap"+tap[10:]
    else:
       port_name = 'vx'+cluster_ip[1]
    out=os.popen("ovs-vsctl get Interface "+port_name +" ofport").read()
    out = ''.join(out.splitlines())
    flow = "table=1, tun_id="+str(row[0])+",arp,nw_dst="+row[1]+",actions=output:"+str(out)+"\n"
    table1 = table1 + flow
try:
  fo = open(folder_path+'maciptable','r')
  for line in fo:
    parts = line.split('_')
    port_name='vx'+parts[0]
    out=os.popen("ovs-vsctl get Interface "+port_name +" ofport").read()
    out = ''.join(out.splitlines())
    parts[3]=''.join(parts[3].splitlines())
    flow = "table=1, tun_id="+str(parts[3])+",arp,nw_dst="+parts[1]+",actions=output:"+str(out)+"\n"
    table1 = table1 + flow
except:
  print 'ipmactable not found'

table1 = table1 + "table=1,priority=1000,actions=drop"
print table1
table = table0 + table1
f = open(folder_path+'vxlanflows.txt','w')
f.write(table)
f.close()

#Remove ipmactables
try:
 os.remove(folder_path+'maciptable')
except:
 print 'Already removed maciptabl/Doesnot exist'
os.popen("ovs-ofctl del-flows br-ant")
os.popen("ovs-ofctl add-flows br-ant  "+folder_path+"/vxlanflows.txt")

