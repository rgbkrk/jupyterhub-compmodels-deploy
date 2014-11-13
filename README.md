# compmodels jupyterhub deployment

This repository contains an Ansible playbook for launching JupyterHub for the Computational Models class at Berkeley.

Setup is currently:

* nginx on one server for SSL termination
* primary jupyterhub launch

## Launching with Ansible

:warning: Note: you'll need to install Ansible from source (`devel` branch) to get the current versions of the Docker modules.

### "Easy" mode

```
script/deploy
```

### Directly, assuming you have secrets.yml available

```
ansible-playbook site.yml -i inventory
```
