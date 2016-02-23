# (openSUSE) Vagrant Salt Playground

This Vagrantfile starts 1 master and three minions.

* The master/minions are deployed with salt (meta-salt?)
  using the /vagrant/salt recipes

* Everything in /vagrant/salt (/vagrant/vagrant/salt inside the
  VMs) is used only for the initial deployment.

* Everything in /srv/salt (/vagrant/srv/salt, symlinked to /srv/salt)
  can be used to play with modules and states.

## Usage

```console
vagrant up
```

This will start one master and 3 minions. The base image is `opensuse/openSUSE-42.1-x86_64`.
The salt packages are not the ones in Leap but the ones the SUSE maintains in
[systemsmanagement:salstack](https://build.opensuse.org/project/show/systemsmanagement:saltstack) which may be a bit newer than Leap.

Once the base box is booted, the salt recipes in `vagrant/salt` will bootstrap the master, expose its IP via [SLP](https://en.wikipedia.org/wiki/Service_Location_Protocol), and configure the minions to point to this IP. The states in `vagrant/salt` are only using for the initial bootstrapping.

The master will be configured with `file_root` point to `/vagrant/srv/salt` which is the folder `srv/salt` outside of the VM. That is the folder where you can put states for the minions.

## Author

* Duncan Mac-Vicar P. <dmacvicar@suse.de>
