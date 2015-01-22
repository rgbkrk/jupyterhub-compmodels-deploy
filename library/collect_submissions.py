#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import tarfile

def main():
    module = AnsibleModule(
        argument_spec={
            'src': dict(required=True),
            'dest': dict(required=True),
            'users': dict(required=True, type='list'),
            'overwrite': dict(default=False, type='bool')
        }
    )

    src = module.params["src"]
    dest = module.params["dest"]
    users = module.params["users"]
    overwrite = module.params["overwrite"]

    if os.path.exists(dest) and not overwrite:
        module.exit_json(changed=False)
    elif os.path.exists(dest):
        os.remove(dest)

    tf = tarfile.open(dest, 'w:gz')

    for user in users:
        homedir = os.path.abspath('/home/{}'.format(user))
        if not homedir.startswith('/home/'):
            tf.close()
            os.remove(dest)
            module.fail_json(msg="Home directory is invalid: {}".format(homedir))
        if not os.path.exists(homedir):
            tf.close()
            os.remove(dest)
            module.fail_json(msg="Home directory does not exist: {}".format(homedir))

        pth = os.path.join(homedir, src)
        if not os.path.exists(pth):
            continue

        tf.add(pth, arcname="{}.tar.gz".format(user))

    tf.close()

    module.exit_json(changed=True)


from ansible.module_utils.basic import *
main()
