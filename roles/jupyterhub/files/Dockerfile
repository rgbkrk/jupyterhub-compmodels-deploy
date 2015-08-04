FROM jupyter/jupyterhub

MAINTAINER Jessica Hamrick <jhamrick@berkeley.edu>

# We need to update pip, otherwise the version of requests that
# is installed by dockerspawner breaks things.
RUN pip3 install --upgrade pip

# Install dockerspawner and oauthenticator
RUN /usr/local/bin/pip3 install docker-py
RUN /usr/local/bin/pip3 install git+git://github.com/jupyter/dockerspawner.git
RUN /usr/local/bin/pip3 install git+git://github.com/ryanlovett/jh-google-oauthenticator.git

# Add variable to allow connecting to the docker swarm
ENV DOCKER_HOST https://127.0.0.1:2376

# Create oauthenticator directory -- this is where we'll put the userlist later
RUN mkdir /srv/oauthenticator
ENV OAUTHENTICATOR_DIR /srv/oauthenticator
RUN chmod 700 /srv/oauthenticator

# add the userlist, spawner, and authenticator
ADD userlist /srv/oauthenticator/userlist
ADD swarmspawner.py /srv/oauthenticator/swarmspawner.py
ADD docker_oauth.py /srv/oauthenticator/docker_oauth.py

# set working directory to the jupyterhub directory
WORKDIR /srv/jupyterhub
