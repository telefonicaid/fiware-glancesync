#!/bin/bash

# CentOS 6 http://cloud.centos.org/centos/6/images/
# Last used was: 20141129_01 (1 Dec 2014)
wget http://cloud.centos.org/centos/6/images/CentOS-6-x86_64-GenericCloud.qcow2

# CentOS 7 http://cloud.centos.org/centos/7/images/
# Last used was: 1503 (31 Mar)
wget http://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2
glance image-create --name centos7.orig --disk-format qcow2 --container-format bare --is-public True --property type=baseimages --file CentOS-7-x86_64-GenericCloud.qcow2

# Ubuntu 14.04 images: http://cloud-images.ubuntu.com/trusty/current/
# Last version: 
# Ubuntu 14.04.2 LTS (Trusty Tahr) Daily Build [20150708]
wget http://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img

glance image-create --name ubuntu14.04_cloud_x64 --disk-format qcow2 --container-format bare --is-public True --property type=baseimages --file trusty-server-cloudimg-amd64-disk1.img


# Ubuntu 12.04 images: http://cloud-images.ubuntu.com/precise/
# Last version: 
# Ubuntu 12.04.5 LTS (Precise Pangolin) Daily Build [20150709]
wget http://cloud-images.ubuntu.com/precise/current/precise-server-cloudimg-amd64-disk1.img

glance image-create --name ubuntu12.04_cloud_x64 --disk-format qcow2 --container-format bare --is-public True --property type=baseimages --file precise-server-cloudimg-amd64-disk1.img
# Debian 7 image was locally builded on my laptop, using build-openstack-debian-imag 
# (package openstack-debian-images)

