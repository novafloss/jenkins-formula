# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

import salt.exceptions as exc


view_xml_tmpl = """
<hudson.model.ListView>
  <name>{name}</name>
  <filterExecutors>false</filterExecutors>
  <filterQueue>false</filterQueue>
  <properties class="hudson.model.View$PropertyList"/>
  <jobNames>
    <comparator class="hudson.util.CaseInsensitiveComparator"/>
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

    runcli = __salt__['jenkins.runcli']  # noqa
    update_or_create_xml = __salt__['jenkins.update_or_create_xml']  # noqa

    try:
        old = view_xml = runcli('get-view', name)
    except exc.CommandExecutionError:
        old = None
        view_xml = view_xml_tmpl.format(name=name)

    view_xml = ET.fromstring(view_xml)
    root = view_xml.find('columns')
    root.clear()
    # Indentation
    root.text = "\n    "
    root.tail = "\n  "

    for i, c in enumerate(columns or []):
        element = ET.Element(c)
        next_indent_level = 2 if i in range(len(columns) - 1) else 1
        element.tail = "\n" + next_indent_level * "  "
        root.append(element)

    return update_or_create_xml(name, view_xml, old=old, object_='view')


def absent(name):
    """Ensures jenkins view is absent.

    name
        The name of the view to be present.
    """

    runcli = __salt__['jenkins.runcli']  # noqa
    test = __opts__['test']  # noqa

    ret = {
        'name': name,
        'changes': {},
        'result': None if test else True,
        'comment': ''
    }

    # check exist
    try:
        old = runcli('get-view', name)
    except exc.CommandExecutionError as e:
        ret['comment'] = 'View `{0}` not found'.format(name)
        return ret

    # delete
    if not test:
        try:
            runcli('delete-view', name)
        except exc.CommandExecutionError as e:
            ret['comment'] = e.message
            ret['result'] = False
            return ret

    ret['changes'] = {
        'old': old,
        'new': None,
    }

    return ret


def get_view_jobs(view_str):
    return [e.text for e in ET.fromstring(view_str).find('jobNames').findall('string')]  # noqa


def job_present(name, job=None, jobs=None):
    """Ensure jenkins job is present in a given view.

    name
        The view.

    job
        The job to add to the view.

    jobs
        List of jobs name to add at once.
    """

    runcli = __salt__['jenkins.runcli']  # noqa
    update_or_create_xml = __salt__['jenkins.update_or_create_xml']  # noqa

    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': ''
    }

    if not jobs and not job:
        ret['comment'] = "Missing job name"
        return ret

    if not jobs:
        jobs = [job]

    # check exist
    try:
        old = runcli('get-view', name)
    except exc.CommandExecutionError as e:
        ret['comment'] = e.message
        return ret

    jobs = set(jobs + get_view_jobs(old))

    # parse, clean and update xml
    view_xml = ET.fromstring(old)
    root = view_xml.find('jobNames')
    root.clear()
    # Indentation
    root.text = "\n    "
    root.tail = "\n  "

    for i, job in enumerate(sorted(jobs)):
        job_xml = ET.Element('string')
        job_xml.text = job
        next_indent_level = 2 if i in range(len(jobs) - 1) else 1
        job_xml.tail = "\n" + next_indent_level * "  "
        view_xml.find('jobNames').append(job_xml)

    return update_or_create_xml(name, xml=view_xml, old=old, object_='view')
