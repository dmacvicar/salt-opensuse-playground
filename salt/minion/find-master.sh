#!/bin/sh
while true; do
  MASTER=$(slptool findsrvs service:salt-master | cut -d, -f1 | cut -d/ -f 3)
  [[ !  -z  $MASTER  ]] && break
done
echo $MASTER
