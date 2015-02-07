#!/bin/bash

source ./duplicity.sh

duplicity restore --encrypt-key "$gpg_key" "${dest}" "$1"
