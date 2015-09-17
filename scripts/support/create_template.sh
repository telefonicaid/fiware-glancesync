#/bin/bash
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

export SHARED_NETWORK_ID=008c8d1d-88f3-4c29-847a-7464574f936d
set -e
cd $(dirname $0)

create_template_ubuntu12() {
  # Parameters: name, key, ip, scripts, test_script
  check_params $*
  create_template $1 base_ubuntu_12.04 ubuntu $2 $3 $4 $5
}

create_template_ubuntu14() {
  # Parameters: name, key, ip, scripts, test_script
  check_params $*
  create_template $1 base_ubuntu_14.04 ubuntu $2 $3 $4 $5
}

create_template_debian7() {
  # Parameters: name, key, ip, scripts, test_script
  check_params $*
  create_template $1 base_debian_7 debian $2 $3 $4 $5
}

create_template_centos6() {
  # Parameters: name, key, ip, scripts, test_script
  check_params $*
  create_template $1 base_centos_6 centos $2 $3 $4 $5
}

create_template_centos7() {
  # Parameters: name, key, ip, scripts, test_script
  check_params $*
  create_template $1 base_centos_7 centos $2 $3 $4 $5
}


create_template() {
  name=$1
  base_image=$2
  user=$3
  key=$4
  ip=$5
  script=$6
  test_script=$7

  # ask sudo password at start
  sudo true
  # Launch de VM using base image
  echo "launching VM $name $base_image $key $ip m1.small"
  ID=$(nova boot ${name} --flavor m1.small --key-name $key --image ${base_image} --nic net-id=$SHARED_NETWORK_ID | awk -F\| '$2 ~ /[ \t]+id[ \t]+/ {print $3}')
  #ID=$(./launch_image.py $name $base_image $key $ip m1.small)
  echo "VM id is $ID"
  sleep 5
  nova floating-ip-associate $ID $ip
  unsecuressh="ssh -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no"
  unsecurescp="scp -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no"
  # Wait until ssh is ready
  echo "Waiting until ssh is ready..."
  sleep 30
  until $unsecuressh ${user}@${ip} true 2>/dev/null ; do sleep 10 ; done

  # run script, delete support account,  poweroff the VM
  # Centos requires -t -t because sudo needs tty; with Debian -t -t sometimes 
  # hungs with apt-get upgrade.
  if [ "$user" = "centos" ] ; then
    cat $script - <<EOF | $unsecuressh -t -t ${user}@${ip}

echo "Finish."
exit
EOF
  $unsecuressh -t ${user}@${ip} sudo userdel support
  $unsecuressh -t ${user}@${ip} sudo rm -rf /home/support
  $unsecuressh -t ${user}@${ip} sudo poweroff || true
  echo "sigue"
  else
     cat $script - <<EOF | $unsecuressh ${user}@${ip}

echo "Finish."
exit
EOF
  $unsecuressh  ${user}@${ip} sudo userdel support
  $unsecuressh  ${user}@${ip} sudo rm -rf /home/support
  $unsecuressh  ${user}@${ip} sudo poweroff
  fi
  echo "sigue2"

  # create template from VM, delete VM
  sleep 20
  nova image-create ${ID} ${name}-snapshot --poll
  nova delete ${ID}

  # download snapshot and delete it from server
  glance image-download --file tmp_image --progress ${name}-snapshot
  glance image-delete ${name}-snapshot

  # sysprep VM
  sudo virt-sysprep -a tmp_image
  sudo virt-sparsify  tmp_image tmp_image.new
  rm tmp_image
  mv tmp_image.new tmp_image

  # boot centOS images and poweroff after reboot; this is required because
  # SELinux relabeling.
  if [ "$user" = "centos" ] ; then
      sudo kvm  -no-reboot -nographic  -m 2048 -hda tmp_image
  fi

  # upload template and delete file
  glance image-create --name ${name} --disk-format qcow2 --container-format bare --is-public False --file tmp_image
  rm -f tmp_image

  # test template
  test_template $name $key $ip $test_script
}

test_template() {
  name=$1
  key=$2
  ip=$3
  test_script=$4

  # launch a VM using the new template
  echo "Launching a testing VM"
  # ID = $(./launch_image.py test-$name $name $key $ip m1.small)
  ID=$(nova boot test-${name} --flavor m1.small --key-name $key --image ${name} --nic net-id=$SHARED_NETWORK_ID | awk -F\| '/\|[ \t]+id[ \t]+\|/ {print $3}')
  echo "VM id: $ID"
  sleep 5
  nova floating-ip-associate $ID $ip
  export IP=$ip
  # Wait until ssh is reading
  echo "Waiting until ssh is ready..."
  sleep 30
  until $unsecuressh ${user}@${ip} true 2>/dev/null ; do sleep 10 ; done

  # if present, upload file
  if [ -n "${UPLOAD_FILE}" -a -f $UPLOAD_FILE ] ; then
     $unsecurescp files.tgz ${user}@${ip}:
  fi
  # run test script
  $test_script

  # delete the VM
  nova delete $ID
}

check_params() {
  if [ ! $# -eq 5 ] ; then
    echo  "Use: $0 name key ip script test_script" >&2
    exit 0
  fi
}
