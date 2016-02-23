# Vagrant Salt Playground

This Vagrantfile starts 1 master and three minions.

* The master/minions are deployed with salt (meta-salt?)
  using the /vagrant/salt recipes

* Everything in /vagrant/salt (/vagrant/vagrant/salt inside the
  VMs) is used only for the initial deployment.

* Everything in /srv/salt (/vagrant/srv/salt, symlinked to /srv/salt)
  can be used to play with modules and states.


