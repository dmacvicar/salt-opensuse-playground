#!/bin/sh
while true; do
  MASTER=$(avahi-browse --ignore-local --resolve -t  -p _salt-master._tcp  | grep '^=;eth0;IPv4' | grep salt-master._tcp | cut -d ';' -f 8)
  [[ !  -z  $MASTER  ]] && break
done
echo $MASTER
