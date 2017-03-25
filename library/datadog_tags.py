#!/usr/bin/python
# -*- coding: utf-8 -*-
#

# Import Datadog
try:
    from datadog import initialize, api
    HAS_DATADOG = True
except:
    HAS_DATADOG = False

ANSIBLE_METADATA = {'status': ['preview'],
                    'supported_by': 'community',
                    'version': '1.0'}

DOCUMENTATION = '''
---
module: datadog_tags
short_description: Posts tags to DataDog service
description:
- "Allows to post tags to DataDog (www.datadoghq.com) service."
- "Uses http://docs.datadoghq.com/ja/api/#tags API."
version_added: ""
author:
- "Yohei Kawahara (@inokappa)"
notes: []
requirements: []
options:
    api_key:
        description: ["Your DataDog API key."]
        required: true
        default: null
    app_key:
        description: ["Your DataDog app key."]
        required: true
    host:
        description: ["The Datadog Host."]
        required: true
        default: null
    tags:
        description: ["Comma separated list of tags to apply to the event."]
        required: false
        default: null
'''

EXAMPLES = '''
- name: Test datadog_tags(present)
  datadog_tags:
    state: present
    host: MyHost
    tags: 'aa,bb,cc,dd'
    api_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    app_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- name: Test datadog_tags(absent)
  datadog_tags:
    state: absent
    host: MyHost
    api_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    app_key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
'''

def _get_host(host):
    res = api.Infrastructure.search(q=host)
    return res['results']['hosts']

def _have_tags(module):
    res = api.Tag.get(module.params['host'])
    diff = (list(set(res['tags']) & set(module.params['tags'])))
    return set(res['tags']) == set(diff) and set(module.params['tags']) == set(diff)

def _post_tags(module):
    host = _get_host(module.params['host'])

    if not host:
        module.exit_json(changed=False)

    have_tags = _have_tags(module)
    if have_tags == False:
        try:
            msg = api.Tag.create(
                host=module.params['host'],
                    tags=module.params['tags'],
                    source_type_name='ansible'
                )
            if msg['host'] != module.params['host']:
                module.fail_json(msg=msg)

            module.exit_json(changed=True, msg=msg)
        except Exception:
            e = get_exception()
            module.fail_json(msg=str(e))
    else:
        module.exit_json(changed=False)

def _delete_tags(module):
    host = _get_host(module.params['host'])

    if not host:
        module.exit_json(changed=False)

    res = api.Tag.get(module.params['host'])
    if len(res['tags']) == 0:
        module.exit_json(changed=False)

    try:
        msg = api.Tag.delete(module.params['host'])
        module.exit_json(changed=True, msg=msg)
    except Exception:
        e = get_exception()
        module.fail_json(msg=str(e))

def main():
    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(required=True, no_log=True),
            app_key=dict(required=True, no_log=True),
            host=dict(required=True),
            tags=dict(required=False, type='list'),
            state=dict(required=True, default=None)
        )
    )

    if not HAS_DATADOG:
        module.fail_json(msg='datadogpy required for this module')

    options = {
        'api_key': module.params['api_key'],
        'app_key': module.params['app_key']
    }

    initialize(**options)

    if module.params['state'] == 'present':
        _post_tags(module)
    elif module.params['state'] == 'absent':
        _delete_tags(module)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
