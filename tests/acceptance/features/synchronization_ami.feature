# -*- coding: utf-8 -*-

Feature: Image (AMI) sync between regions using GlanceSync in the same federation.
  As a sys-admin of FIWARE federation
  I want to sync images AMI from master node to other nodes in the federation
  So that I can use the same base images in all nodes and keep them updated


  @happy_path @skip @bug @CLAUDIA-5327
  Scenario: Simple AMI image synchronization between regions. The last uploaded image is the AMI image (biggest size)
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting01"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting03" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  all images are synchronized
    And   the image "qatestingkernel01" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatestingramdisk01" is present in all target nodes with the content of file "qatesting02"
    And   the image "qatestingami01" is present in all target nodes with the content of file "qatesting03"
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |


  @skip @bug @CLAUDIA-5324
  Scenario: Simple AMI image synchronization between regions. The AMI image is the first uploaded image (lesser size)
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting01" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  all images are synchronized
    And   a warning message is shown informing that the kernel image "qatestingkernel01" has not been found for the AMI image "qatestingami01"
    And   a warning message is shown informing that the ramdisk image "qatestingramdisk01" has not been found for the AMI image "qatestingami01"
    And   the image "qatestingkernel01" is present in all target nodes with the content of file "qatesting03"
    And   the image "qatestingramdisk01" is present in all target nodes with the content of file "qatesting02"
    And   the image "qatestingami01" is present in all target nodes with the content of file "qatesting01"

  @skip @bug @CLAUDIA-5327
  Scenario: Simple AMI image synchronization between regions. The kernel image is the last uploaded image. The AMI image is the second one.
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting01"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting02" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  all images are synchronized
    And   a warning message is shown informing that the kernel image "qatestingkernel01" has not been found for the AMI image "qatestingami01"
    And   the image "qatestingkernel01" is present in all target nodes with the content of file "qatesting03"
    And   the image "qatestingramdisk01" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatestingami01" is present in all target nodes with the content of file "qatesting02"
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | ramdisk_id      | id(qatestingramdisk01)          |


  @skip @bug @CLAUDIA-5327
  Scenario: Simple AMI image synchronization between regions. The ramdisk image is the last uploaded image. The AMI image is the second one.
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting01"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting03"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting02" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  all images are synchronized
    And   a warning message is shown informing that the ramdisk image "qatestingramdisk01" has not been found for the AMI image "qatestingami01"
    And   the image "qatestingkernel01" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatestingramdisk01" is present in all target nodes with the content of file "qatesting03"
    And   the image "qatestingami01" is present in all target nodes with the content of file "qatesting02"
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |


  @skip @bug @CLAUDIA-5327
  Scenario: Simple AMI image synchronization between regions with custom metadata. The last uploaded image is the AMI image (biggest size)
    Given a new image created in the Glance of master node with name "qatestingkernel01", file "qatesting01" and these properties:
            | param_name      | param_value                     |
            | custom_k1       | valuekernel1                    |
            | custom2         | valuekernel2                    |
            | custom3         | valuekernel3                    |
    And   a new image created in the Glance of master node with name "qatestingramdisk01", file "qatesting02" and these properties:
            | param_name      | param_value                     |
            | custom_r1       | valueramdisk1                   |
            | custom2         | valueramdisk2                   |
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting03" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
            | custom_a1       | valueami1                       |
            | custom2         | valueami2                       |
            | custom3         | valueami3                       |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key                      | config_value                               |
            | DEFAULT         | metadata_condition              |                                            |
            | DEFAULT         | metadata_set                    | 'custom_k1, custom_r1, custom_a1, custom2' |
    When  I sync images
    Then  all images are synchronized
    And   the image "qatestingkernel01" is present in all nodes with the content of file "qatesting01"
    And   the image "qatestingramdisk01" is present in all nodes with the content of file "qatesting02"
    And   the image "qatestingami01" is present in all target nodes with the content of file "qatesting03"
    And   the properties values of the image "qatestingkernel01" in all target nodes are the following:
            | param_name      | param_value                     |
            | custom_k1       | valuekernel1                    |
            | custom2         | valuekernel2                    |
    And   the properties values of the image "qatestingramdisk01" in all target nodes are the following:
            | param_name      | param_value                     |
            | custom_r1       | valueramdisk1                   |
            | custom2         | valueramdisk2                   |
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
            | custom_a1       | valueami1                       |
            | custom2         | valueami2                       |


  @happy_path
  Scenario Outline: AMI image synchronization between regions. The AMI image is correctly synchronized in the second execution (different file size).
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "<kernel_image_file>"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "<ramdisk_image_file>"
    And   a new image created in the Glance of master node with name "qatestingami01", file "<ami_image_file>" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    When  I sync images
    Then  metadata of the image "qatestingami01" are updated
    And   the image "qatestingkernel01" is present in all target nodes with the content of file "<kernel_image_file>"
    And   the image "qatestingramdisk01" is present in all target nodes with the content of file "<ramdisk_image_file>"
    And   the image "qatestingami01" is present in all target nodes with the content of file "<ami_image_file>"
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |

    Examples:
            | ami_image_file | ramdisk_image_file | kernel_image_file |
            | qatesting01    | qatesting02        | qatesting03       |
            | qatesting01    | qatesting03        | qatesting02       |
            | qatesting02    | qatesting01        | qatesting03       |


  Scenario: AMI image synchronization between regions with custom metadata. The AMI image is correctly synchronized in the second execution (different file size).
    Given a new image created in the Glance of master node with name "qatestingkernel01", file "qatesting03" and these properties:
            | param_name      | param_value                     |
            | custom_k1       | valuekernel1                    |
            | custom2         | valuekernel2                    |
    And   a new image created in the Glance of master node with name "qatestingramdisk01", file "qatesting02" and these properties:
            | param_name      | param_value                     |
            | custom_r1       | valueramdisk1                   |
            | custom2         | valueramdisk2                   |
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting01" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
            | custom_a1       | valueami1                       |
            | custom2         | valueami2                       |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key                      | config_value                               |
            | DEFAULT         | metadata_condition              |                                            |
            | DEFAULT         | metadata_set                    | 'custom_k1, custom_r1, custom_a1, custom2' |
    And   already synchronized images
    When  I sync images
    Then  metadata of the image "qatestingami01" are updated
    And   the image "qatestingkernel01" is present in all nodes with the content of file "qatesting03"
    And   the image "qatestingramdisk01" is present in all nodes with the content of file "qatesting02"
    And   the image "qatestingami01" is present in all nodes with the content of file "qatesting01"
    And   the properties values of the image "qatestingkernel01" in all nodes are the following:
            | param_name      | param_value                     |
            | custom_k1       | valuekernel1                    |
            | custom2         | valuekernel2                    |
    And   the properties values of the image "qatestingramdisk01" in all nodes are the following:
            | param_name      | param_value                     |
            | custom_r1       | valueramdisk1                   |
            | custom2         | valueramdisk2                   |
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
            | custom_a1       | valueami1                       |
            | custom2         | valueami2                       |

  @skip @bug @CLAUDIA-5327
  Scenario: AMI image synchronization between regions when conflicts. All checksum are different. No actions configured (replace/rename)
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting01" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatestingami01" is deleted from the Glance of master node
    And   the image "qatestingramdisk01" is deleted from the Glance of master node
    And   the image "qatestingkernel01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03b"
    And   other new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02b"
    And   other new image created in the Glance of master node with name "qatestingami01", file "qatesting01b" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    When  I sync images
    Then  no images are synchronized


  @happy_path @skip @bug @CLAUDIA-5327
  Scenario: AMI image synchronization between regions when conflicts. All checksum are different. Replace.
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting01" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key                      | config_value                                                                          |
            | DEFAULT         | replace                         | 'checksum(qatestingami01), checksum(qatestingramdisk01), checksum(qatestingkernel01)' |
    And   already synchronized images
    And   the image "qatestingami01" is deleted from the Glance of master node
    And   the image "qatestingramdisk01" is deleted from the Glance of master node
    And   the image "qatestingkernel01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03b"
    And   other new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02b"
    And   other new image created in the Glance of master node with name "qatestingami01", file "qatesting01b" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    When  I sync images
    Then  all images are replaced
    And   the image "qatestingkernel01" is present in all target nodes with the content of file "qatesting03b"
    And   the image "qatestingramdisk01" is present in all target nodes with the content of file "qatesting02b"
    And   the image "qatestingami01" is present in all target nodes with the content of file "qatesting01b"
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |


  @skip @bug @CLAUDIA-5327
  Scenario: AMI image synchronization between regions when conflicts. Only the kernel image has been modified (the checksum is different). Replace.
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting01" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key                      | config_value          |
            | DEFAULT         | replace                         | any                   |
    And   already synchronized images
    And   the image "qatestingkernel01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03b"
    And   the user properties of the image "qatestingami01" are updated in the Glance of master node:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
    When  I sync images
    Then  the image "qatestingkernel01" is replaced
    And   the image "qatestingami01" is not replaced
    And   the image "qatestingramdisk01" is not replaced
    And   the image "qatestingkernel01" is present in all target nodes with the content of file "qatesting03b"
    And   the image "qatestingramdisk01" is present in all target nodes with the content of file "qatesting02"
    And   the image "qatestingami01" is present in all target nodes with the content of file "qatesting01"
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |


  @happy_path @skip @bug @CLAUDIA-5327
  Scenario: AMI image synchronization between regions when conflicts. All checksum are different. Rename.
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting01" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key                      | config_value                                                                          |
            | DEFAULT         | rename                          | 'checksum(qatestingami01), checksum(qatestingramdisk01), checksum(qatestingkernel01)' |
    And   already synchronized images
    And   the image "qatestingami01" is deleted from the Glance of master node
    And   the image "qatestingramdisk01" is deleted from the Glance of master node
    And   the image "qatestingkernel01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03b"
    And   other new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02b"
    And   other new image created in the Glance of master node with name "qatestingami01", file "qatesting01b" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    When  I sync images
    Then  all images are renamed and replaced
    And   the image "qatestingkernel01" is present in all target nodes with the content of file "qatesting03b"
    And   the image "qatestingramdisk01" is present in all target nodes with the content of file "qatesting02b"
    And   the image "qatestingami01" is present in all target nodes with the content of file "qatesting01b"
    And   the image "qatestingkernel01.old" is present in all target nodes with the content of file "qatesting03"
    And   the image "qatestingramdisk01.old" is present in all target nodes with the content of file "qatesting02"
    And   the image "qatestingami01.old" is present in all target nodes with the content of file "qatesting01"
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   the AMI image "qatestingami01.old" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01.old)       |
            | ramdisk_id      | id(qatestingramdisk01.old)      |


  @skip @bug @CLAUDIA-5327
  Scenario: AMI image synchronization between regions when conflicts. Only the ramdisk image has been modified (the checksum is different). Rename.
    Given a new image created in the Glance of master node with name "qatestingkernel01" and file "qatesting03"
    And   a new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02"
    And   a new image created in the Glance of master node with name "qatestingami01", file "qatesting01" and these properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key                      | config_value                 |
            | DEFAULT         | rename                          | any                          |
    And   already synchronized images
    And   the image "qatestingramdisk01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatestingramdisk01" and file "qatesting02b"
    And   the user properties of the image "qatestingami01" are updated in the Glance of master node:
            | param_name      | param_value                     |
            | ramdisk_id      | id(qatestingramdisk01)           |
    When  I sync images
    Then  the image "qatestingramdisk01" is renamed and replaced
    And   the image "qatestingami01" is neither renamed nor replaced
    And   the image "qatestingkernel01" is neither renamed nor replaced
    And   the image "qatestingkernel01" is present in all target nodes with the content of file "qatesting03"
    And   the image "qatestingramdisk01" is present in all target nodes with the content of file "qatesting02b"
    And   the image "qatestingami01" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatestingkernel01.old" is not present in target nodes
    And   the image "qatestingami01.old" is not present in target nodes
    And   the image "qatestingramdisk01.old" is present in all target nodes with the content of file "qatesting02"
    And   the AMI image "qatestingami01" is present in all target nodes with the following properties:
            | param_name      | param_value                     |
            | kernel_id       | id(qatestingkernel01)           |
            | ramdisk_id      | id(qatestingramdisk01)          |
