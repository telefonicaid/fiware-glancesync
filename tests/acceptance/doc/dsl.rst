=============================================
FIWARE | GLANCESYNC | Acceptance test project
=============================================

This page describes the DSL implemented for building features. All available steps can be used as part of following
test elements:

- Given
- When
- Then
- And
- But

Although all steps can be used as part of any group above, in next sections we have grouped them by the typical test
element you are going to use with them.

Given clauses
-------------

::
    >> the GlanceSync command line interface is installed

    >> a new image created in the Glance of master node with name "(?P<image_name>\w*)" and these properties
    >> a new image created in the Glance of master node with name "(?P<image_name>\w*)"
    >> other new image created in the Glance of master node with name "(?P<image_name>\w*)" and these properties
    >> other new image created in the Glance of master node with name "(?P<image_name>\w*)"
    >> other new image created in the Glance of master node with name "(?P<image_name>\w*)" and file "(?P<file>\w*)"
    >> other new image created in the Glance of master node with name "(?P<image_name>\w*)", file "(?P<file>\w*)"
       and these properties
    >> a new image created in the Glance of all target nodes with name "(?P<image_name>\w*)"
    >> a new image created in the Glance of all target nodes with name "(?P<image_name>\w*)" and file "(?P<file>\w*)"
    >> a new image created in the Glance of all target nodes with name "(?P<image_name>\w*)"
       and without upload an image file
    >> a new image created in the Glance of all target node with name "(?P<image_name>\w*) file "(?P<file_name>\w*)"
       and using a credential type "(?P<cred_type>\w*)"

    >> the following images created in the Glance of master node with name


    >> GlanceSync configured to sync images using these configuration parameters
    >> GlanceSync configured to sync images without specifying any condition


    >> already synchronized images
    >> already synchronized images on "(?P<nodes>[\w,: ]*)"


When clauses
------------

::

    >> I sync images
    >> I sync the image
    >> I sync images on "(?P<nodes>[\w,: ]*)"
    >> I sync the image on "(?P<nodes>[\w,: ]*)"
    >> I run the sync command with options "(?P<cli_options>[\w,\'=\-\.\s]*)"

Then clauses
------------

::

    >> the image "(?P<image_name>\w*)" is synchronized
    >> all images are synchronized
    >> all images are synchronized in "(?P<region>\w*)"
    >> the image "(?P<image_name>\w*)" is synchronized in target region "(?P<region>\w*)"
    >> the image "(?P<image_name>\w*)" is not synchronized again
    >> the image "(?P<image_name>\w*)" is not synchronized
    >> all images are replaced
    >> the image "(?P<image_name>\w*)" is replaced
    >> the image "(?P<image_name>\w*)" is not replaced
    >> all images are renamed and replaced
    >> the image "(?P<image_name>\w*)" is renamed and replaced
    >> the image "(?P<image_name>\w*)" is neither renamed nor replaced
    >> no images are synchronized


    >> the AMI image "(?P<image_name>[\w\.]*)" is present in all target nodes with the following properties
    >> a warning message is shown informing that the (?P<type>kernel|ramdisk) image "(?P<type_image_name>\w*)" has not
       been found for the AMI image "(?P<image_name>\w*)"


    >> the properties values of the image "(?P<image_name>\w*)" in all nodes are the following
    >> the properties values of the image "(?P<image_name>[\w\.]*)" in all target nodes are the following
    >> the properties values of the image "(?P<image_name>\w*)" are only the following


    >> the user properties of the image "(?P<image_name>\w*)" are updated in the Glance of master node
    >> metadata of the image "(?P<image_name>\w*)" are updated
    >> metadata of all images are updated
    >> the timestamp of image "(?P<image_name>[\w]*)" in "(?P<region1>[\w]*)" is greater than the image
       in "(?P<region2>[\w]*)"


    >> the image "(?P<image_name>\w*)" is present in all nodes with the expected data
    >> the image "(?P<image_name>\w*)" is only present in target node "(?P<region_name>\w*)"
    >> all synchronized images are present in all nodes with the expected data
    >> the image "(?P<image_name>\w*)" is present in all nodes with the content of file "(?P<file_name>\w*)"
    >> the image "(?P<image_name>[\w\.]*)" is present in all target nodes with the content of file "(?P<file_name>\w*)"
    >> the image "(?P<image_name>[\w\.]*)" is not present in target nodes
    >> the image "(?P<image_name>\w*)" is deleted from the Glance of master node
    >> a new image created in the Glance of any target node with name "(?P<image_name>\w*)", file "(?P<file_name>\w*)"
       and using a credential type "(?P<cred_type>\w*)"


    >> a warning message is shown informing about images with the same name "(?P<image_name>\w*)"
    >> a warning message is shown informing about checksum conflict with "(?P<image_name>\w*)"
    >> a warning message is shown informing about image duplicity for "(?P<image_name>\w*)"
    >> a warning message is shown informing about not active status in the image "(?P<image_name>\w*)"
    >> a warning message is shown informing about different owner for image "(?P<image_name>\w*)"


    >> I can see.*
    >> configured regions are listed
    >> the image "(?P<image_name>\w*)" is pending for synchronization
    >> all images are pending for synchronization
    >> the image "(?P<image_name>\w*)" has the status "(?P<status>\w*)" in all target regions
    >> the image "(?P<image_name>\w*)" has the status "(?P<status>\w*)" on "(?P<region_name>[\w,: ]*)"


    (parallel execution: --parallel)
    >> files are created with output logs
    >> parallel process is executed for all nodes
    >> the image "(?P<image_name>\w*)" is synchronized in a parallel way
    >> all images are synchronized in a parallel execution
    >> no images are synchronized in a parallel execution
    >> a warning message is logged informing about checksum conflict with "(?P<image_name>\w*)" in a parallel execution
    >> the image "(?P<image_name>\w*)" is replaced in a parallel execution
    >> the image "(?P<image_name>\w*)" is renamed and replaced in a parallel execution
