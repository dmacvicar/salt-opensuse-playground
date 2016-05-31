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
        - file: /etc/salt/master.d/salt-auth.conf
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

# configure salt api
salt-api:
  pkg.installed: []
  service.running:
    - watch:
        - file: /etc/salt/master.d/salt-api-world.conf
    - enable: True

/etc/salt/master.d/salt-api-world.conf:
    file.managed:
    - contents: |
        rest_cherrypy:
          port: 8000
          host: 0.0.0.0
          disable_ssl: True
          debug: True

/etc/salt/master.d/salt-auth.conf:
    file.managed:
    - contents: |
        external_auth:
          auto:
            admin:
              - .*
              - '@wheel'
              - '@runner'
              - '@jobs'

