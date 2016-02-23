Vagrant.configure(2) do |config|
  config.vm.box = 'opensuse/openSUSE-42.1-x86_64'
  config.vm.synced_folder './', '/vagrant', type: '9p'
  config.vm.define 'master' do |master|
    # master.vm.hostname = 'master'
    master.vm.provision 'shell', inline: <<-SHELL
       export PATH=$PATH:/sbin
       hostnamectl set-hostname master
       sudo zypper -n install --no-recommends salt
       salt-call -l debug --file-root /vagrant/salt --pillar-root=/vagrant/pillar --local state.highstate
    SHELL
  end

  3.times do |i|
    config.vm.define "minion#{i}" do |minion|
      # minion.vm.hostname = "minion#{i}"
      minion.vm.provision 'shell', inline: <<-SHELL
       export PATH=$PATH:/sbin
       hostnamectl set-hostname minion#{i}
       sudo zypper -n install --no-recommends salt
       salt-call -l debug --file-root /vagrant/salt --pillar-root=/vagrant/pillar --local state.highstate
    SHELL
    end
  end
end
