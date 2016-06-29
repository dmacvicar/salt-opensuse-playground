# -*- coding: utf-8 -*-
'''
Building containers from pure state data

https://hackweek.suse.com/14/projects/1756)

:maintainer:    Duncan Mac-Vicar P. <dmacvicar@suse.de>
:maturity:      new

'''
import logging
import os
import os.path
import shutil
import tempfile
import salt.utils.thin
import salt.exceptions

log = logging.getLogger(__name__)

__virtualname__ = 'dockerimage'


def __virtual__():
    # as this will be moved to dockerng, we have the same
    # requirements, assume it just works
    return __virtualname__


def build_image(name, base='opensuse:42.1', mods=None, **kwargs):
    '''
    Build a docker image using the specified sls modules and base image.

    For example, if your master defines the states ``web`` and ``rails``, you
    can build a docker image inside myminion that results of applying those
    states by doing:

    .. code-block:: bash

        salt myminion dockerimage.build_image imgname mods=rails,web
    '''
    tmpdir = tempfile.mkdtemp()
    thin_path = salt.utils.thin.gen_thin(tmpdir)
    unpack_path = os.path.join(tmpdir, 'salt')
    state_path = os.path.join(tmpdir, 'srv', 'salt')

    os.makedirs(unpack_path)
    os.makedirs(state_path)

    if mods is not None:
        mods = [x.strip() for x in mods.split(',')]
    else:
        mods = []

    # prepare salt itself
    __salt__['archive.tar']('-zxf', thin_path, dest=unpack_path)

    # prepare the state tree. May be this is a hack
    for mod in mods:
        __salt__['cp.get_dir']('salt://{0}'.format(mod), state_path, gzip=5)

    salt_cmd = './salt-call -l debug --retcode-passthrough --local --file-root=/tmp/srv/salt'
    if len(mods) > 0:
        salt_cmd += ' state.sls {0}'.format(','.join(mods))

    content = """
    FROM {base}
    ADD ./salt /tmp/salt
    ADD ./srv /tmp/srv
    RUN chmod +x /tmp/salt/salt-call
    WORKDIR /tmp/salt
    RUN zypper -n in --no-recommends python python-msgpack-python
    RUN python {salt_cmd}
    """.format(
        base=base,
        salt_cmd=salt_cmd
    )

    log.info('Dockerfile to build:\n{0}'.format(content))
    dockerfile_path = os.path.join(tmpdir, 'Dockerfile')
    with open(dockerfile_path, 'w') as f:
        f.write(content)

    ret = None
    try:
        ret = __salt__['dockerng.build'](path=tmpdir, image=name)
    except salt.exceptions.CommandExecutionError as e:
        return False, e.message

    shutil.rmtree(tmpdir)
    return ret
