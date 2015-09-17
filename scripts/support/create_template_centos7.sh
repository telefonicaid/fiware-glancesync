#!/bin/bash

cd $(dirname $0)
. create_template.sh

# Parameters: name, key, ip, scripts, test_script

create_template_centos7 $1 $2 $3 $4 $5

