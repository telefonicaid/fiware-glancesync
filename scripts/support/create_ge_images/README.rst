*******************************************
Scripts to create, test & publish GE images
*******************************************

This is the software used to implement the functionality described at
https://forge.fiware.org/plugins/mediawiki/wiki/testbed/index.php/FIWARE_LAB_Image_Deployement_Guideline.

That is, this software creates, tests and publishes an image, using the pair of
scripts, a creation script and a testing script, provided by each GE owner.


Installation
************

The software must be used from a Ubuntu 14.04 system with the following packages installed:

* qemu-kvm
* python-novaclient
* python-glanceclient
* python-keystoneclient
* python-neutronclient
* libguestfs-tools

The scripts should be copied to */opt/create_ge_images* to share the installation
between several users. Also the module *osclients.py*, provided in the parent
folder, must be copied.

Each user must create the folder *~/create_ge_images* and load the environment
variables (``OS_USERNAME``, ``OS_PASSWORD``, ``OS_TENANT_NAME``, ``OS_AUTH_URI``) with its
FIWARE Lab credential. The script *sec_group* is useful to initialize the
user account: it creates a pair of security groups (one of them to create
the image and the other one to test it), generates and registers a key pair and allocates a
floating IP if it is not already allocated.

Creating/testing the image
**************************

To create an image called *myimage*, the user must create the folder
*~create_ge_images/myimage* and put inside the scripts *create.sh* and
*test.sh*. Optionally, the file *data.tgz* can also be added.

It is strongly recommended that both *create.sh* and *test.sh* scripts start with
``#!/bin/bash -ex``. This way, the script stops when something is wrong and
a trace is displayed for each command invoked. Anyway, the exit status of the
script must be zero only when the script runs without error.

After this, one of the scripts *create_template_\*.sh*, must be invoked passing
as parameter the name of the image. For example, to create the image
*myimage* using the *debian* image, the command to invoke is:

.. code::

  /opt/create_ge_images/create_template_debian.sh myimage

Inside the folder myimage, a pair of logs will be generated: *create.log* is the
result of invoking the *create.sh* script and *test.log* is the output of
the *test.sh* launch. Of course, if the execution of the creation script fails,
then only *create.log* is generated.

If all the processes end without errors, the UUID of the new image is printed.
This image is private and owned by the user, but it is ready to be published
now.

By default, the *m1.small* flavor is used. To choose another flavor, the
FLAVOR environment variable may be used. The flavor to be used is specified by the
GE owners. They should choose the minimal flavor their images work with.

How the script works
--------------------

At first, the script launch a VM using the chosen base image, with the generated
keypair and the security group *sshopen*. The name of the virtual machine is
the same than the image. Then it assigns the floating IP and wait until a SSH
connection is ready.

At this moment, the create.sh script is uploaded to the VM (the data.tgz
is upload if it exists, too). Then the script is invoked via SSH.

If the script did not fail, the support account and the script are deleted and
the VM is power down. Then a snapshot is made, downloaded and deleted. Also
the VM is deleted.

The local copy of the snapshot is *virt-syspred*. Then the shrink process and
*virt-sparsify* are invoked. Finally, the resulting image is upload as
*<imagename>_rc* (*rc* means *release candidate*)

The last phase is to check the image. A VM is instantiated from that image, using again the
generated keypair and assigning the floating IP. This time, however, the security
group *allopen* is used and the name of the VM is the same than the image but
with the *test-* prefix. A ssh-agent is started to insert the generated public key.
Then the testing script is invoked. If it complete without errors, the VM is deleted,
the ssh-agent is killed and the UUID of the image is printed. The image is
ready for publication.

Be aware that if the creation script fails, the virtual machine will not be deleted;
this is useful to debug the problem, but anyway that virtual machine should be
deleted before trying again. In the same way, if the testing script fails,
neither the virtual machine nor the release candidate image are deleted.

**Warning: the testing script is executed directly, it is not invoked inside the
VM machine but in the user account. Therefore, this script is a security risk
and must be audited before running it. It is important also not use the root
account to invoke the process. The script cleans the sudo credential before
invoking the script. As an experimental feature, it is possible to run the
script inside a VM. This is described in next section.**

Running the testing script in a VM
----------------------------------

If ``TEST_USING_VM`` is defined and not empty, the testing script is executed
inside a VM. This is an experimental feature that does not require an extra
floating IP. It is more secure, but it needs more time to complete. If the
script fails, maybe a good idea is to check that this experimental feature is
not the cause of the problem. To repeat the test only, the variable ``TEST_ONLY``
must be defined and not empty (and of course to use the traditional method,
``TEST_USING_VM`` must be undefined).

It works by creating a second VM (the tester). Initially the floating IP is assigned to
this VM and a SSH connection is created, using SSH ControlMaster; this maintains
a persistent connection that is reused by the subsequent ssh commands. Then the
IP is assigned to the tested VM; this change does not affect to the already
created connections. This way is possible to connect to the tester VM via ssh,
in spite of the floating IP is assigned now to the tested VM.

Publishing the image
********************

Every GE image have two properties: the NID and the type. The values are
registered at https://wikis.hi.inet/fi-ware/index.php/Cloud:GE_Identification

The following three situations are possible:

* the image is completely new. Then a new NID must be allocated and registered in
  the wiki. The type must be the same that the other images in the same chapter.
* there is an older version of the image and both will coexist, using for example
  a suffix with the version number. The NID and type must be provided to the
  script manually but they must be the same values than the other image.
* the image replaces an older version, using the same name. The old image
  will be overwritten. The NID and type of the old image will be used
  automatically.

The script ``locate_images.py`` can be helpful. It shows a list of the images with
its name, nid and type. It is also useful to see what NIDs are in use.

To publish the image, the script ``publish_image.py`` can be used. The following
order is used to publish the image *myimage*, that replaces an image already
existing with the same name:

.. code::

  /opt/create_ge_images/publish_image.py myimage

The command renames the old image (using the suffix .old) and makes it private.
It also prints the old image checksum. This value must be append to the replace
directive at ``/etc/glancesync.conf``, this way the old image will be replaced
with the new one in the other regions.


If the image does not replace an existing one, then the NID and type must be
provided:

.. code::

  /opt/create_ge_images/publish_image.py myimage <nid> <type>

Both *publish_image.py* as *locate_images.py* requires virtualevn with the same
environment than the described in scripts/support/README.md

