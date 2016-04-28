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

IMAGE=ubuntu14.04
USER=ubuntu
set -e
unsecuressh="ssh -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no"
unsecurescp="scp -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no"

sudo true
./launch_image.py ubuntu14.04 ubuntu14.04_cloud_x64 m1.small
sleep 180
$unsecurescp resources/20auto-upgrades activate_support_account.py resources/support-account.conf support_pubkeys/defaultgpg.pub support_pubkeys/defaultssh.pub $USER@10.95.55.170:
cat <<EOF | $unsecuressh $USER@10.95.55.170 -t -t
sudo apt-get update
sudo apt-get -y upgrade
sudo mv activate_support_account.py /sbin
sudo mv 20auto-upgrades /etc/apt/apt.conf.d
sudo mv support-account.conf /etc/init
sudo chown root:root /sbin/activate_support_account.py /etc/init/support-account.conf
sudo chown root:root /etc/apt/apt.conf.d/20auto-upgrades
sudo install -d /etc/fiware-support/
sudo mv defaultgpg.pub defaultssh.pub /etc/fiware-support/
sudo rm -f /var/cache/apt/archives/*.deb
exit
EOF

nova image-create ${IMAGE} ${IMAGE}snapshot --poll
nova delete $IMAGE
IMAGE_ID=$(glance image-list | awk -F\| /${IMAGE}'snapshot/ {gsub(/^[ ]+/,"", $2) ; print $2}')
sudo virt-sysprep -a /var/lib/glance/images/$IMAGE_ID
#sudo virt-sparsify  /var/lib/glance/images/$IMAGE_ID ${IMAGE}.new
sudo qemu-img convert -O qcow2 /var/lib/glance/images/$IMAGE_ID ${IMAGE}.new
glance image-delete ${IMAGE}snapshot

glance image-create --name ${IMAGE}_rc --disk-format qcow2 --container-format bare --is-public False --property type=baseimages --min-disk 2 --file ${IMAGE}.new
sudo rm ${IMAGE}.new
