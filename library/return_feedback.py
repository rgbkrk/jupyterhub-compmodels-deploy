#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil

def main():
    module = AnsibleModule(
        argument_spec={
            'src': dict(required=True),
            'overwrite': dict(default=False, type='bool')
        }
    )

    src = module.params["src"]
    overwrite = module.params["overwrite"]

    if not os.path.exists(src):
        module.fail_json(msg="Source path does not exist")

    changed = False
    changed_users = []

    # copy feedback to the home directory of each user
    users = sorted(os.listdir(src))
    for user in users:
        homedir = os.path.abspath('/home/{}'.format(user))
        if not homedir.startswith('/home/'):
            module.fail_json(msg="Home directory is invalid: {}".format(homedir))
        if not os.path.exists(homedir):
            module.fail_json(msg="Home directory does not exist: {}".format(homedir))

        userfiles = os.listdir(os.path.join(src, user))
        if len(userfiles) != 1:
            module.fail_json(
                msg="Expected exactly one directory per user, but {} had {}".format(
                    user, len(userfiles)))

        usrsource = os.path.join(src, user, userfiles[0])
        usrdest = os.path.join(homedir, userfiles[0])
        if not os.path.isdir(usrsource):
            module.fail_json(msg="File for user {} is not a directory".format(user))

        # remove existing feedback, or skip it
        if os.path.exists(usrdest):
            if not overwrite:
                continue
            else:
                shutil.rmtree(usrdest)

        # copy the feedback
        shutil.copytree(usrsource, usrdest)

        # set permissions        
        module.run_command(
            'chown -R {}:{} "{}"'.format(user, user, usrdest), check_rc=True)
        module.run_command(
            'chmod -R u+rX,u-w,og-rwx "{}"'.format(usrdest), check_rc=True)

        changed = True
        changed_users.append(user)

    module.exit_json(
        changed=changed,
        users=changed_users
    )

from ansible.module_utils.basic import *
main()
