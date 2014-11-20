# JupyterHub deployment for the compmodels class

This repository contains an Ansible playbook for launching JupyterHub for the
Computational Models of Cognition class at Berkeley.

Setup is currently:

* nginx on one server for SSL termination
* primary jupyterhub launch
* releasing an assignment to students' home directories

:warning: Note: you'll need to install Ansible from source (`devel` branch) to
    get the current versions of the Docker modules.

## Proxy

To deploy the proxy server:

```
./script/deploy_proxy
```

## JupyterHub

To deploy JupyterHub:

```
./script/deploy
```

Note that this will stop JupyterHub if it is currently running -- so don't run
this when people might be using the hub!

## Releasing assignments

To release an assignment:

```
./script/release
```

This will prompt you for the name of the assignment. You'll need to have also
specified the path to the assignments in `vars.local.yml` (if that file does not
exist, copy `vars.yml` and then edit it).

Also, note that if the assignment folder already exists in the user's home
directory, then it will NOT be overridden by default.

## Collecting assignments

Coming soon!

## Returning assignments

Coming soon!
