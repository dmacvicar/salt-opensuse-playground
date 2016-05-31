
SuSEfirewall2:
  pkg.removed: []
  service.dead: []

broadcast:
  cmd.run:
    - name: route add -net 224.0.0.0 netmask 240.0.0.0 dev eth0
    - unless: route | grep 240.0.0.0 | grep eth0

