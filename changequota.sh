#!/bin/bash
#This scipt will change the quota as passed in arguments.
#Currently it will only modify the instances count.
#Script relys on keystone_admin & keystone_tester. Make sure both scripts
#exits in the folder
source keystone_admin
ins_count=$1
if [[ -n "$ins_count" ]]; then
   tenant="$(keystone tenant-list | awk '/tester/ {print $2}')"
   nova quota-update  --instances $ins_count --cores 2 --ram 1024 $tenant
else
  echo "ERROR: Pass instance_count as argument"
fi
