#!/bin/bash

# remove existing file
rm -f $1

# populate instructors and students
users=$(cut -d: -f1 /etc/passwd)
for user in $users; do
    is_instructor=$(groups $user | grep "\\binstructors\\b")
    if [[ ! -z "$is_instructor" ]]; then
        echo "$user admin" >> $1
    fi

    is_student=$(groups $user | grep "\\bstudents\\b")
    if [[ ! -z "$is_student" ]]; then
        echo "$user" >> $1
    fi
done
