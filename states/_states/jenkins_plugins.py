# -*- coding: utf-8 -*-
import re

import salt.exceptions as exc


def _update(name, names=None, updateall=True, **kwargs):

    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': ''
    }

    if updateall:
        names = []
    elif not names:
        names = [name]

    _runcli = __salt__['jenkins.runcli']  # noqa
    try:
        stdout = _runcli('list-plugins')
    except exc.CommandExecutionError as e:
        ret['comment'] = e.message
        return ret

    # match with ex.: 'maven-plugin  Maven plugin  2.7.1 (2.8)'
    RE_UPDATE = '(\w.+?)\s.*\s(\d+.*) \((.*)\)'
    for l in stdout.strip().split('\n'):

        m = re.match(RE_UPDATE, l)
        # no need to update
        if not m:
            continue

        short_name, current, update = m.groups()
        # no need to update
        if names and short_name not in names:
            continue

        try:
            _runcli('install-plugin', short_name)
        except exc.CommandExecutionError as e:
            ret['comment'] = e.message
            return ret

        ret['changes'][short_name] = {
            'old': current,
            'new': update,
        }

    ret['result'] = True
    return ret


(
    IS_INSTALLED,
    NOT_AVAILABLE
) = range(2)


def _info(short_name):

    # get info
    _runcli = __salt__['jenkins.runcli']  # noqa
    stdout = _runcli('list-plugins {0}'.format(short_name))

    # check info
    RE_INSTALL = '(\w.+?)\s.*\s(\d+.*)'
    m = re.match(RE_INSTALL, stdout)
    if not m:
        return NOT_AVAILABLE, 'Invalid info for {0}: {1}'.format(short_name, stdout)  # noqa

    __, version = m.groups()
    return IS_INSTALLED, version


def installed(name, names=None, **kwargs):
    """Ensures jenkins plugins are present.

    name
        The name of one specific plugin to ensure.

    names
        The names of specifics plugins to ensure.
    """
    ret = _update(name, names=names, updateall=False)

    if not names:
        names = [name]

    _runcli = __salt__['jenkins.runcli']
    for short_name in names:

        # just updated
        if short_name in ret['changes']:
            continue

        # get info before install
        try:
            status, info = _info(short_name)
        except exc.CommandExecutionError as e:
            ret['comment'] = e.message
            return ret

        # installed
        if status == IS_INSTALLED:
            ret['changes'][short_name] = {
                'old': info,
                'new': None,
            }
            continue

        # install
        try:
            stdout = _runcli('install-plugin {0}'.format(short_name))
        except exc.CommandExecutionError as e:
            ret['comment'] = e.message
            return ret

        # get info
        try:
            stdout = _runcli('list-plugins {0}'.format(short_name))
        except exc.CommandExecutionError as e:
            ret['comment'] = e.message
            return ret

        # get info after install
        try:
            status, info = _info(short_name)
        except exc.CommandExecutionError as e:
            ret['comment'] = e.message
            return ret

        # invalid info
        if status == NOT_AVAILABLE:
            ret['comment'] = info
            return ret

        # fresh install
        ret['changes'][short_name] = {
            'old': None,
            'new': info,
        }

    ret['result'] = True
    return ret


def updated(name, names=None, updateall=True, **kwargs):
    """Updates jenkins plugins.

    name
        The name of one specific plugin to update

    names
        The names of specifics plugins to update.

    updateall
        Boolean flag if we want to update all the updateable plugins
        (default: True).
    """
    return _update(name, names=names, updateall=updateall)
