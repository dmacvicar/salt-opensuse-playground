# -*- coding: utf-8 -*-

'''
Module to manage filesystem snapshots using salt
'''
from salt.exceptions import SaltInvocationError, CommandExecutionError
import logging
import os
import time
from pwd import getpwuid

SNAPPER_BIN = '/usr/bin/snapper'

try:
    import dbus
    HAS_DBUS = True
except ImportError:
    HAS_DBUS = False

HAS_SNAPPER = os.path.isfile(SNAPPER_BIN) and os.access(SNAPPER_BIN, os.X_OK)


def __virtual__():
    if HAS_DBUS and HAS_SNAPPER:
        return 'snapper'
    else:
        return (False, 'The snapper module cannot be loaded:'
                ' missing snapper or python-dbus')


bus = dbus.SystemBus()
log = logging.getLogger(__name__)
snapper = dbus.Interface(bus.get_object('org.opensuse.Snapper', '/org/opensuse/Snapper'),
                         dbus_interface='org.opensuse.Snapper')


def _snapshot_to_data(snapshot):
    data = {}

    data['id'] = snapshot[0]
    data['type'] = ['single', 'pre', 'post'][snapshot[1]]
    data['pre'] = snapshot[2]

    if snapshot[3] != -1:
        data['timestamp'] = snapshot[3]
    else:
        data['timestamp'] = time.time()

    data['user'] = getpwuid(snapshot[4])[0]
    data['description'] = snapshot[5]
    data['cleanup'] = snapshot[6]

    data['userdata'] = {}
    for k, v in snapshot[7].items():
        data['userdata'][k] = v

    return data


def _dbus_exception_to_reason(exc):
    '''
    Returns a error message from a snapper DBusException
    '''
    error = exc.get_dbus_name()
    if error == 'error.unknown_config':
        return 'Unknown configuration'
    elif error == 'error.illegal_snapshot':
        return 'Invalid snapshot'
    else:
        return exc.get_dbus_name()


def list_snapshots(config='root'):
    try:
        snapshots = snapper.ListSnapshots(config)
        return [_snapshot_to_data(s) for s in snapshots]
    except dbus.DBusException as exc:
        raise CommandExecutionError(
            'Error encountered while listing snapshots: {0}'
            .format(_dbus_exception_to_reason(exc))
        )


def get_snapshot(number=0, config='root'):
    try:
        snapshot = snapper.GetSnapshot(config, int(number))
        return _snapshot_to_data(snapshot)
    except dbus.DBusException as exc:
        raise CommandExecutionError(
            'Error encountered while retrieving snapshot: {0}'
            .format(_dbus_exception_to_reason(exc))
        )


def list_configs():
    try:
        configs = snapper.ListConfigs()
        return dict((config[0], config[2]) for config in configs)
    except dbus.DBusException as exc:
        raise CommandExecutionError(
            'Error encountered while listing configurations: {0}'
            .format(_dbus_exception_to_reason(exc))
        )


def _config_filter(x):
    if isinstance(x, bool):
        return 'yes' if x else 'no'
    return x


def set_config(name='root', **kwargs):
    try:
        data = dict((k.upper(), _config_filter(v)) for k, v in
                    kwargs.iteritems() if not k.startswith('__'))
        snapper.SetConfig(name, data)
    except dbus.DBusException as exc:
        raise CommandExecutionError(
            'Error encountered while setting configuration {0}: {1}'
            .format(name, _dbus_exception_to_reason(exc))
        )


def get_config(name='root'):
    try:
        config = snapper.GetConfig(name)
        return config
    except dbus.DBusException as exc:
        raise CommandExecutionError(
            'Error encountered while retrieving configuration: {0}'
            .format(_dbus_exception_to_reason(exc))
        )


def changed_files(config='root', num_pre=None, num_post=None):
    try:
        snapper.CreateComparison(config, int(num_pre), int(num_post))
        files = snapper.GetFiles(config, int(num_pre), int(num_post))
        return [file[0] for file in files]
    except dbus.DBusException as exc:
        raise CommandExecutionError(
            'Error encountered while listing changed files: {0}'
            .format(_dbus_exception_to_reason(exc))
        )


