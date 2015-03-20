# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

import salt.exceptions as exc


view_xml_tmpl = """
<hudson.model.ListView>
  <name>{name}</name>
  <filterExecutors>false</filterExecutors>
  <filterQueue>false</filterQueue>
  <properties class="hudson.model.View$PropertyList" />
  <jobNames>
    <comparator class="hudson.util.CaseInsensitiveComparator" />
  </jobNames>
  <jobFilters />
  <columns>
  </columns>
  <recurse>false</recurse>
</hudson.model.ListView>
"""  # noqa


def present(name, columns=None):
    """Ensures jenkins view is present.

    name
        The name of the view to be present.

    columns
        List of columns to add in the view.
    """

    _runcli = __salt__['jenkins.runcli']  # noqa
    test = __opts__['test']  # noqa

    ret = {
        'name': name,
        'changes': {},
        'result': None if test else True,
        'comment': ''
    }

    # check exist and continue or create
    try:
        _runcli('get-view', name)
        ret['comment'] = 'View `{0}` exists.'.format(name)
        return ret
    except exc.CommandExecutionError as e:
        pass

    # set columns
    view_xml = ET.fromstring(view_xml_tmpl.format(**{'name': name}))
    for c in columns or []:
        view_xml.find('columns').append(ET.Element(c))

    new = ET.tostring(view_xml.find('.'))

    # create
    if not test:
        try:
            _runcli('create-view', name, input_=new)
        except exc.CommandExecutionError as e:
            ret['comment'] = e.message
            ret['result'] = False
            return ret

    ret['changes'] = {
        'old': None,
        'new': new,
    }
    return ret


def absent(name):
    """Ensures jenkins view is absent.

    name
        The name of the view to be present.
    """

    _runcli = __salt__['jenkins.runcli']  # noqa
    test = __opts__['test']  # noqa

    ret = {
        'name': name,
        'changes': {},
        'result': None if test else True,
        'comment': ''
    }

    # check exist
    try:
        old = _runcli('get-view', name)
    except exc.CommandExecutionError as e:
        ret['comment'] = 'View `{0}` not found'.format(name)
        return ret

    # delete
    if not test:
        try:
            _runcli('delete-view', name)
        except exc.CommandExecutionError as e:
            ret['comment'] = e.message
            ret['result'] = False
            return ret

    ret['changes'] = {
        'old': old,
        'new': None,
    }

    return ret
