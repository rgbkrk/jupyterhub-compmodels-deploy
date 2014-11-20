#!/usr/bin/python
# -*- coding: utf-8 -*-

import tarfile
import os
import shutil

def main():
    module = AnsibleModule(
        argument_spec={
            'src': dict(required=True),
            'users': dict(required=True, type='list'),
            'overwrite': dict(default=False, type='bool')
        }
    )

    src = module.params["src"]
    users = module.params["users"]
    overwrite = module.params["overwrite"]

    # Open the tarfile, figure out the prefix
    tf = tarfile.open(src, 'r:gz')
    prefix = os.path.commonprefix(tf.getnames())
    if prefix == '':
        module.fail_json(msg="Archive has no common prefix")
    tf.close()

    # Extract the archive into the home directory of each user
    changed = False
    changed_users = []
    for user in users:
        homedir = os.path.abspath('/home/{}'.format(user))
        if not homedir.startswith('/home/'):
            module.fail_json(msg="Home directory is invalid: {}".format(homedir))
        if not os.path.exists(homedir):
            module.fail_json(msg="Home directory does not exist: {}".format(homedir))

        root = os.path.abspath(os.path.join(homedir, prefix))
        if not root.startswith(homedir):
            module.fail_json(msg="Root path is invalid: {}".format(root))

        # Skip existing directories, if we're not overwriting
        if os.path.exists(root) and not overwrite:
            continue
        else:
            changed = True
            changed_users.append(user)

        # Remove directory, if it already exists
        if os.path.exists(root):
            shutil.rmtree(root)

        # Extract the archive
        tf = tarfile.open(src, 'r:gz')
        tf.extractall(homedir)
        tf.close()

        # Set permissions
        module.run_command(
            'chown -R {}:{} "{}"'.format(user, user, root), check_rc=True)
        module.run_command(
            'chmod -R u+rwX,og-rwx "{}"'.format(root), check_rc=True)

    module.exit_json(
        changed=changed,
        prefix=prefix,
        users=changed_users
    )

from ansible.module_utils.basic import *
main()
