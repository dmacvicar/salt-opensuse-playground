salt-master:
  pkg.installed: []
  service.running:
    - watch:
        - file: /etc/salt/master.d/vagrant-fileroot.conf
        - file: /etc/salt/master.d/salt-auth.conf
    - enable: True

avahi:
  pkg.installed

avahi-daemon:
  service.running:
    - enabled: True
    - require:
        - pkg: avahi
    - watch:
        - file: /etc/avahi/services/salt-master.service

/etc/avahi/services/salt-master.service:
  file.managed:
    - contents: |
        <service-group>
          <name replace-wildcards="yes">%h</name>
          <service>
            <type>_salt-master._tcp</type>
            <port></port>
          </service>
        </service-group>
    - require:
        - pkg: avahi

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

