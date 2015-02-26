Introduction
-------------

What is Glancesync
__________________

Glancesync is a command line tool to solve the problem of the images synchronisation between regions. It synchronises glance servers in different regions taking the base of a master region. It was designed for FIWARE project, but it has been expanded to be useful for other users or projects.

Features
________

Glancesync synchronises all the images with certain metadata owned by a tenant from a master region to each other region in a federation (or a subset of them). This feature works out of the box without configuration. It requires only the same set of environment variables, which are needed to contact the keystone server, than the glance tool. It's also possible to set these parameters in a file instead of using environment variables.

Next version of Glancesync will support also the synchronisation to regions which do not use the same keystone server than the master region and therefore require their own set of credentials. 

Glancesync by default does not overwrite the content of existing images. If a image checksum is different between the region to synchronise and the master region, a warning is emitted. The user has the option of forcing the overwriting of a specific image (optionally renaming the old one) including the checksums in a configuration file, using a whilelist or a blacklist.

Glancesync has special support for AMI (Amazon Machine Image). Amazon images include a reference to a kernel image (AKI) and to a ramdisk image (ARI), but they are named by UUID. Therefore Glancesync has to update this fields to reflect the UUIDs in that particular region. 

This tool does not synchronise using UUID but names (i.e. a image has the same name in all regions, but not the same UUID). Using a UUID to synchronise is generally a bad idea, because some problems may arise with the restriction that a UUID must be unique. For example, a user in a region might upload a image with this UUID before the synchronisation, or a previous upload may end with an error but with the UUID created. If something similar to an UUID is required, is better to use a metadata field to simulate it.

Installation
------------

At the moment, Glancesync is designed to run in the glance server of the master region, because it reads the images content directly from disk. This will be fixed in a feature version.

It's not necessary to install the software, after unzipping the package or running 'git clone' the tool is ready to work.

Glancesync works mainly as a front-end to the glance and keystone python tool, therefore they must be installed (note that in Essex OpenStack release, python-glanceclient was named as glance-client):

.. code::

   $ apt-get install python-glanceclient python-keystoneclient

How to use
----------

Basic use
_________
First, you need the credentials to authenticate with the keystone server. You can put this credentials in a configuration file or set the following standard OpenStack environment variables: ``OS_USERNAME``, ``OS_PASSWORD``, ``OS_AUTH_URL``, ``OS_TENANT_NAME``, ``OS_REGION_NAME``. The value of ``OS_REGION_NAME`` will be the master region (in FIWARE Lab this region is Spain). 


If you prefer a configuration file, edit the file ``/etc/glancesync.conf`` (a different path may be used, if variable ``GLANCESYNC_CONF`` is defined).  In section [main] the parameter 'master region' must be set with the region from which the images are synchronised. In section [master] the parameter 'credential' must include the following in this order: user, password, keystone_url, tenant. A difference in the configuration file, is that password must be encoded with base64. 


After this, if you simply need to synchronise all the regions with the master region, run ``glancesync/sync.py``. 

The tool first obtains the list of regions, contacts with the master region to obtain its list of images, each one with its metadata, expands this metadata with the checksum of each image and finally prints the set of images to synchronise. Then it iterates through the list of regions. For each region, glancesync obtains the list of images with their metadata and checksums and compare with the results of master region. If an image is present in both regions but with different metadata fields ``nid``, ``type`` or ``sdc_aware``, it updates the image in the region with the values of the images in the master region. After this, it uploads sequentially (ordered by size in ascending order) the missing images to the region. If an operation with a region fails, for example the upload of an image, Glancesync passes to next region, due to if there is a problem uploading an image, there will be also problems uploading another one bigger. 


It is possible that an image is present both in the region and in the master region, but with different content (i.e. the checksums are different). The default behaviour of Glancesync is only to print a warning (safety is a big concern with a synchronisation tool: it never should touch content without user knowledge). The user can specify a list of images that it is right to overwrite by setting a list of checksums (the old content ones) using parameter '``replace``' in the section ``[master``] of the configuration file. Another option is the parameter '``rename``'; in this case the old image is not deleted but renamed (and its properties nid and type are renamed also). Both parameters can include the 'any' keyword. In this case the parameter '``dontupdate``' works as a blacklist. The algorithm is:
 1.  Is the checksum in dontupdate? print a warning only
 2.  Is the checksum in rename? rename old image and upload the master region's image
 3. Is the checksum in replace? replace the old image with the master region's image
 4. Does the parameter 'replace' include the keyword 'any'? rename old image and upload the  master region's image
 5. Does the parameter 'rename' include the keyword 'any'? replace the old image with the master region's image
 6. Otherwise: print a warning only

What images are synchronised?
_____________________________
The images to be synchronised from master region are selected by its metadata. Each selected image must has got a nid value and/or a type value. This choice is not arbitrary, all FIWARE images have at least one of these properties. A feature version of Glancesync will allow and arbitrary selection criteria.

The images also must be public and owned by the tenant.

It is possible to add manually, to the synchronisation set, additional images that:
 * do not include the required metadata
 * they are not public or are not owned by the tenant (but not both, because then they are not accessible)


Additional images are included appending their UUIDs to forcesyncs parameter at [master] section.

The regions list. Multitarget support
_____________________________________

By default Glancesync synchronised the images from the master region to all the others regions whose glance server is registered in the same keystone server than the master region. However, another option is to pass the exact list of regions as parameters.


Additionally, Glancesync iterates sequentially with the regional glance servers in the same order they are get from the keystone server. If the user prefers a different order, they can modify the parameter ``preferable_order`` of section ``[main]``. The value of this parameter does not need to include all the regions available, nor all of them has to exist at this moment. The algorithm works iterating through the list: if the region exists, it is append to the new ordered list and removed from the original list. At the end, the remaining regions are append to the new ordered list. 

A new feature is to synchronise regions registered at different keystone servers. A group of regions sharing a keystone server (and therefore the same credentials) is a 'target'. The 'master' target is mandatory and is the master region's group. Each target has a section in the configuration file and may have its own parameters (every parameter described in this document about the ``master`` region may be inside any other target section), but the only mandatory is ``credential``. Any parameter filled in the special section ``[DEFAULT]`` acts as a default value for each other section. To overwrite a default value, simple use '=' with a value (e.g ``dontupdate=``)

A region is full specified as target:region, but 'master:' may be omitted.

Parallel sync
_____________

The ``parallelsync.py`` tool is an alternative version of sync.sh, which allows the synchronisation of several regions simultaneously. The maximum number of regions that can be synchronised simultaneously is set with paramenter ``max_children`` in section ``[main]``.

When using parallesync.py, the information about each region is not displayed using standard output but saved on a file per region inside a directory with the system time. This is to avoid mixing and interleaving the data from different regions.

Other tools
-----------
Glancesync software distribution includes some extra tools:

 * getregions.py  Obtains the full list of the regions of the specified target. If not parameter is specified, 'master' region is assumed.
 * reportsyncpending.py This is a "dry-run" version of sync tool. That is, shows what regions and images are pending of synchronisation.
 * printimages.py This tool shows for each region its list of images with a prefix indicating some remarkable information. This tool is conceived as a tool to detect anomalies and images that are in some region and not in the master region. These are the special prefixes:

  * +: this image is not on the master glance server
  * $: this image is not active: may be still uploading or in an error
           status.
  * -: this image is on the master glance server, but as non-public
  * !: this image is on the master glance server, but checksum is different
  * #: this image is on the master glance server, but some of these
           attributes are different: nid, type, sdc_aware, Public (if it is
           true on master and is false in the region

 * backup.py do a full backup of the images metadata (not content!!!) located at the specified regions (all regions in the master target if not specified). Of course, only the images which are owned by the tenant or publicly available are consider. This backup correspond with the execution of command 
 * deleteimage_byname.py  Search the image in the region by name and delete it. May also remove the image in all the regions
 * renameimage.py  Rename the image in the specified regions
 * updatemetadata.py  This is an example script to update the metadata (public, nid, type properties) of a set of regions. Image list with their properties are embedded in the source code.
 
Appendix: Example of configuration file
---------------------------------------

.. code::

 [main]
 
 # Region where are the images in the "master" target that are synchronized to
 # the other regions of "master" regions and/or to regions in other targets.
 master_region = Spain
 
 # A sorted list of regions. Regions that are not present are silently
 # ignored. Synchronization is done also to the other regions, but first this
 # list is recurred and then the
 #
 # Regions are prefixed with target:, but this is not required when
 # target is master.
 preferable_order = Trento, Lannion, Waterford, Berlin, Prague

 # The maximum number of simultaneous children to use to do the synchronisation.
 # Each region is synchronised using a children process, therefore, this
 # parameter sets how many regions can be synchronised simultaneously.
 # The default value, max_children = 1, implies that synchronisation is fully
 # sequential.
 max_children = 1
 
 [DEFAULT]
 
 # Values in this section are default values for the other sections.
 # To undefine "parameter1" put "parameter1="
 
 # the files with this checksum will be updated replacing the old image
 # parameter may be any or a CSV list (or a CSV list with 'any' at the end)
 # replace = 9046fd22131a96502cb0d85b4a406a5a
 
 # the files with this checksum will be renamed and its nid and type attributes
 # also renamed to nid.bak and type.bak
 # parameter may be any or a CSV list (or a CSV list with 'any' at the end)
 # rename = any
 
 # If replace or rename is any, don't update nor rename images with some of
 # these checksums
 # dontupdate =
 
 # List of UUIDs that must be synchronized unconditionally. Otherwise, these two
 # conditions are checked:
 # -The image is public
 # -The image has nid and/or type
 #
 # This is useful for example to pre-sync images marked as private
 
 # webtundra, synchronization
 forcesyncs = d93462dc-e7c7-4716-ab64-3cbc109b201f,3471db65-a449-41d5-9090-b8889ee404cb

 # condition to evaluate if the image is synchronised.
 # image is defined, as well as target.
 metadata_condition = image['Public'] == 'Yes' and ('_nid' in image or '_type' in image) and image['Owner'].zfill(32) == target['tenant'].zfill(32) 

 [master]
 credential = fakeuser,W91c2x5X2RpZF95b3VfdGhpbmtfdGhpc193YXNfdGhlX3JlYWxfcGFzc3dvcmQ/,http://fakeserver:4730/v2.0,faketenantid1
 
 [experimental]
 credential = fakeuser2,W91c2x5X2RpZF95b3VfdGhpbmtfdGhpc193YXNfdGhlX3JlYWxfcGFzc3dvcmQ/,http://fakeserver2:4730/v2.0,faketenantid2

