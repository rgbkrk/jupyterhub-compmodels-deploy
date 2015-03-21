#!/usr/bin/python
# -*- coding: utf-8 -*-

import tempfile
import tarfile
import os

def main():
    module = AnsibleModule(
        argument_spec={
            'src': dict(required=True),
            'dest': dict(required=True),
            'name': dict(required=True),
            'overwrite': dict(default=False, type='bool'),
            'users': dict(default=[], type='list')
        }
    )

    src = module.params["src"]
    dest = module.params["dest"]
    name = module.params["name"]
    overwrite = module.params["overwrite"]
    users = module.params["users"]

    # Check that the source is a directory
    if not os.path.isdir(src):
        module.fail_json(msg="Source {} is not a directory".format(src))

    # Skip, if the destination exists and overwrite is false
    if os.path.exists(dest) and not overwrite:
        module.exit_json(
            changed=False,
            src=src,
            dest=dest,
            name=name
        )

    # Check if the destination exists, and create directories, if necessary
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    if os.path.exists(dest):
        os.remove(dest)

    # Make a temporary file to create the archive
    fd, tmp_dest = tempfile.mkstemp()
    os.close(fd)

    # Make the list of users
    if users == []:
        users = os.listdir(src)

    # Create the tarball
    tf = tarfile.open(tmp_dest, 'w:gz')
    for user in users:
        userpath = os.path.join(src, user)
        for (dirpath, dirnames, filenames) in os.walk(userpath):
            for filename in filenames:
                fullpath = os.path.join(dirpath, filename)
                arcpath = os.path.join(user, name + " Feedback", os.path.relpath(fullpath, userpath))
                tf.add(fullpath, arcname=arcpath)
    tf.close()

    # Move the archive into place
    module.atomic_move(tmp_dest, dest)

    module.exit_json(
        changed=True,
        src=src,
        dest=dest,
        name=name,
        checksum=module.sha1(dest),
        md5sum=module.md5(dest)
    )

from ansible.module_utils.basic import *
main()
