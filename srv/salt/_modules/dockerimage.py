# -*- coding: utf-8 -*-
'''
Building containers from pure state data

https://hackweek.suse.com/14/projects/1756)

:maintainer:    Duncan Mac-Vicar P. <dmacvicar@suse.de>
:maturity:      new

'''
import hashlib
import logging
import os
import os.path
import shutil
import tempfile
import salt.utils.thin
import salt.pillar
import salt.exceptions
import salt.fileclient

from salt.state import HighState
import salt.client.ssh.state

log = logging.getLogger(__name__)

__virtualname__ = 'dockerimage'


def __virtual__():
    # as this will be moved to dockerng, we have the same
    # requirements, assume it just works
    return __virtualname__


def _mk_client():
    '''
    Create a file client and add it to the context.
    '''
    if 'cp.fileclient' not in __context__:
        __context__['cp.fileclient'] = \
                salt.fileclient.get_file_client(__opts__)


def _prepare_trans_tar(mods=None, saltenv='base'):
    '''
    Prepares a self contained tarball that has the state
    to be applied in the container
    '''
    chunks = _compile_state(mods, saltenv)
    # reuse it from salt.ssh, however this function should
    # be somewhere else
    refs = salt.client.ssh.state.lowstate_file_refs(chunks)
    _mk_client()
    trans_tar = salt.client.ssh.state.prep_trans_tar(
        __context__['cp.fileclient'],
        chunks, refs, pillar={'docker': {'guess': 'no'}})
    return trans_tar


def _compile_state(mods=None, saltenv='base'):
    '''
    Generates the chunks of lowdata from the list of modules
    '''
    st_ = HighState(__opts__)

    high_data, errors = st_.render_highstate({saltenv: mods})
    high_data, ext_errors = st_.state.reconcile_extend(high_data)
    errors += ext_errors
    errors += st_.state.verify_high(high_data)
    if errors:
        return errors

    high_data, req_in_errors = st_.state.requisite_in(high_data)
    errors += req_in_errors
    high_data = st_.state.apply_exclude(high_data)
    # Verify that the high data is structurally sound
    if errors:
        return errors

    # Compile and verify the raw chunks
    return st_.state.compile_high_data(high_data)


def build_image(name, base='opensuse:42.1', mods=None, saltenv='base',
                **kwargs):
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

    if mods is not None:
        mods = [x.strip() for x in mods.split(',')]
    else:
        mods = []

    # prepare salt itself
    __salt__['archive.tar']('-zxf', thin_path, dest=tmpdir)

    # prepare the state tree. May be this is a hack
    trans_tar = _prepare_trans_tar(mods=mods, saltenv=saltenv)

    trans_tar_sha256 = hashlib.sha256()
    with open(trans_tar, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            trans_tar_sha256.update(data)

    shutil.move(trans_tar, os.path.join(tmpdir, 'salt_state.tgz'))

    ret = {}
    ret_debug = {}
    ret['result'] = True

    # start a new container
    ret_debug['create'] = __salt__['dockerng.create'](image=base,
                                                         cmd='/usr/bin/sleep infinity',
                                                         binds=['{0}:/tmp/salt:ro'.format(tmpdir)],
                                                         interactive=True, tty=True)
    container_id = ret_debug['create']['Id']
    ret_debug['start'] =__salt__['dockerng.start'](container_id)

    ret_debug['commands'] = []
    # HACK we need a distro agnostic way of installing python
    cmd_ret = __salt__['dockerng.run_all'](container_id, 'zypper -n in --no-recommends python')
    if cmd_ret['retcode'] != 0:
        ret['result'] = False
    ret_debug['commands'].append(cmd_ret)

    # Now execute the state into the container
    # TODO examine the json output because salt-call will return 0 even if a
    # state failed
    cmd_ret = __salt__['dockerng.run_all'](container_id,
                                           'python /tmp/salt/salt-call --out json -l debug --retcode-passthrough --local state.pkg /tmp/salt/salt_state.tgz {trans_tar_sha256} sha256'.format(trans_tar_sha256=trans_tar_sha256.hexdigest()))
    if cmd_ret['retcode'] != 0:
        ret['result'] = False
    ret_debug['commands'].append(cmd_ret)

    ret_debug['stop'] =__salt__['dockerng.stop'](container_id)
    ret = __salt__['dockerng.commit'](container_id, name)

    if 'debug' in kwargs and kwargs['debug']:
        ret['debug'] = ret_debug
    shutil.rmtree(tmpdir)
    return ret
