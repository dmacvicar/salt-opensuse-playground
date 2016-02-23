include:
  - common.slp

openslp-server:
  pkg.installed: []
  service.running:
    - name: slpd
    - enable: True
    - require_in:
        - pkg: salt-master

salt-master:
  pkg.installed: []
  service.running:
    - enable: True

publish master:
  cmd.run:
    - name: slptool register service:salt-master://{{ salt['network.interfaces']()['eth0']['inet'][0]['address'] }}

