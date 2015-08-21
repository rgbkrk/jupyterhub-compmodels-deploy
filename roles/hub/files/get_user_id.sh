#!/bin/bash -e

user=$1
response=$(echo -e "POST /$user HTTP/1.0\r\n" | nc -U /var/run/restuser.sock)
uid=$(echo "$response" | grep -o "\"uid\":\ [0-9]\+" | cut -c 8-)
echo -n $uid
