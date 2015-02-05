# JupyterHub deployment for the compmodels class

This repository contains an Ansible playbook for launching JupyterHub for the
Computational Models of Cognition class at Berkeley.

The setup is a bit complex, so this readme will try to break it down and explain everything that's going on.

## Overview

To understand what's going on behind the scenes, it is probably helpful to know what happens when a user accesses the server.

1. First, they go to the main url for the server.
2. This url actually points to a proxy server which authenticates the SSL connection, and proxies the connection to the JupyterHub instance running on the hub server.
3. The hub server is both a NFS server (to serve user's home directories) and the JupyterHub server. JupyterHub runs in a docker container called "jupyterhub".
4. Users see a JupyterHub login screen. When they click login, they are authenticated. When they access their server, JupyterHub creates a new docker container on one of the node servers running an IPython notebook server. This docker container is called "jupyter-username", where "username" is the user's username.
5. As users open IPython notebooks and run them, they are actually communicating with one of the seven node servers. The URL still appears the same, because the connection is first being proxied to the hub server via the proxy server, and then proxied a second time to the node server via the JupyterHub proxy.
6. Users have access to their home directory, because each node server is also a NFS client with the filesystem mounted at `/home`.

## Proxy server

The proxy server runs [nginx](http://nginx.org/en/) (pronounced "engine x"), which is a reverse HTTP proxy, in a docker container called "nginx". 
It proxies all connections from the main URL to port 8000 on the hub server.

You can verify that the proxy is running with `docker ps`. 
If you need to access logs for the proxy server, you can run `docker logs --tail=10 nginx`, and adjust the tail length as needed.

### Static files

nginx proxies to the hub server, but it also serves the static notebook files directly to save on the number of files that need to be accessed. 
To do this, it mounts a volume from the `jupyter/systemuser` container, which contains all the necessary notebook files. 
However, this also means that if the user server docker images are updated on the node servers, that the `jupyter/systemuser` container must *also* be updated on the proxy server or you may see weird errors because the clients are requesting files that the proxy server has an old version of, or doesn't have at all. 
See [the docker documentation on data volume containers](https://docs.docker.com/userguide/dockervolumes/#creating-and-mounting-a-data-volume-container) for more details on how this works.

## Hub server

The hub server fulfills two functions: it is both the NFS server, hosting all user's home directories, and it is the JupyterHub server.

### NFS

[NFS](http://en.wikipedia.org/wiki/Network_File_System) is the Network File System. 
It requires there to be a host server, where the files actually exist, and then any number of client servers that mount the NFS filesystem. 
Once the filesystem is mounted, it behaves just like a normal filesystem.

The hub server on its own only has about 28GB of disk space, so to supplement this, we have about 3TB of additional storage mounted at `/var/lib/docker`.

The original copies of all files are located at `/var/lib/docker/export/home` (the directory `/var/lib/docker/export` is the root of the NFS host filesystem).
They are additionally mounted at `/home` on the hub server, and that is the location from which they should *always* be accessed.

There is a cron job that runs every hour to back up the files in `/home` using the script `/srv/backup/duplicity.sh`.
The script runs [duplicity](http://duplicity.nongnu.org/), which is a backup service that performs a full backup every seven days and otherwise performs incremental backups.
The files get encrypted and then backed up to a Rackspace Cloud Files container, from which they can also be restored, if necessary.

Logs for NFS aren't in a separate log file; they can be found just in `/var/log/syslog`.

### JupyterHub

The JupyterHub setup itself is actually pretty straightforward.
JupyterHub runs in a docker container from the image `compmodels/jupyterhub`, which is built from `jupyter/jupyterhub`.
The differences are that our version of JupyterHub uses a special blend of GitHub authentication with local system users (called [docker-oathenticator](https://github.com/jhamrick/docker-oauthenticator)) and spawns user servers inside docker containers on the node servers using a spawner based on the [system user docker spawner](https://github.com/jupyter/dockerspawner).
What this basically means is:

1. Users are created on the hub server with a username that needs to be the same as their GitHub username.
2. In addition to their username, JupyterHub stores the pid of each user.
3. When they login, JupyterHub authenticates the users with GitHub.
4. Once authenticated, JupyterHub spawns a docker container on one of the node servers and mounts the user's home directory inside the container.
5. A user is created inside the docker container with the appropriate username and pid, so that they have access to the files in their home directory.

You should be able to see the JupyterHub docker container with `docker ps`. To get the JupyterHub logs, you can run `docker logs --tail=10 jupyterhub`.

### Swarm

To spawn the user docker containers, we use a load-balancing clustering system called [swarm](https://github.com/docker/swarm).
Essentially, swarm exposes an interface that looks just like the normal docker interface, and figures out in the background where to start new containers.
For example, to get a list of the docker containers that are running through swarm (i.e., the user containers that are running on all node servers):

```
docker --tls -H 127.0.0.1:2735 ps
```

To get the logs for a container running through swarm, you can run `docker --tls -H 127.0.0.1:2735 logs --tail=10 jupyter-username`, where `username` is the username for the user that you want logs from.

The actual logs for swarm itself are stored at `/var/log/swarm.log`.

### Culling containers

Each docker container started through swarm is allocated 1GB of memory (currently there is no limit on CPU, but if a problem arises, we can institute one as well).
Each node server has 32GB of memory, meaning that we can run about 31*7=217 containers at once.
We actually have slightly more users than that, so we've set up a script that runs every hour and shuts down user containers if they haven't been accessed in 24 hours.
The script can be run as follows:

```
cd /root/cull
export JPY_API_TOKEN=`cat ../stats/jpy_api_token`
python3 ./cull_idle_servers.py --timeout=86400 --cull_every=3600 --log_file_prefix=cull.log
```

You can background the process by pressing `Ctrl-z` and then running the command `bg`. Logs will go into the `cull.log` file.

Note: there is currently a bug in JupyterHub that causes the culling script to encounter a bunch of timeout errors because each server takes several seconds to shutdown.
This has been fixed in JupyterHub, but we haven't updated to the new version yet because it will cause a service interruption.
In the meantime, the errors are mostly harmless; the user servers still end up getting shutdown.

## Node servers

In general, the node servers probably don't need to be accessed directly because logs for all the user containers can be accessed through swarm on the hub server.

Each node server is a NFS client, with the NFS filesystem mounted at `/home`.
Additionally, each node server is set up to run the singleuser IPython notebook servers in docker containers.
The image is based on `jupyter/systemuser`, with the only differences being that `nbgrader` is installed so that students can validate and submit their assignments, and that terminado is installed so that users can have access to a terminal if they so desire.

## Potential issues and bugs

### Swarm leaks file descriptors

Every time a user container is started or stopped, swarm opens a new file and then never closes it.
There is a limit on the number of files that a process can have open (1024), so eventually swarm will reach this limit.
When this happens, you will see in the JupyterHub and swarm logs errors that look like "Too many open files".
You can verify the problem by checking the number of files that swarm has open:

```
lsof -a -p $(pidof swarm) | wc -l
```

If this number returned by this command gets up to 1024, then users trying to access their server will get a "500: Interal Server Error" message.
The solution for now (until the bug is fixed in swarm proper) is to periodically restart swarm. First, stop swarm:

```
daemon --name swarm --stop
```

Verify that it's not running with `ps aux | grep swarm` (you should only see the grep process). Then start it again with:

```
daemon -n swarm -o /var/log/swarm.log -- swarm --debug manage --tlsverify --tlscacert=/root/.docker/ca.pem --tlscert=/root/.docker/cert.pem --tlskey=/root/.docker/key.pem --discovery file:///srv/cluster -H=127.0.0.1:2735
```

## Setup

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

## Deploying

:warning: Note: you'll need to install Ansible from source (`devel` branch) to
    get the current versions of the Docker modules.

To deploy this setup:

```
./script/deploy
```

Note that this will stop JupyterHub if it is currently running -- so don't run
this when people might be using the hub!

Required variables in secrets.yml (or secrets.vault.yml):

- ssl_key: the SSL key
- ssl_cert: the SSL certificate
- github_client_id (the client id as provided by the GitHub app)
- github_client_secret (the client secret as provided by the GitHub app)
- oauth_callback_url (the callback url, the same as specified in the GitHub app)
- configproxy_auth_token (a smallish random string - `openssl rand -hex 16`)
- cookie_secret (a large-ish random hex string - (`openssl rand -hex 2048`))

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
