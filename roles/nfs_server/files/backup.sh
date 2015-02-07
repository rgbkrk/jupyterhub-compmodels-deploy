#!/bin/bash

source ./duplicity.sh

duplicity --verbosity notice \
        --encrypt-key "$gpg_key" \
        --full-if-older-than 7D \
        --num-retries 3 \
        --asynchronous-upload \
        --volsize 10 \
        --log-file /srv/backup/duplicity.log \
         "${src}" "${dest}"
