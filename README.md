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

`salt-api` will be configured on the master and open to the world.

### Accessing the master

You can find the ip of the master from your machine:

```console
$ slptool -i virbr1 findsrvs service:salt-master
service:salt-master://192.168.121.73,65535
```

Where virbr1 is the bridge where your virtualization setup is connected to.
(ignore the port, we only announce the ip address)

But vagrant can ssh into it automatically, just do:

```console
$ vagrant ssh master
```

### Accepting the minions

The minions will be in pending state. To accept them, get into the master and do:

```console
$ vagrant ssh master
$ salt-key -A
```

### Using salt from the master

```console
$ vagrant ssh master
$ salt '*' test.ping
minion1:
    True
minion2:
    True
minion0:
    True
```

### Using salt via salt-api

From your host, find the ip of the master:

```console
$ slptool -i virbr1 findsrvs service:salt-master
service:salt-master://192.168.121.73,65535
```
Where virbr1 is the bridge where your virtualization setup is connected to.
(ignore the port, we only announce the ip address)

Now you can control salt via http:

```console
curl -sS 192.168.121.73:8000/run -d client='local' -d tgt='*' -d fun='test.ping' -d eauth='auto' -d username='admin' -d password=''
```

```json
{"return": [{"minion1": true, "minion0": true, "minion2": true}]}
```

As this setup is intended for development, `salt-api` is listening to external connections and the master configured with dummy authentication on `admin`.

## Author

* Duncan Mac-Vicar P. <dmacvicar@suse.de>
