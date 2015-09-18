GlanceSync - Glance Synchronization Component
*********************************************

.. contents:: :local:

Introduction
============

This is the code repository for the GlanceSync component, the FIWARE Ops tool
used to sincronize the glance images in the different Glance servers connected
in the FIWARE Lab.

This project is part of [FIWARE](http://www.fiware.org).

Although this component has been developed for FIWARE, the software is highly
configurable, do not have special requirements beyond OpenStack libraries and
may be used with any other project or as a generic tool to synchronise images.
Moreover, all the OpenStack interface is in a module and it is possible to
adapt the code to support other platforms.

Any feedback on this documentation is highly welcome, including bugs, typos
or things you think should be included but are not. You can use 
[github issues](https://github.com/telefonicaid/fiware-glancesync/issues/new)
to provide feedback.

Overall description
===================

Glancesync is a command line tool to solve the problem of the images
synchronisation between regions. It synchronises glance servers in different
regions taking the base of a master region. It was designed for FIWARE project,
but it has been expanded to be useful for other users or projects.

Sofware features
----------------

Glancesync synchronises all the images with certain metadata owned by a tenant
from a master region to each other region in a federation (or a subset of them).
This feature works out of the box without configuration. It requires only the
same set of environment variables, which are needed to contact the
keystone server, than the glance tool. It's also possible to set these
parameters in a file instead of using environment variables.

Glancesync synchronisation algorithm (i.e. the method to determine if a master
image must be synchronised to the other regions) is configurable. By default
all public images are synchronised, but it is enough with adding a line in the
configuration file to synchronise only the public images with certain metadata.

Glancesync supports also the synchronisation to regions which do not use the
same keystone server than the master region and therefore require their own set
of credentials. The regions are grouped by *targets*: two regions are in the
same *target* if their glance servers are registered in the same keystone
server. The only mandatory *target* is the ``master`` target, where the master
region is. Most of the Glancesync configuration, including the criteria to select
which images are synchronised, is defined at target level.

Glancesync by default does not replace existing images. If an
image checksum is different between the region to synchronise and the master
region, a warning is emitted. The user has the option of forcing the
overwriting of a specific image (optionally renaming the old one) including the
checksums in a configuration file, using a whilelist or a blacklist.

When the remote image has the same content than the master image, but the
metadata differs, Glancesync updates the metadata, but only a limited set, to
avoid overwriting properties considered as local in that glance server. Also
the system property ``is_public`` is updated.

Glancesync has special support for *AMI* (Amazon Machine Image). Amazon images
include a reference to a kernel image (*AKI*) and to a ramdisk image (*ARI*),
but they are named by UUID. Therefore Glancesync has to update this fields to
reflect the UUIDs in that particular region. 

About UUIDs and image names
---------------------------

This tool does not synchronise using UUID but names (i.e. a image has the same
name in all regions, but not the same UUID). Using a UUID to synchronise is
generally a bad idea, because some problems may arise with the restriction that
a UUID must be unique. Be aware that it is not possible to replace
the content of a image, without creating a new one and the old UUID may not be
reused.  If something similar to an UUID is required, it is better to use a
metadata field to simulate it.

The downside of using names, is that a region may have more than a image
with the same name. This is specially challenging, when there is more than a
image in a destination target, with the name of the image to synchronise. In
this situation, Glancesync takes the first it found and print a warning with
the others.

Of course, duplicating the image names is easy to avoid, with one serious
exception: when ordinary users can publish their images as public (shared), the
risk of collision increases and escapes of the control of the user. To avoid
this, Glancesync allows setting a parameter to ignore images of other tenants.
Anyway, this is a general problem, not only a synchronisation
problem, because more than image with the same name is very confusing to the
users of the images. Therefore it is better to restrict the publication of
shared images.

How it works
------------

First glancesync gets a list of the images in the master region. Then runs the
algorithm with each specified region (or all the regions registered in the
same keystone server than the master region, if not specified). If an error
occurs within a region synchronisation, glancesync does not run more operations
in that region and jumps to the next one.

For each region, Glancesync starts getting a list of its images. Then
calculates with images should be synchronised to this region (this is detailed
in the next section).

It some images has metadata pending, it updates them. After updating the metadata, 
the missing images are upload. The uploading is by size order, this way when
there is a problem in the glance server it will be detected earlier with the
smallest image (e.g. when there is not enough space). Another reason to start
with the smallest first, is because AMI images; the kernel and ramdisk are also
images and because they are smaller, are uploaded before the AMI image that
needs them.

The last step is to update the kernel/ramdisk fields in AMI
images when the kernel/ramdisk has been uploaded during this synchronisation
session.

When a image with the same name is already present in the destination region,
glancesycn check it they are the same comparing the checksums. When they are
different, the following algorithm is applied:

1) Is the checksum in the ``dontupdate`` list? print a warning only
2) Is the checksum in the ``rename`` list? rename old image (adding the *.old*
   suffix), change it to private, and upload the master region's image
3) Is the checksum in the replace list? replace the old image with the master
   region's image
4) Does the parameter ``replace`` include the keyword *any*? rename old image and
   upload the  master region's image
5) Does the parameter ``rename`` include the keyword *any*? replace the old image
   with the master region's image
6) Otherwise: print a warning. The user should take an action and fill
   ``dontupdate``, ``replace`` or ``rename`` parameters. In the meanwhile, the
   image is considered *stalled* and it is not synchronised at all.

How the images to synchronise are selected
------------------------------------------

There are three parameters in the configuration that affects which images are
selected: forcesync, metadata_condition, metadata_set. All of them can be
different for each target; when all targets use the same selection criteria,
an option is to put this options in the DEFAULT section.

This is the algorithm to determine if an image is synchronisable:

1) if the UUID of the image is included in ``forcesync``, then it is synchronised
   unconditionally, even if the image is not public.
2) if ``metadata_condition`` is defined, it contains python code that is evaluated
   to determine if the image is synchronised. The code can use two variables:
   image, with the information about the image and ``metadata_set``, with the content
   of that parameter. The more interesting field of image is ``user_properties``,
   that is a dictionary with the metadata of the image. Other properties are *id*,
   *name*, *owner*, *size*, *region*, *is_public*. The image may be synchronised
   even if it is not public, to avoid this, check ``image.is_public`` in the condition.
3) if ``metadata_condition`` is not defined, the image is public, and
   ``metadata_set`` is defined, the image is synchronized if some of the
   properties of ``metadata_set`` is on ``image.user_properties``.
4) if ``metadata_condition`` is not defined, the image is public, and
   ``metadata_set`` is not defined, the image is synchronized
5) otherwise, the image is not synchronised.

For example, to synchronise the images in FIWARE-LAB, the best choice is
setting ``metadata_set=nid, type, nid_version``, because all the images to be
synchronised has at least one of those properties.

The parameter ``metadata_set`` has another function. It is used to determine how
the metadata is updated in the remote image. If it is not defined, all the metadata
is copied from the master image, otherwise, only the properties in ``metadata_set``
are copied. Be aware that system property *is_public* must not be included in
``metadata_set``, because it is not a user property but a system one. Therefore,
*is_public* is unconditionally synchronised.

Build and Install
=================

Requirements
------------

At the moment, Glancesync is designed to run in the glance server of the master
region, because it reads the images that are stored directly in the filesystem.
This will be fixed in a future version.

The following software must be installed (e.g. using apt-get on Debian and Ubuntu,
or with yum in CentOS):

- Python 2.7
- pip
- virtualenv


Installation
------------

The recommend installation method is using a virtualenv. Actually, the installation
process is only about the python dependencies, because the scripts do not need
installation.

1) Create a virtualenv 'glanceysncENV' invoking *virtualenv glancesyncENV*
2) Activate the virtualenv with *source glancsyncENV/bin/activate*
3) Install the requirements running *pip install -r requirements.txt
   --allow-all-external*

Now the system is ready to use. For future sessions, only the step2 is required.


Running
=======

Security consideration
----------------------

Glancesyncs does not require root access. But at this version it requires
read-only access to image directory ``/var/lib/glance/images`` (or a copy of
all these files in other path and then set the option *images_path*)

It is strongly recommended:

* creating an account to run glancesync only
* creating a configuration file only readable by the glancesync account. This
is because the credentials should not be exposed to other users.

Basic use
---------

Once installed all the dependencies, there is a way to run GlanceSync manually
from the command line invoking the ``sync.py`` tool inside the GlanceSync
distribution.

The tool can work without a configuration tool. In this case, the following
OpenStack environment variables must be filled with the administrator's
credential: ``OS_USERNAME``, ``OS_PASSWORD``, ``OS_AUTH_URL``,
``OS_TENANT_NAME``, ``OS_REGION_NAME``. The value of ``OS_REGION_NAME`` will be
the master region (in FIWARE Lab this region is Spain2).

When ``./sync.py`` is invoked without parameters, it synchronises the images from
the master region to all the other regions with a glance endpoint registered in
the keystone server (except the ones, if any, specified as a comma separated list
in the ``ignore_regions`` parameter, inside the ``master`` section). The command
can also receive as parameters the regions to synchronise.

Advanced use
------------

By default, GlanceSync synchronises regions one by one. When the command line
option *--parallel* is passed, GlanceSync synchronised several regions in
parallel. The number or regions synchronised at the same time is determined by the
parameter max_children in the main section. Default value is 1 (no parallel).
When Glancesyncs runs in parallel, a directory with

The option *--dry-run* shows the changes needed to synchronise the images,
but without doing the operations actually.

Finally, the option *--show-status* is to obtain a report about the
synchronisation status of the regions. A more detailed information of this is
provided in the *Checking status* section.

As pointed, GlanceSync can synchronised also from the master region to regions
that do not use the same keystone server. A *target* is a namespace to refer to
the regions that shared a keystone server. The ``master`` target is the one
where the master region is. Each target has a section with its name in the
configuration file, to specify the credential and optionally other configuration
(most of the parameters are local to each target)

The way to synchronise to regions that are in other *target*, is to specified
the region with the preffix ``<target_name>:``. For example, to synchronise to region
Trento and Berlin2, both in the same keystone server than the master region,
but also to RegionOne and RegionTwo, registered in target *other* the
following command must be invoked:

.. code::

   ./sync.py Trento Berlin2 other:RegionOne other:RegionTwo
   
Note that the *master:* prefix may be omitted.

Configuration file
------------------

The configuration used by the GlanceSync component is stored in the
``/etc/glancesync.conf`` file.

The following is an example of a configuration file, with all the possible
options autoexplained in the comments.

.. code::

 [main]

 # Region where are the images in the "master" target that are synchronized to
 # the other regions of "master" regions and/or to regions in other targets.
 master_region = Spain
 
 # A sorted list of regions. Regions that are not present are silently
 # ignored. Synchronization is done also to the other regions, but first this
 # list is revised and then the Regions are prefixed with "target:"
 # This parameter is only used when running synchronisation without parameters.
 # When the region list is provided explicitly via command line, the order of
 # the parameters is used instead.
 preferable_order = Trento, Lannion, Waterford, Berlin, Prague

 # The maximum number of simultaneous children to use to do the synchronisation.
 # Each region is synchronised using a children process, therefore, this
 # parameter sets how many regions can be synchronised simultaneously.
 # The default value, max_children = 1, implies that synchronisation is fully
 # sequential. Be aware that you need also to invoke the sync tool with the
 # --parallel parameter.
 #
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

 # List of UUIDs that must be synchronized unconditionally.
 #
 # This is useful for example to pre-sync images marked as private

 forcesyncs = 6e240dd4-e304-4599-b7d8-e38e13cef058

 # condition to evaluate if the image is synchronised.
 # image is defined, as well as metadata_set (see next parameter).
 # Default condition is:
 #  image.is_public and (not metadata_set or metadata_set.intersection(image.user_properties))
 metadata_condition = image.is_public and\
  ('nid' in image.user_properties or 'type' in image.user_properties)

 # the list of userproperties to synchronise. If this variable is undefined, all
 # user variables are synchronised.
 metadata_set = nid , type, sdc_aware, nid_version

 # if true, ignore public images of other tenants. That is, a image is upload
 # even when a image with the same name and content exist in the regional
 # server, if this image is not owned by the tenant specified in the credential.
 only_tenant_images = True

 [master]
 credential = user,W91c2x5X2RpZF95b3VfdGhpbmtfdGhpc193YXNfdGhlX3JlYWxfcGFzc3dvcmQ/,http://server:4730/v2.0,tenantid1
 ignore_regions = Spain

 [experimental]
 credential = user2,W91c2x5X2RpZF95b3VfdGhpbmtfdGhpc193YXNfdGhlX3JlYWxfcGFzc3dvcmQ/,http://server2:4730/v2.0,tenantid2

This example has 4 configuration sections:

* main: here they are a few global options: the master_region (the only
  mandatory one, unless OS_REGION_NAME is defined), preferable_order, that is used
  only to determine the order of regions in master target when ./sync.py is
  invoked without parameters and max_children. Be aware that for running the
  synchronisation in parallel, both max_children must be greater than one and
  --parallel option must be passed to sync.py.
* DEFAULT: this section is used to avoid repeating the parameters with each
  target. Putting a line in this section is equivalent to adding it at the
  beginning of each other section. As the name indicates, it is only a default
  value and can be overwritten inside a section.
* master: this is the target when the master region is. The only parameter
  that may be considered specific of this target is
* experimental: this is another target


Checking status
---------------

In order to check the status of the synchronisation, use the following command:

.. code::

   ./sync.py --show-status

This print the status of all the regions in the *master* target, that is, the
region in the same keystone server than the master region. If ``ignore_regions``
is defined in the *master* configuration section, the specified regions are
ignored.

Of course is also possible to check the status of any group of regions, for
example, the call:

.. code::

   ./sync.py --show-status Trento Mexico Gent target2:Region1 target2:Region2

It will show the status of the regions Trento, Mexico, Gent both in the *master*
target, and the regions Region1 in Region2 defined in the *target2* target.

The output of command is a line for each image to be synchronised for each
region. That is, in the last example, if 15 images are syncrhonised to the
regions of *master* and 10 images to the regions of *target2*, then a total
of 15*3 + 10*2 images are printed.

Each line is a CSV. The firt field is the synchronisation status, the
seconds is the region's name, and the third is the image name. This is an
example:

.. code::

 ok,Prague,base_centos_6
 ok,Prague,base_ubuntu_14.04
 ok,Prague,base_ubuntu_12.04
 ok,Prague,base_debian_7
 pending_upload,Prague,base_centos_7

The synchronisation status can be classified in three categories: final status,
error status and pending synchronisation status.

Final status
____________

GlanceSync consider that there is no pending operations: the image is
synchronised of marked as 'dontupdate'.

* ok: the image is fully synchronised
* ok_stalled_checksum: the image has a different checksum than master,
  but this checksum is included in parameter 'dontupdate'. Therefore the image
  will not be updated (content nor metadata)

Error status
____________

There is an error condition that requires user intervention before trying
again.

* error_checksum: there is an image, but with a different checksum and
  there is not a matching dontupdate, rename or replace directive. Action
  required: fill the checksum (or use any) with dontupdate or rename or replace.
* error_ami: the image requires a kernel or ramdisk that is not in the
  list of images to sync. Action required: ensure that the selection criteria
  include the kernel/ramdisk images.

Pending synchronisation status
______________________________

The image needs synchronisation. Be aware that perhaps the image is on one of
this status although GlanceSync execution has completed, because the glance
server responds with an error. However, this is not considered an error status,
because it is not a problem that users must resolve by themselves.

* pending_metadata: there is an image with the right content (checksum), but
  metadata must be updated (this may include ramdisk_id and kernel_id)
* pending_upload: the image is not synchronised; it must be upload
* pending_replace: there is an image, but with different checksum. The
  image will be replaced
* pending_rename: there is an image, but with different checksum. The
  image will be replaced, but before this the old image will be renamed
* penging_ami: the image requires a kernel or ramding that is in state
  pending_upload, pending_replace or pending_rename.


Testing
=======

Ent-to-end tests
----------------

To run the end-to-end tests, go to ``test/acceptance`` folder and run:

.. code::

    behave features/ --tags ~@skip

Please, be aware that this tests requires preparing a environment, including
at least three glance servers and two keystone servers. Have a look to the
``test/acceptance/README.rst`` in order to get more information about how to
prepare the environment to run the functional_test target.

Unit tests
----------

To run the unit tests, go to ``test/unit`` folder and run:

.. code::

     export PYTHONPATH=../..
     python -m unittest discover

Eight tests are marked as skipped because they are more properly integration
test. They are in the file ´´test_glancesync_serversfacade.py´´. The tested
module contains all the code that interacts with Glance and the tests do some
checks agains a real glance server. To activate this eight tests, edit the file and
change testingFacadeReal to True. It needs the usual OpenStack environment
variables (*OS_USERNAME*, *OS_PASSWORD*, *OS_TENANT_NAME*, *OS_REGION_NAME*,
*OS_AUTH_URL*)

Advanced topics
===============

* Installation and administration

 * [Building from sources](doc/manuals/admin/build_source.md)
 * [Running GlanceSync from command line](doc/manuals/admin/cli.md)
 * [Logs](doc/manuals/admin/logs.md)
 * [Resources & I/O Flows](doc/manuals/admin/resources.md)

* [Problem diagnosis procedures](doc/manuals/admin/diagnosis.md)
* Container-based deployment

 * [Vagrant](doc/manuals/vagrant.md)
 * [Sample code contributions](doc/manuals/code_contributions.md)

License
=======

GlanceSync is licensed under Apache v2.0 license.
