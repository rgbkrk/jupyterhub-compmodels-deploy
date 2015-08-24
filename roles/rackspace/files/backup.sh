#!/bin/sh -e

if [ -z $(which driveclient) ]; then
    apt-get update
    apt-get install python-apt
    cd /tmp
    wget 'http://agentrepo.drivesrvr.com/debian/cloudbackup-updater-latest.deb'
    dpkg -i /tmp/cloudbackup-updater-latest.deb || true
    apt-get install -f
    cloudbackup-updater -v
    /usr/local/bin/driveclient --configure -u $1 -k $2
    service driveclient start
else
    service driveclient restart
fi
