#!/bin/bash

source ./duplicity.sh

duplicity remove-all-but-n-full 2 \
        --force \
        --verbosity notice \
        --encrypt-key "$gpg_key" \
        --log-file /srv/backup/duplicity.log \
         "${dest}"
