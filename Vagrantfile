Vagrant.configure(2) do |config|
  config.vm.box = 'alchemy-solutions/opensuseleap42.1'
  config.vm.synced_folder './', '/vagrant', type: '9p'

  config.vm.define 'master' do |master|
    master.vm.provision 'shell', inline: <<-SHELL
       hostnamectl set-hostname master
       systemctl stop SuSEfirewall2
       systemctl disable SuSEfirewall2
       sudo zypper -n install --no-recommends salt-master openslp-server
       systemctl enable slpd
       systemctl start slpd
       systemctl enable salt-master
       systemctl start salt-master
       IP=$(/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}')
       route add -net 224.0.0.0 netmask 240.0.0.0 dev eth0
       slptool register service:salt-master://$IP
    SHELL
  end

  3.times do |i|
    config.vm.define "minion#{i}" do |minion|
      minion.vm.provision 'shell', inline: <<-SHELL
       hostnamectl set-hostname minion#{i}
       systemctl stop SuSEfirewall2
       systemctl disable SuSEfirewall2
       sudo zypper -n install --no-recommends salt-minion openslp
       route add -net 224.0.0.0 netmask 240.0.0.0 dev eth0
       while true; do
         MASTER=$(slptool findsrvs service:salt-master | cut -d, -f1 | cut -d/ -f 3)
         [[ !  -z  $MASTER  ]] && break
       done
       echo "master: $MASTER\n" > /etc/salt/minion.d/master.conf
       systemctl enable salt-minion
       systemctl start salt-minion
    SHELL
    end
  end
end
