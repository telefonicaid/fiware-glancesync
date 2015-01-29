#!/usr/bin/env python
# coding=utf-8
"""Module to synchronize several regions glance server with a master region.

Prerequisites:

"""

import sys
import os
import datetime
import urllib
import time

import glance.client

from subprocess import Popen, PIPE

from keystoneclient.v2_0.client import Client as KeystoneClient

class GlanceSync(object):
    _forcesyncs = ()

    def __init__(self, master_region='Spain', white_checksums_file=None):
        self._master_region = master_region
        self.regions_uris = _get_regions_uris(self.get_regions(False))
        self.master_region_dict = _get_master_region_dict(
            master_region, self.regions_uris[master_region])
        if white_checksums_file is not None:
            self.whitechecksum_dict = _get_whitechecksum_dict(
                white_checksums_file)
        else:
            self.whitechecksum_dict = None

    def get_regions(self, omit_master_region=True):
        """returns a list of regions

        Keyword arguments:
        omit_master_region -- if true the master region is not included
        """

        p = Popen(['/usr/bin/keystone', 'catalog', '--service=image'],
                  stdin=None, stdout=PIPE)
        output_cmd = p.stdout
        regions_list = list()
        for line in output_cmd:
            if line.startswith('| region'):
                name = line.split('|')[2].strip()
                if omit_master_region and name == self._master_region:
                    continue
                regions_list.append(name)
        p.wait()
        return regions_list

    def sync_region(self, region):
        _sync_region(
            self.master_region_dict, region, self.regions_uris[region], False,
            self.whitechecksum_dict, self._forcesyncs)

    def show_sync_region_status(self, region):
        _sync_region(
            self.master_region_dict, region, self.regions_uris[region], True,
            self.whitechecksum_dict, self._forcesyncs)

    def print_images_master_region(self):
        _printimages(self.master_region_dict.values())

    def print_images(self, region):
        images_region = self.get_images_region(region)
        _printimages(images_region, self.master_region_dict)

    def update_metadata_image(self, region, image):
        _update_metadata_remote(region, image)

    def delete_image(self, region, uuid, confirm=True):
        os.environ['OS_REGION_NAME'] = region
        if confirm:
            p = Popen(['/usr/bin/glance', 'delete', uuid], stdin=None,
                      stdout=None)
        else:
            p = Popen(['/usr/bin/glance', 'delete', uuid, '-f'], stdin=None,
                      stdout=None)
        p.wait()

    def backup_glancemetadata(self):
        date = datetime.datetime.now().isoformat()
        for region in self.get_regions(False):
            os.environ['OS_REGION_NAME'] = region
            fich = open('backup_glance_' + date + '_' + region + '.txt', 'w')
            try:
                print 'Backup of region ' + region
                p = Popen(['/usr/bin/glance', 'details', '--limit=100000'],
                          stdin=None, stdout=fich)
                code = p.wait()
                fich.close()
                if code != 0:
                    print 'Failed backup of ' + region
            except Exception:
                print 'Failed backup of ' + region

    def get_images_region(self, region):
        return _getimagelist(region, self.regions_uris[region])

    def set_forcesync(self, forcesync):
        self._forcesync = forcesync

_force_sync = ('de0223a5-90d4-43cd-aa5b-cd3c6c1790c7',
               'd93462dc-e7c7-4716-ab64-3cbc109b201f',
               '933d26bf-2285-4c0e-9c5b-b38165a1acd7',
               '3471db65-a449-41d5-9090-b8889ee404cb',
               '0a2119f1-3c6a-49b0-ae22-5e4c12b1c2eb')


def _update_metadata_remote(region, image):
    # We update only _nid, _type, _kernel_id, _ramdisk_id
    # get as a list all the properties (all of them start with _)
    props = list(x[1:] + '=' + image[x] for x in image if x.startswith('_'))
    # compose cmd line
    arguments = [
        'glance', 'update', image['Id'], 'disk_format=' + image[
            'Disk format'], 'name=' + image['Name'], 'is_public=' + image[
            'Public'], 'protected=' + image['Protected'], 'container_format=' +
        image['Container format']]
    arguments.extend(props)
    # set the region
    os.environ['OS_REGION_NAME'] = region
    # update
    p = Popen(arguments, stdin=None, stdout=None, stderr=None)
    p.wait()
    if p.returncode != 0:
        raise Exception('update of ' + image['Name'] + 'failed')


def _upload_image_remote(region, image, replace_uuid=None, rename_uuid=None):
    """Upload the image to the specified region.

    Usually, this call is invoked by sync_region()
    Be careful! if image has properties kernel_id / ramdisk_id, must be
    updated with the ids of this region
    """
    # set region
    os.environ['OS_REGION_NAME'] = region
    # if replace_uuid, first upload with other name and without nid
    # nor type
    if replace_uuid or rename_uuid:
        saved_type = image.get('_type', None)
        if saved_type:
            del(image['_type'])
        saved_nid = image.get('_nid', None)
        if saved_nid:
            del(image['_nid'])
        saved_name = image['Name']
        image['Name'] += '_tmp'
        image['Public'] = 'No'
    # get as a list all the properties (all of them start with _)
    props = list(x[1:] + '=' + image[x] for x in image if x.startswith('_'))
    # compose cmdline
    arguments = ['glance', 'add', '--silent-upload', 'disk_format=' + image[
        'Disk format'], 'name=' + image['Name'], 'is_public=' +
        image['Public'], 'protected=' + image['Protected'], 'container_format='
        + image['Container format']]
    arguments.extend(props)
    # run command
    fich = open('/var/lib/glance/images/' + image['Id'], 'r')
    p = Popen(arguments, stdin=fich, stdout=PIPE, stderr=None)
    fich.close()
    outputcmd = p.stdout
    result = outputcmd.read()
    p.wait()
    if p.returncode != 0:
        print 'Upload of ' + image['Name'] + " to region " + region +\
            ' Failed.'
        print result
        sys.exit(-1)
    newuuid = result.split(':')[1].strip()
    if rename_uuid or replace_uuid:
        newimage = dict(image)
        newimage['Id'] = newuuid
        if saved_nid:
            newimage['_nid'] = saved_nid
        if saved_type:
            newimage['_type'] = saved_type
        newimage['Name'] = saved_name
        newimage['Public'] = 'Yes'
        _update_metadata_remote(region, newimage)
        if replace_uuid:
            delete_image(region, replace_uuid, confirm=False)
        elif rename_uuid:
            # locate old image
            l = _getimagelist(region)
            oldimage = None
            for i in l:
                if i['Id'] == rename_uuid:
                    oldimage = i
                    if saved_nid:
                        oldimage['_nid.bak'] = saved_nid
                        del(oldimage['_nid'])
                    oldimage['Name'] = saved_name + '.old'
                    _update_metadata_remote(region, oldimage)


def _getimagelist(region, region_uri):
    """returns a list of images from the glance of the specified region

     Each imagen is a dictionary indexed by name. Extra properties are
     coded as _<name> the other labels are the returned by glance details.
     List is completed with checksum.
    """
    os.environ['OS_REGION_NAME'] = region
    images = list()
    image = None
    p = Popen(['/usr/bin/glance', 'details', '--limit=100000'],
              stdin=None, stdout=PIPE)
    outputcmd = p.stdout
    # Read first a line; detect if there is an error
    line = outputcmd.readline()
    if line[0] != '=':
        print line,
        for line in outputcmd:
            print line,
        raise Exception("Error retrieving image list")
    checksums = _get_checksums(region, region_uri)
    image = dict()
    for line in outputcmd:
        if line[0] == '=':
            if image is not None and image['Name'] is not 'None':
                image['checksum'] = checksums[image['Name']]
                images.append(image)
            image = dict()
        else:
            (key, value) = line.split(':', 1)
            if key.startswith('Property \''):
                key = '_' + key[10:-1]
                if key == '_nic':
                    continue
            image[key] = value.strip()
    return images


def _convert2csv(image, fields, allmandatory=False):
    """Extract the fields of the image as a CSV

    Only the fields especified in fields list are listed
    If allmandatory, returns None if some of the
    fields are missing.
    """
    sub = list()
    for field in fields:
        if field in image:
            sub.append(image[field])
        else:
            if allmandatory:
                return None
            sub.append('')
    return ','.join(sub)


def _prefix(image, comparewith):
    name = image['Name']
    if name not in comparewith:
        return '+'
    if image['Status'] != 'active':
        return '$'
    image_master_region = comparewith[name]
    if image_master_region['checksum'] != image['checksum']:
        return '!'
    if image_master_region.get('Public', None) != image.get('Public', None):
        if image_master_region.get('Public', None) == 'No':
            return '-'
        else:
            return '#'
    if image_master_region.get('_nid', None) != image.get('_nid', None):
        return '#'
    if image_master_region.get('_type', None) != image.get('_type', None):
        return '#'
    if image_master_region.get('_sdc_aware', None) != image.get(
            '_sdc_aware', None):
        return '#'
    return ''


def _printimages(imagesregion, comparewith=None):
    images = list(image for image in imagesregion if image['Public'] == 'Yes'
                  and ('_nid' in image and '_type' in image))
    images.sort(key=lambda image: image['_type'] + image['Name'])
    for image in images:
        line = _convert2csv(image, ('Name', '_type', '_nid'))
        if line is not None:
            if comparewith is not None:
                print _prefix(image, comparewith) + line
            else:
                print line
    print "---"
    images = list(image for image in imagesregion if image['Public'] == 'Yes'
                  and ('_nid' not in image and '_type' in image))
    images.sort(key=lambda image: image['_type'] + image['Name'])
    for image in images:
        line = _convert2csv(image, ('Name', '_type', '_nid'))
        if line is not None:
            if comparewith is not None:
                print _prefix(image, comparewith) + line
            else:
                print line
    print "---"
    images = list(image for image in imagesregion if image['Public'] == 'Yes'
                  and ('_nid' in image and '_type' not in image))
    images.sort(key=lambda image: int(image['_nid']))
    for image in images:
        line = _convert2csv(image, ('Name', '_type', '_nid'))
        if line is not None:
            if comparewith is not None:
                print _prefix(image, comparewith) + line
            else:
                print line


def _sync_region(
        master_region_dictimages, region, region_uri, onlyshow=False,
        whitechecksums=None, forcesync=()):
    imagesregion = _getimagelist(region, region_uri)
    # sets to images with different checksums
    images2replace = set()
    images2rename = set()
    # These two dictionaries are used for _kernel_id and _ramdisk_id update
    dictimages = dict((image['Name'], image) for image in imagesregion)
    dictimagesbyid = dict((image['Id'], image) for image in imagesregion)
    regionimageset = set()
    noactive = list()
    for image in imagesregion:
        p = _prefix(image, master_region_dictimages)
        image_name = image['Name']
        ids_need_update = False
        # Check kernel_id and ramdisk_id if present
        if '_kernel_id' in image and image_name in master_region_dictimages:
            kernel_id = image['_kernel_id']
            ramdisk_id = image['_ramdisk_id']
            kernel_name = None
            ramdisk_name = None
            if kernel_id in dictimagesbyid:
                kernel_name = dictimagesbyid[kernel_id]['Name']
            if ramdisk_id in dictimagesbyid:
                ramdisk_name = dictimagesbyid[ramdisk_id]['Name']
            if kernel_name is None:
                kernel_name_sp = master_region_dictimages[image_name][
                    '_kernel_id']
                if kernel_name_sp not in dictimages:
                    print 'Warning: image ' + kernel_name_sp +\
                          ' missing: is the kernel of ' + image_name
                else:
                    image['_kernel_id'] = dictimages[kernel_name_sp]['Id']
                    ids_need_update = True
            if ramdisk_name is None:
                ramdisk_name_sp = master_region_dictimages[
                    image_name]['_ramdisk_id']
                if ramdisk_name_sp not in dictimages:
                    print 'Warning: image ' + ramdisk_name_sp +\
                        ' missing: is the ramdisk of ' + image_name
                else:
                    image['_ramdisk_id'] = dictimages[ramdisk_name_sp]['Id']
                    ids_need_update = True
        if p == '#' or ids_need_update:
            image_spain = master_region_dictimages[image_name]
            if '_type' in image_spain:
                image['_type'] = image_spain['_type']
            if '_nid' in image_spain:
                image['_nid'] = image_spain['_nid']
            if '_sdc_aware' in image_spain:
                image['_sdc_aware'] = image_spain['_sdc_aware']
            image['Public'] = image_spain['Public']
            if not onlyshow:
                _update_metadata_remote(region, image)
            else:
                print 'Image penging to update the metadata ' + image_name
        if p == '$':
            print 'Warning! state of image ' + image_name + ' is not active: '\
                  + image['Status']
        if p == '!':
            if image_name is None:
                image_name = 'None'
            c = image['checksum']
            if not isinstance(c, unicode):
                c = 'None'
            image_spain = master_region_dictimages[image_name]
            if image_spain.get('_sdc_aware', None) != image.get('_sdc_aware',
                                                                None):
                print 'Warning! image ' + image_name + \
                    ' has different checksum: ' + c + \
                    ' and different value of sdc_aware '
            else:
                print 'Warning! image ' + image_name +\
                    ' has different checksum: ' + c
        if image_name in regionimageset:
            print 'WARNING!!!!!: the image name ' + image_name +\
                ' is duplicated '
        regionimageset.add(image_name)
    # upload images of master region to the region if they are not already
    # present.
    # only is both this two conditions are met:
    # * image is public
    # * image has the property type and/or the property nid
    # as an exception, also sync images in forcesync tuple
    totalmbs = 0
    # There are two reason to upload first the smaller images:
    #   *kernel and ramdisk must be updload before AMI images to insert the
    #    UUID
    #   *if there is a problem (e.g. server is full) the error appears before.
    imgs = master_region_dictimages.values()
    imgs.sort(key=lambda image: int(image['Size']))
    for image in imgs:
        image_name = image['Name']
        uuid2replace = None
        uuid2rename = ''
        if image['Public'] == 'No' and not image['Id'] in forcesync:
            continue
        if image_name in dictimages:
            if not whitechecksums:
                continue
            checksum = dictimages[image_name]['checksum']
            if image['checksum'] == checksum:
                continue
            if checksum in whitechecksums['dontupdate']:
                continue
            if checksum in whitechecksums['replace']:
                uuid2replace = dictimages[image_name]['Id']
            elif checksum in whitechecksums['rename'] or 'any' in\
                    whitechecksums['rename']:
                uuid2rename = dictimages[image_name]['Id']
            elif 'any' in whitechecksums['replace']:
                uuid2replace = dictimages[image_name]['Id']
            else:
                continue
        if '_type' not in image and '_nid' not in image and image[
                'Id'] not in forcesync:
            continue
        sizeimage = int(image['Size']) / 1024 / 1024
        totalmbs = totalmbs + sizeimage
        if not onlyshow:
            print 'Uploading image ' + image_name + ' (' +\
                str(sizeimage) + ' MB)'
            sys.stdout.flush()
            # Check kernel_id and ramdisk_id if present
            if '_kernel_id' in image:
                kernel_id = image['_kernel_id']
                ramdisk_id = image['_ramdisk_id']
                kernel_name = master_region_dictimages[image_name][
                    '_kernel_id']
                ramdisk = master_region_dictimages[image_name]['_ramdisk_id']
                if kernel_name not in dictimages:
                    print 'Warning: image ' + kernel_name +\
                        ' missing: is the kernel of ' + image_name
                else:
                    image['_kernel_id'] = dictimages[kernel_name]['Id']
                if ramdisk not in dictimages:
                    print 'Warning: image ' + ramdisk +\
                        ' missing: is the ramdisk of ' + image_name
                else:
                    image['_ramdisk_id'] = dictimages[ramdisk]['Id']
            _upload_image_remote(region, image, uuid2replace, uuid2rename)
            print 'Done.'
            sys.stdout.flush()
        else:
            print 'Pending: ' + image_name + ' (' + str(sizeimage) + ' MB)'
    if totalmbs == 0:
        print 'Region is synchronized.'
    else:
        if onlyshow:
            print 'MBs pending : ' + str(totalmbs)
        else:
            print 'Total uploaded to region ' + region + ': ' + str(totalmbs)\
                + ' (MB) '
    sys.stdout.flush()
    return totalmbs


def _get_regions_uris(region_list):
    regionsuris = dict()
    kc = KeystoneClient(
        username=os.environ['OS_USERNAME'], password=os.environ['OS_PASSWORD'],
        tenant_name=os.environ['OS_TENANT_NAME'],
        auth_url=os.environ['OS_AUTH_URL'])
    for region in region_list:
        regionsuris[region] = kc.service_catalog.url_for(
            'region', region, 'image')
    return regionsuris


def _get_checksums(region, region_uri):
    host = urllib.splithost(urllib.splittype(region_uri)[1])[0]
    (host, port) = urllib.splitport(host)
    images = glance.client.get_client(
        host=host, port=port, region=region).get_images(limit=5000)
    checksum_region = dict()
    for image in images:
        checksum_region[image['name']] = image['checksum']
    return checksum_region


def _get_master_region_dict(master_region, master_region_uri):
    images = _getimagelist(master_region, master_region_uri)
    master_region_dictimagesbyid = dict((image['Id'], image) for image in
                                        images)
    master_region_dictimages = dict()
    for image in images:
        if '_kernel_id' in image:
            image['_kernel_id'] = master_region_dictimagesbyid[image[
                '_kernel_id']]['Name']
        if '_ramdisk_id' in image:
            image['_ramdisk_id'] = master_region_dictimagesbyid[image[
                '_ramdisk_id']]['Name']
        master_region_dictimages[image['Name']] = image
    return master_region_dictimages


def _get_whitechecksum_dict(filename):
    checksumdict = {'replace': set(), 'rename': set(), 'dontupdate': set()}
    for line in open(filename):
        line = line.strip()
        if len(line) == 0 or line[0] == '#':
            continue
        parts = line.split('=')
        if len(parts) != 2:
            print >>sys.stderr, 'Error parsing file', filename
            sys.exit(-1)
        key = parts[0].rstrip()
        values = set(parts[1].split(','))
        if key in ['replace', 'rename', 'dontupdate']:
            checksumdict[key] = values
        else:
            print >>sys.stderr, 'Error parsing file', filename, 'key ', key,\
                ' not recognized'
    return checksumdict
