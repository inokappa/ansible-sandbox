#!/usr/bin/python

def main():
    fields = {
        "key1": { "required": True, "type": "str" },
        "key2": { "required": True, "type": "str" }
    }
    module = AnsibleModule(
        argument_spec=fields,
        supports_check_mode=True
    )
    response = {
        "key1": module.params['key1'],
        "key2": module.params['key2']
    }
    module.exit_json(changed=False, meta=response)

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
