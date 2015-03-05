#!/usr/bin/python
# -*- coding: utf-8 -*-

import tarfile
import os
import shutil

def extract_to(module, src, pth, prefix, user, overwrite=False):
    root = os.path.abspath(os.path.join(pth, prefix))
    ro_root = os.path.abspath(os.path.join(pth, prefix + " (read only)"))
    if not root.startswith(pth):
        module.fail_json(msg="Root path is invalid: {}".format(root))

    # Skip existing directories, if we're not overwriting
    if os.path.exists(root) and not overwrite:
        return False

    # Remove directory, if it already exists
    if os.path.exists(root):
        shutil.rmtree(root)
    if os.path.exists(ro_root):
        shutil.rmtree(ro_root)

    # Extract the archive
    tf = tarfile.open(src, 'r:gz')
    tf.extractall(pth)
    tf.close()

    # Set permissions
    module.run_command(
        'chown -R {}:{} "{}"'.format(user, user, root), check_rc=True)
    module.run_command(
        'chmod -R u+rwX,og-rwx "{}"'.format(root), check_rc=True)

    # Create a read-only version
    shutil.copytree(root, ro_root)
    module.run_command(
        'chown -R {}:{} "{}"'.format(user, user, ro_root), check_rc=True)
    module.run_command(
        'chmod -R u+rX,u-w,og-rwx "{}"'.format(ro_root), check_rc=True)

    return True


def main():
    module = AnsibleModule(
        argument_spec={
            'src': dict(required=True),
            'users': dict(required=True, type='list'),
            'skeldir': dict(default=''),
            'overwrite': dict(default=False, type='bool')
        }
    )

    src = module.params["src"]
    users = module.params["users"]
    skeldir = module.params["skeldir"]
    overwrite = module.params["overwrite"]

    # Open the tarfile, figure out the prefix
    tf = tarfile.open(src, 'r:gz')
    prefix = os.path.commonprefix(tf.getnames()).rstrip("/")
    if prefix != '':
        member = tf.getmember(prefix)
        if not member.isdir():
            prefix = os.path.dirname(prefix)
    tf.close()
    if prefix == '':
        module.fail_json(msg="Archive has no common prefix")

    # Copy to the skeleton directory
    if skeldir != "":
        skeldir = os.path.abspath(skeldir)
        if skeldir in ("/", "/root", "/home"):
            module.fail_json(msg="Skeleton directory is {}, danger!".format(skeldir))
        extract_to(module, src, skeldir, prefix, "root", overwrite=True)

    changed = False
    changed_users = []

    # Extract the archive into the home directory of each user
    for user in users:
        homedir = os.path.abspath('/home/{}'.format(user))
        if not homedir.startswith('/home/'):
            module.fail_json(msg="Home directory is invalid: {}".format(homedir))
        if not os.path.exists(homedir):
            module.fail_json(msg="Home directory does not exist: {}".format(homedir))

        if extract_to(module, src, homedir, prefix, user, overwrite=overwrite):
            changed = True
            changed_users.append(user)

    module.exit_json(
        changed=changed,
        prefix=prefix,
        users=changed_users
    )

from ansible.module_utils.basic import *
main()
