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

set -e
cd $(dirname $0)

create_template_ubuntu12(name, key, ip, script, test_script) {
  create_template(name, base_ubuntu12.04, ubuntu, key, ip, script, test_script)
}

create_template_ubuntu14(name, key, ip, script, test_script) {
  create_template(name, base_ubuntu14.04, ubuntu, key, ip, script, test_script)
}

create_template_debian7(name, key, ip, script, test_script) {
  create_template(name, base_debian7, debian, key, ip, script, test_script)
}

create_template_centos6(name, key, ip, script, test_script) {
  create_template(name, base_centos6, centos, key, ip, script, test_script)
}

create_template_centos7(name, key, ip, script, test_script) {
  create_template(name, base_centos7, centos, key, ip, script, test_script)
}


create_template(name, base_image, user, key, ip, script, test_script) {
  # Launch de VM using base image
  ID = $(./launch_image.py $name $base_image $key $ip m1.small)
  # Wait a few seconds while the VM is booting
  sleep 180

  # run script, delete support account,  poweroff the VM
  ssh ${user}@${ip} < $script
  ssh ${user}@${ip} <<EOF
sudo userdel support
sudo poweroff
EOF

  # create template from VM, delete VM
  nova image-create ${ID} ${name}-snapshot --poll
  nova delete ${ID}

  # download snapshot and delete it from server
  glance image-download --file tmp_image --progress ${name}-snapshot

  # sysprep VM
  sudo virt-sysprep -a tmp_image
  sudo virt-sparsify  tmp_image

  # boot centOS images and poweroff after reboot; this is requires because
  # SELinux relabeling.
  if [ $user -eq centos ] ; then
      sudo kvm  -no-reboot -nographic  -m 2048 -hda tmp_image
  fi

  # upload template and delete file
  glance image-create --name ${name} --disk-format qcow2 --container-format bare --is-public False --file tmp_image
  rm tmp_image

  # launch a VM using the new template
  ID = $(./launch_image.py $name $base_image $key $ip m1.small)
  # Wait a few seconds while the VM is booting
  sleep 180

  # run test script
  $test_script

  # delete the VM
  nova delete $ID
}