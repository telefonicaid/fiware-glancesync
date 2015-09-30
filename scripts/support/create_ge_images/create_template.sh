#!/bin/bash -e
#
# Copyright 2015 Telefónica Investigación y Desarrollo, S.A.U
#
# This file is part of FI-Core project.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For those usages not covered by the Apache version 2.0 License please
# contact with opensource@tid.es
#

# See: https://forge.fiware.org/plugins/mediawiki/wiki/testbed/index.php/FIWARE_LAB_Image_Deployement_Guideline

set -e

export SHARED_NETWORK_ID=$(neutron net-list |awk -e '/node-int-net-01/ {print $2}')
export SECURITY_GROUP_CREATE=sshopen
export SECURITY_GROUP_TEST=allopen
export KEYPAIR=createimage
export CREATESCRIPT=create.sh
export TESTSCRIPT=test.sh
export UPLOAD_FILE=data.tgz
export IMAGES_DIR=~/create_ge_images/
export IP=$(nova floating-ip-list | awk '/^\|[ ]+[0-9]+/ { print $2 }')


cd $(dirname $0)

create_template_ubuntu12() {
  # Parameters: name
  check_params $*
  create_template $1 base_ubuntu_12.04 ubuntu 
}

create_template_ubuntu14() {
  # Parameters: name
  check_params $*
  create_template $1 base_ubuntu_14.04 ubuntu
}

create_template_debian7() {
  # Parameters: name
  check_params $*
  create_template $1 base_debian_7 debian
}

create_template_centos6() {
  # Parameters: name
  check_params $*
  create_template $1 base_centos_6 centos
}

create_template_centos7() {
  # Parameters: name
  check_params $*
  create_template $1 base_centos_7 centos
}


create_template() {
  name=$1
  base_image=$2
  user=$3

  # ask sudo password at start
  sudo true
  # Launch de VM using base image
  echo "launching VM $name $base_image $KEYPAIR $IP m1.small"
  ID=$(nova boot ${name} --flavor m1.small --key-name $KEYPAIR --security-groups $SECURITY_GROUP_CREATE --image ${base_image} --nic net-id=$SHARED_NETWORK_ID | awk -F\| '$2 ~ /[ \t]+id[ \t]+/ {print $3}')
  echo "VM id is $ID"
  sleep 5
  nova floating-ip-associate $ID $IP
  # Wait until ssh is ready
  ussh="ssh -oStrictHostKeyChecking=no"
  if [ -f ~/.ssh/known_hosts ] ; then 
      ssh-keygen -f ~/.ssh/known_hosts -R $IP
  fi
  echo "Waiting until ssh is ready..."
  sleep 30
  until $ussh ${user}@${IP} true 2>/dev/null ; do sleep 10 ; done

  echo "VM is ready"

  # if present, upload file
  if [ -n "${UPLOAD_FILE}" -a -f $IMAGES_DIR/${name}/$UPLOAD_FILE ] ; then
     echo "Uploading ${UPLOAD_FILE}"
     scp $IMAGES_DIR/${name}/$UPLOAD_FILE ${user}@${IP}:
  fi

  # upload create script
  scp $IMAGES_DIR/${name}/$CREATESCRIPT ${user}@${IP}:
  ssh ${user}@${IP} chmod 700 $CREATESCRIPT

  # run script, delete support account,  poweroff the VM
  # Centos requires -t -t because sudo needs tty; with Debian -t -t sometimes 
  # hungs with apt-get upgrade.
  if [ "$user" = "centos" ] ; then
    echo 'Running script in CentOS distribution'
    O="-t"
  else
    echo 'Running script in Debian/Ubuntu distribution'
    O=""
  fi
  set -o pipefail
  ssh $O ${user}@${IP} ./${CREATESCRIPT} 2>&1 |tee $IMAGES_DIR/${name}/create.log
  set +o pipefail
  ssh $O ${user}@${IP} sudo userdel support
  ssh $O ${user}@${IP} sudo rm -rf /home/support $CREATESCRIPT $UPLOAD_FILE
  ssh $O ${user}@${IP} sudo poweroff || true

  # create template from VM, delete VM
  sleep 20
  nova image-create ${ID} ${name}-snapshot --poll
  nova delete ${ID}

  # download snapshot and delete it from server
  echo "downloading image"
  glance image-download --file $IMAGES_DIR/${name}/tmp_image ${name}-snapshot
  echo "deleting image"
  glance image-delete ${name}-snapshot

  # sysprep VM
  echo "running virt-sysprep"
  sudo virt-sysprep -a $IMAGES_DIR/${name}/tmp_image

  # shrink VM
  sudo ./shrink.py $IMAGES_DIR/${name}
  echo "running virt-sparsify"
  sudo virt-sparsify  $IMAGES_DIR/${name}/tmp_image $IMAGES_DIR/${name}/tmp_image.new
  rm -f $IMAGES_DIR/${name}/tmp_image
  mv $IMAGES_DIR/${name}/tmp_image.new $IMAGES_DIR/${name}/tmp_image

  # boot centOS images and poweroff after reboot; this is required because
  # SELinux relabeling.
  if [ "$user" = "centos" ] ; then
      sudo kvm  -no-reboot -nographic  -m 2048 -hda $IMAGES_DIR/${name}/tmp_image
  fi

  # upload template and delete file
  echo "uploading image"
  glance image-create --name ${name}_rc --disk-format qcow2 --container-format bare --is-public False --file $IMAGES_DIR/${name}/tmp_image
  rm -f $IMAGES_DIR/${name}/tmp_image

  # test template
  test_template $name $user
}

test_template() {
  name=$1
  user=$2

  # launch a VM using the new template
  echo "Launching a testing VM"
  ID=$(nova boot test-${name} --security-groups $SECURITY_GROUP_TEST --flavor m1.small --key-name $KEYPAIR --image ${name}_rc --nic net-id=$SHARED_NETWORK_ID | awk -F\| '/\|[ \t]+id[ \t]+\|/ {print $3}')
  echo "VM id: $ID"
  sleep 5
  nova floating-ip-associate $ID $IP
  # Wait until ssh is reading
  ussh="ssh -oStrictHostKeyChecking=no"
  ssh-keygen -f ~/.ssh/known_hosts -R $IP
  echo "Waiting until ssh is ready..."
  sleep 30
  until $ussh ${user}@${IP} true 2>/dev/null ; do sleep 10 ; done

  echo "Running the test"
  # run test script
  export USERNAME=${user}
  chmod 700 $IMAGES_DIR/${name}/${TESTSCRIPT}
  set -o pipefail
  $IMAGES_DIR/${name}/${TESTSCRIPT} 2>&1 |tee $IMAGES_DIR/${name}/test.log
  set +o pipefail

  echo "Success. Deleting the VM"
  # delete the VM
  nova delete $ID
}

check_params() {
  if [ ! $# -eq 1 ] ; then
    echo  "Use: $0 name" >&2
    exit 0
  fi
}
