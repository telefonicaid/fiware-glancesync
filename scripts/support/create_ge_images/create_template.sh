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

# Force use of apt-get installed packages instead of the pip ones
export PATH=/usr/bin:$PATH ; export PYTHONPATH=/usr/lib/python2.7/dist-packages

export SHARED_NETWORK_ID=$(neutron net-list |awk -e '/node-int-net-01/ {print $2}')
export SECURITY_GROUP_CREATE=sshopen
export SECURITY_GROUP_TEST=allopen
export KEYPAIR=createimage
export CREATESCRIPT=create.sh
export TESTSCRIPT=test.sh
export UPLOAD_FILE=data.tgz
export IMAGES_DIR=~/create_ge_images/
export IP=$(nova floating-ip-list | awk '/^\|[ ]+[0-9]+/ { print $2 }')
export FLAVOR=${FLAVOR:-m1.small}

cd $(dirname $0)

wait_ssh() {
  user=$1
  if [ -f ~/.ssh/known_hosts ] ; then 
      ssh-keygen -f ~/.ssh/known_hosts -R $IP
  fi
  echo "Waiting until ssh is ready..."
  sleep 30
  tries=25
  ussh="ssh -i $HOME/.ssh/createtestimage -oStrictHostKeyChecking=no"
  until $ussh ${user}@${IP} true ; do
     sleep 10 
     ((tries-=1))
     if [ $tries -eq 0 ] ; then
        echo "Timeout while waiting for ssh."
        exit -1
     fi
  done
  echo "VM is ready for ssh"

}
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

launch_vm() {
  # $1 name, $2 flavor, $3 security group, $4 image
  nova boot $1 --flavor $2 --key-name $KEYPAIR --security-groups $3 --image $4 --nic net-id=$SHARED_NETWORK_ID
}

launch_vm_get_id() {
  launch_vm $* | awk -F\| '$2 ~ /[ \t]+id[ \t]+/ {print $3}'
}

create_template() {
  name=$1
  base_image=$2
  user=$3
  DIR=$IMAGES_DIR/${name}

  I="-i $HOME/.ssh/createtestimage"

  if [ $TEST_ONLY ] ; then
     test_template $name $user
     exit
  fi
  # ask sudo password at start
  sudo true
  # Launch de VM using base image
  echo "launching VM $name $base_image $KEYPAIR $IP $FLAVOR"
  ID=$(launch_vm_get_id ${name} $FLAVOR $SECURITY_GROUP_CREATE $base_image)

  echo "VM id is $ID"
  sleep 5
  nova floating-ip-associate $ID $IP

  # Wait until ssh is ready
  wait_ssh $user

  # if present, upload file
  if [ -n "${UPLOAD_FILE}" -a -f $IMAGES_DIR/${name}/$UPLOAD_FILE ] ; then
     echo "Uploading ${UPLOAD_FILE}"
     scp $I $IMAGES_DIR/${name}/$UPLOAD_FILE ${user}@${IP}:
  fi

  # upload creation script
  scp $I $DIR/$CREATESCRIPT ${user}@${IP}:
  ssh $I ${user}@${IP} chmod 700 $CREATESCRIPT

  # run script, delete support account,  poweroff the VM
  # Centos requires -t -t because sudo needs tty; with Debian -t -t sometimes 
  # hungs with apt-get upgrade.
  if [ "$user" = "centos" ] ; then
    echo 'Running script in CentOS distribution'
    O="$I -t"
  else
    echo 'Running script in Debian/Ubuntu distribution'
    O="$I"
  fi
  set -o pipefail
  ssh  $O ${user}@${IP} ./${CREATESCRIPT} 2>&1 |tee $DIR/create.log
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
  glance image-download --file $DIR/tmp_image ${name}-snapshot
  echo "deleting image"
  glance image-delete ${name}-snapshot

  # sysprep VM
  echo "running virt-sysprep"
  sudo virt-sysprep -a $DIR/tmp_image

  # shrink VM
  sudo ./shrink.py $DIR
  echo "running virt-sparsify"
  sudo virt-sparsify  $DIR/tmp_image $DIR/tmp_image.new
  rm -f $DIR/tmp_image
  mv $DIR/tmp_image.new $DIR/tmp_image

  # boot centOS images and poweroff after reboot; this is required because
  # SELinux relabeling.
  if [ "$user" = "centos" ] ; then
      sudo kvm  -no-reboot -nographic  -m 2048 -hda $DIR/tmp_image
  fi

  # upload template and delete file
  echo "uploading image"
  glance image-create --name ${name}_rc --disk-format qcow2 --container-format bare --is-public False --file $DIR/tmp_image
  rm -f $DIR/tmp_image

  # test template
  test_template $name $user
}

test_template() {
  name=$1
  user=$2
  export USERNAME=${user}

  if [ $TEST_USING_VM ] ; then
     echo "Launching a tester VM"
     ID2=$(launch_vm_get_id tester-${name} m1.tiny $SECURITY_GROUP_CREATE base_debian_7)

     echo "VM id: $ID2"
  fi

  # launch a VM using the new template
  echo "Launching a testing VM"
  ID=$(launch_vm_get_id test-${name} $FLAVOR $SECURITY_GROUP_TEST ${name}_rc)

  echo "VM id: $ID"
  sleep 5

  if [ $TEST_USING_VM ] ; then
     nova floating-ip-associate $ID2 $IP
     IDSAVE=$ID
     ID=$ID2 
     wait_ssh debian
     DIR=$IMAGES_DIR/${name}
     CP="-o ControlPath=$DIR/cm_%h%p%r"
     eval $(ssh-agent)
     ssh-add ~/.ssh/createtestimage

     ssh -A -i ~/.ssh/createtestimage -o ControlMaster=yes $CP -o ControlPersist=yes debian@$IP true
     scp $CP $DIR/${TESTSCRIPT} debian@$IP:
     ssh $CP debian@$IP chmod 700 $TESTSCRIPT
     cat << EOF | ssh $CP debian@$IP 'cat - > ./testenv'
     export IP=$IP
     export USERNAME=$USERNAME
     export TESTSCRIPT=$TESTSCRIPT
     ssh -o StrictHostKeyChecking=no $USERNAME@$IP true
EOF

     ID=$IDSAVE
     nova floating-ip-associate $ID $IP
     wait_ssh $user
     # Connect to ID2, because we are using the master connection
     set -o pipefail
     ssh $CP debian@$IP '. testenv ; ./${TESTSCRIPT}' 2>&1 |tee $DIR/test.log || touch $DIR/failed
     set +o pipefail
     ssh $CP -O exit debian@$IP
     ssh-agent -k
     nova delete $ID2

  else
     nova floating-ip-associate $ID $IP
     # Wait until ssh is reading
     wait_ssh $user
     # remove sudo credential (to avoid the script use it)
     sudo -k
     DIR=$IMAGES_DIR/${name}
     eval $(ssh-agent)
     ssh-add ~/.ssh/createtestimage

     echo "Running the testing script"
     # run testing script
     chmod 700 $IMAGES_DIR/${name}/${TESTSCRIPT}
     set -o pipefail
     $DIR/${TESTSCRIPT} 2>&1 |tee $DIR/test.log || touch $DIR/failed
     set +o pipefail
     ssh-agent -k

  fi

  if [ -f $DIR/failed ] ; then
        rm $DIR/failed
        echo "Failed."
        exit -1
  fi

  echo "Success. Deleting the VM"
  # delete the VM
  nova delete $ID

  # print the image UUID
  echo "Success. UUID: $(glance image-show ${name}_rc | awk '/^\|[ ]+id/ {print $4}')"
}

check_params() {
  if [ ! $# -eq 1 ] ; then
    echo  "Use: $0 name" >&2
    exit 0
  fi
}
