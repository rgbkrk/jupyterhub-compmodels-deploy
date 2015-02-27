#!/bin/bash

source /srv/backup/duplicity.sh

duplicity restore --encrypt-key "$gpg_key" "${dest}" "$1"
