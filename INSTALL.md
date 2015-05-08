# Installation and setup instructions

:warning: Note: you'll need to install Ansible from source (`devel` branch) to
    get the current versions of the Docker modules.

## Generating TLS/SSL certificates

**This only ever needs to be done once!**

You'll need to generate SSL/TLS certificates for the hub server and node servers.
To do this, you can use the [keymaster](https://github.com/cloudpipe/keymaster) docker container.
First, setup the certificates directory, password, and certificate authority:

```
mkdir certificates

touch certificates/password
chmod 600 certificates/password
cat /dev/random | head -c 128 | base64 > certificates/password

KEYMASTER="keymaster="docker run --rm -v $(pwd)/certificates/:/certificates/ cloudpipe/keymaster"

${KEYMASTER} ca
```

Then, to generate a keypair for a server:

```
${KEYMASTER} signed-keypair -n server1 -h server1.website.com -p both -s IP:192.168.0.1
```

where `server1` is the name of a server (e.g. `compmodels`), `server1.website.com` is the hostname for the server, and `192.168.0.1` is the IP address of the server.

You'll need to generate keypairs for the hub server and for each of the node servers.

## Secrets

Copy the `secrets.vault.yml.example` file to `secrets.vault.yml` and edit it to include keys and passwords for your specific deployment. You should then encrypt it using Ansible vault:

```
ansible-vault encrypt secrets.vault.yml
```

It may be helpful to put your Ansible vault password in a file called `vault-password`, so then you can do:

```
ansible-vault encrypt --vault-password-file vault-password secrets.vault.yml
```

You will also need to save host-specific variables (such as certificates) into the `host_vars` directory (one file per host in the inventory). There is a file there called `example` that will tell you what variables need to be defined in those files. One example of something that needs to be in these files are the certificates for the servers running Docker with TLS. If you generated certificates as suggested above, then you will have all your Docker certs in the `certificates` folder. You can copy these to the `host_vars` directory with the helper script `script/assemble_certs` -- you will just need to edit the `assemble_certs` script so that it uses the correct names for your certificates and hosts.

## Users

For the whitelist of users, you need to copy `users.vault.yml.example` to `users.vault.yml` and edit it to include your list of admins and users. Once you are done editing it, you should encrypt it using Ansible vault:

```
ansible-vault encrypt --vault-password-file vault-password users.vault.yml
```

## Other variables

You'll need to set a few other variables. Copy `vars.yml.example` to `vars.yml` and edit it to include specifics for your deployment.
