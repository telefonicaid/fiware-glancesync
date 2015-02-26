Introduction
============

For an introduction about Glancesync, please refer to the user manual. This guide assumes that the reader is already familiarised with that document; therefore it does not explain any concepts already described on it.

Glancesync tools are written in Python. Each tool is a script with a few lines of code: most of the work is done by GlanceSync class. This class is an interface that programmers can use to extend or customise the tools behaviour.

The following fragment is a basic example:::

 from glancesync import GlanceSync

 glancesync = GlanceSync()
 regions = glancesync.get_regions()
 for region in regions:
     try:
         print '==Region: ' + region
         glancesync.sync_region(region)
         print 'Done.'
     except Exception:
         # Do nothing, message already logged


A typical case is to get a list of regions first and the operate over each region. Most of the operations work with a specific region.

A region is namespaced with a 'target' (e.g. ``development:Spain``). The default target is 'master' and therefore the suffix 'master:' is optional.

The call glancesync.get_regions() returns a list of the regions in the master target. To obtain the regions in other targets, invoke glancesync.get_regions(target).


Methods of GlanceSync
=====================

With all methods, param 'region' pattern is '::target:region_name::' (e.g. development:Spain). The suffix 'master:' may be omitted.

constructor
___________

::

 def __init__(self, glancesyncconfig=None)

The constructor of GlanceSync may be invoked without parameters. It read then the configuration file from ``/etc/glancesync.conf`` or from the path specified in ``GLANCESYNC_CONFIG`` environment variable.  It is also possible to pass to the constructor a GlanceSyncConfig parameter with the configuration.

get_regions
___________

::

 def get_regions(self, omit_master_region=True, target='master')

It returns the list of regions. Unless *omit_master_region* is *False*, the master region is excluded from the list. The parameter *target* determines the keystone server where the glance regional servers are registered.

sync_region
___________

::

 def sync_region(self, region) 

It synchronises the glance server of the specified region with the contents of the master region.

show_sync_region_status
_______________________

::

 def show_sync_region_status(self, region) 

This is a dry-run version of the *sync* method. Don't synchronise, only show the images to be synchronised.

print_images_master_region
__________________________

::

 def print_images_master_region(self) 

Print the set of images in master region to be synchronized to the others regions

backup_glancemetadata_region
____________________________

::

 def backup_glancemetadata_region(self, region, path=None)

Save on a file a backup of the metadata of the regional glance server. Only the tenant's images and public images are preserved. The backup file is created in the current directory, unless a different location is provided in *path* parameter.

print_images
____________

::

 def print_images(self, region)

Print a report about the images present on the specified region

This method is NOT intended to check the synchronization status (for this is better *show_sync_region_status*) but to detect anomalies as images present in some regions that are not in master region.

The images may be prefixed with a symbol indicating something special:

* +: this image is not on the master glance server
* $: this image is not active: may be still uploading or in an error status.
* -: this image is on the master glance server, but as non-public
* !: this image is on the master glance server, but checksum is different
* #: this image is on the master glance server, but some of these attributes are different: *nid*, *type*, *sdc_aware*, *Public* (if it is true on master and is false in the region)

get_images_region
_________________

::

 def get_images_region(self, region)

Return a list with the tenant's images and the public images. Each image is a dictionary with the metadata.

delete_image
____________

::

 def delete_image(self, region, uuid, confirm=True)

Delete a image from the specified region. Be careful, this action cannot be reverted and for this reason by default it requires confirmation!

update_metadata_image
_____________________

::

 def update_metadata_image(self, region, image):

Update the image metadata on the specified region. Some metadata keys are special: the name, the owner... The id metadatum cannot be changed.

