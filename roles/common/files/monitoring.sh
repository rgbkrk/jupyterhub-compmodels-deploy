#!/bin/sh -e

if [ -z $(which rackspace-monitoring-agent) ]; then
    sh -c 'echo "deb http://stable.packages.cloudmonitoring.rackspace.com/ubuntu-14.04-x86_64 cloudmonitoring main" > /etc/apt/sources.list.d/rackspace-monitoring-agent.list'
    curl https://monitoring.api.rackspacecloud.com/pki/agent/linux.asc | apt-key add -
    apt-get update
    apt-get install rackspace-monitoring-agent
    rackspace-monitoring-agent --setup --username $1 --apikey $2
    service rackspace-monitoring-agent start
else
    service rackspace-monitoring-agent restart
fi
