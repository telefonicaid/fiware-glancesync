# -*- coding: utf-8 -*-

Feature: GlanceSync CLI implementation: Show sync status of each image for each region

  As a sys-admin user,
  I want to see the synchronization status of the images for each regions
  so that I can know what images are successfully synchronized or not.


  Scenario: Show image sync status when images are not synchronized (pending_upload)
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    When  I run the sync command with options "--show-status"
    Then  the image "qatesting01" has the status "pending_upload" in all target regions


  Scenario: Show image sync status when images are synchronized (ok)
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    When  I run the sync command with options "--show-status"
    Then  the image "qatesting01" has the status "ok" in all target regions

  @env_dependant @experimentation
  Scenario: Show image sync status when images are synchronized (ok, pending_upload)
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images on "Burgos"
    When  I run the sync command with options "--show-status"
    Then  the image "qatesting01" has the status "ok" on "Burgos"
    And   the image "qatesting01" has the status "pending_upload" on "Caceres"


  Scenario: Show image sync status when images are synchronized but they have different checksum (error_checksum)
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    When  I run the sync command with options "--show-status"
    Then  the image "qatesting01" has the status "error_checksum" in all target regions


  Scenario Outline: Show image sync status when 'conflicts' are detected (pending_replace, pending_rename, ok_stalled_checksum)
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  |                       |
            | DEFAULT         | metadata_set        | 'nid, sdc_aware'      |
            | DEFAULT         | <config_key>        | checksum(qatesting01) |
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01", file "qatesting01b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    When  I run the sync command with options "--show-status"
    Then  the image "qatesting01" has the status "<status>" in all target regions

    Examples:
          | config_key | status               |
          | replace    | pending_replace      |
          | rename     | pending_rename       |
          | dontupdate | ok_stalled_checksum  |


  Scenario: Show image sync status when metadata are modified (pending_metadata)
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  |                       |
            | DEFAULT         | metadata_set        | 'nid, sdc_aware'      |
    And   already synchronized images
    And   the user properties of the image "qatesting01" are updated in the Glance of master node:
            | param_name      | param_value         |
            | nid             | 55555               |
            | sdc_aware       | False               |
    When  I run the sync command with options "--show-status"
    Then  the image "qatesting01" has the status "pending_metadata" in all target regions


  Scenario: Show image sync status when kernel or ramdiskid are pending to be uploaded (pending_ami)
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting01"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting03" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02"
    And   the user properties of the image "qatestingami01" are updated in the Glance of master node:
            | param_name      | param_value                     |
            | ramdisk_id      | id(qatestingramdisk01)          |
    When  I run the sync command with options "--show-status"
    Then  the image "qatestingkernel01" has the status "ok" in all target regions
    And   the image "qatestingramdisk01" has the status "pending_upload" in all target regions
    And   the image "qatestingami01" has the status "pending_ami" in all target regions


  Scenario: Show image sync status when kernel or ramdiskid are not in the list of images to sync (error_ami)
    Given a new image created in the Glance of master node with name "qatestingami01", file "qatesting03" and these properties:
            | param_name      | param_value                     |
            | type            | testing                         |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key                      | config_value          |
            | DEFAULT         | metadata_condition              | ''                    |
            | DEFAULT         | metadata_set                    | 'type'                |
    And   already synchronized images
    And   a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting01"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02"
    And   the user properties of the image "qatestingami01" are updated in the Glance of master node:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    When  I run the sync command with options "--show-status"
    And   the image "qatestingami01" has the status "error_ami" in all target regions
