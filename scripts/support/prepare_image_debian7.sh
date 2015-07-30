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

IMAGE=debian7
USER=debian
set -e
unsecuressh="ssh -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no"
unsecurescp="scp -oUserKnownHostsFile=/dev/null -oStrictHostKeyChecking=no"

sudo true
VMID=$(./launch_image.py $IMAGE newdebian7 m1.tiny)
sleep 180
$unsecurescp support_pubkeys/defaultgpg.pub suppport_pubkeys/defaultssh.pub resources/rc.local activate_support_account.py $USER@10.95.55.170:
$unsecuressh $USER@10.95.55.170 -t -t sudo apt-get update
$unsecuressh $USER@10.95.55.170 -t -t sudo apt-get -y upgrade
$unsecuressh $USER@10.95.55.170 -t -t sudo apt-get -y install openjdk-6-jre-headless wget
$unsecuressh $USER@10.95.55.170 -t -t sudo apt-get -y install unattended-upgrades
cat <<EOF | $unsecuressh $USER@10.95.55.170 -t -t
#sudo apt-get update
#sudo apt-get -y upgrade
#sudo apt-get -y install openjdk-6-jre-headless wget
#sudo apt-get -y install unattended-upgrades
sudo mv activate_support_account.py /sbin
sudo mv rc.local /etc/
sudo chmod 755 /etc/rc.local
sudo install -d /etc/fiware-support/
sudo mv defaultgpg.pub defaultssh.pub /etc/fiware-support/
sudo rm -f /var/cache/apt/archives/*.deb
exit
EOF
nova delete $VMID
nova image-create ${VMID} ${IMAGE}snapshot --poll
nova delete $VMID
 
IMAGE_ID=$(glance image-list | awk -F\| /${IMAGE}'snapshot/ {gsub(/^[ ]+/,"", $2) ; print $2}')
sudo virt-sysprep -a /var/lib/glance/images/$IMAGE_ID
#sudo virt-sparsify  /var/lib/glance/images/$IMAGE_ID ${IMAGE}.new
sudo qemu-img convert -O qcow2 /var/lib/glance/images/$IMAGE_ID ${IMAGE}.new
glance image-delete ${IMAGE}snapshot

glance image-create --name ${IMAGE}_rc --disk-format qcow2 --container-format bare --is-public False --property type=baseimages --min-disk 1 --file ${IMAGE}.new
sudo rm ${IMAGE}.new
