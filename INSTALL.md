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

Required variables in secrets.yml (or secrets.vault.yml):

- ssl_key: the SSL key
- ssl_cert: the SSL certificate
- github_client_id (the client id as provided by the GitHub app)
- github_client_secret (the client secret as provided by the GitHub app)
- oauth_callback_url (the callback url, the same as specified in the GitHub app)
- configproxy_auth_token (a smallish random string - `openssl rand -hex 16`)
- cookie_secret (a large-ish random hex string - (`openssl rand -hex 2048`))
