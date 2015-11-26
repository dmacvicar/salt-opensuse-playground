
include:
  - common.slp

openslp:
  pkg.installed:
    - require:
      - sls: common.slp

salt-minion:
  pkg.installed: []
  service.running:
    - enable: True
    - watch:
      - pkg: salt-minion
      - file: /etc/salt/minion.d/master.conf

/etc/salt/minion.d/master.conf:
  file.managed:
    - contents: |
        {% set stop = salt['service.stop']('SuSEfirewall2') %}
        {% set master = salt['cmd.script'](source='salt://minion/find-master.sh')['stdout'] %}
        master: {{ master }}
    - require:
        - pkg: salt-minion
        - pkg: openslp
