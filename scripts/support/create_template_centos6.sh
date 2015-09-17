#!/bin/bash

cd $(dirname $0)
. create_template.sh

# Parameters: name, key, ip, scripts, test_script

create_template_centos6 $1 $2 $3 $4 $5

