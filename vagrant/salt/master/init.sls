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
    - watch:
        - file: /etc/salt/master.d/vagrant-fileroot.conf
    - enable: True

publish master:
  cmd.run:
    - name: slptool register service:salt-master://{{ salt['network.interfaces']()['eth0']['inet'][0]['address'] }}

# use the vagrant /srv/salt
/etc/salt/master.d/vagrant-fileroot.conf:
  file.managed:
    - contents: |
        file_roots:
          base:
            - /vagrant/srv/salt
    - require:
        - pkg: salt-master
