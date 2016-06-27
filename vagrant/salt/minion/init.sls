bind-utils:
  pkg.installed

avahi-utils:
  pkg.installed

salt-minion:
  pkg.installed: []
  service.running:
    - enable: True
    - watch:
      - pkg: salt-minion
      - file: /etc/salt/minion.d/master.conf

/etc/salt/minion.d/master.conf:
  file.managed:
    - source: salt://minion/master.conf
    - template: jinja
    - require:
      - pkg: salt-minion
      - pkg: avahi-utils
