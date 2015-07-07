# -*- coding: utf-8 -*-

Feature: Image sync between regions using GlanceSync in the same federation when conflicts happen (checksum).
  As a sys-admin of FIWARE federation
  I want to sync images from master node to other nodes in the federation using 'custom' properties to manage conflicts
  So that I can use the same base images in all nodes and keep them updated (replace, rename, dontupdate)


  @happy_path
  Scenario: Sync images when there are checksum conflicts: replace. Image without metadata.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | replace             | checksum(qatesting01) |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    When  I sync the image
    Then  all images are replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"


  @skip @bug @CLAUDIA-5189
  Scenario Outline: Sync images when there are checksum conflicts. ImageID is not updated.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | <config_key>        | 123-123-123-1231-2312 |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    When  I sync images
    And   a warning message is shown informing about checksum conflict with "qatesting01"
    Then  no images are synchronized

    Examples:
            | config_key |
            | replace    |
            | rename     |
            | dontupdate |


  Scenario Outline: Sync images when there are checksum conflicts: replace. One image with different metadata.
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  |                       |
            | DEFAULT         | metadata_set        | 'nid, sdc_aware'      |
            | DEFAULT         | replace             | <replace>             |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01", file "qatesting01b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    When  I sync the image
    Then  all images are replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the properties values of the image "qatesting01" in all nodes are the following:
            | param_name      | param_value         |
            | nid             | 33333               |
            | sdc_aware       | False               |

    Examples:
            | replace               |
            | checksum(qatesting01) |
            | any                   |


  Scenario Outline: Sync images when there are checksum conflicts: replace. Some images with different metadata.
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   a new image created in the Glance of master node with name "qatesting02" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 67890               |
            | sdc_aware       | False               |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  |                       |
            | DEFAULT         | metadata_set        | 'nid, sdc_aware'      |
            | DEFAULT         | replace             | <replace>             |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   the image "qatesting02" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01", file "qatesting01b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    And   other new image created in the Glance of master node with name "qatesting02", file "qatesting02b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 44444               |
            | sdc_aware       | True                |
    When  I sync images
    Then  all images are replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02b"
    And   the properties values of the image "qatesting01" in all nodes are the following:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    And   the properties values of the image "qatesting02" in all nodes are the following:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 44444               |
            | sdc_aware       | True                |

    Examples:
            | replace                                             |
            | 'checksum(qatesting01), checksum(qatesting02)'      |
            | 'checksum(qatesting01), any'                        |
            | any                                                 |


  @happy_path
  Scenario: Sync images when there are checksum conflicts: rename. Image without metadata.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | rename              | checksum(qatesting01) |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    When  I sync the image
    Then  all images are renamed and replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting01.old" is present in all target nodes with the content of file "qatesting01"


  Scenario Outline: Sync images when there are checksum conflicts: rename. One image with different metadata.
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  |                       |
            | DEFAULT         | metadata_set        | 'nid, sdc_aware'      |
            | DEFAULT         | rename              | <rename>              |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01", file "qatesting01b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    When  I sync the image
    Then  all images are renamed and replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting01.old" is present in all target nodes with the content of file "qatesting01"
    And   the properties values of the image "qatesting01" in all nodes are the following:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    And   the properties values of the image "qatesting01.old" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |
            | nid             | 12345               |
            | sdc_aware       | True                |

    Examples:
            | rename                |
            | checksum(qatesting01) |
            | any                   |


  Scenario Outline: Sync images when there are checksum conflicts: rename. Some images with different metadata.
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   a new image created in the Glance of master node with name "qatesting02" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 67890               |
            | sdc_aware       | False               |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  |                       |
            | DEFAULT         | metadata_set        | 'nid, sdc_aware'      |
            | DEFAULT         | rename              | <rename>              |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   the image "qatesting02" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01", file "qatesting01b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    And   other new image created in the Glance of master node with name "qatesting02", file "qatesting02b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 44444               |
            | sdc_aware       | True                |
    When  I sync images
    Then  all images are renamed and replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02b"
    And   the image "qatesting01.old" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatesting02.old" is present in all target nodes with the content of file "qatesting02"
    And   the properties values of the image "qatesting01" in all nodes are the following:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    And   the properties values of the image "qatesting02" in all nodes are the following:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 44444               |
            | sdc_aware       | True                |
    And   the properties values of the image "qatesting01.old" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   the properties values of the image "qatesting02.old" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |
            | nid             | 67890               |
            | sdc_aware       | False               |

    Examples:
            | rename                                          |
            | 'checksum(qatesting01), checksum(qatesting02)'  |
            | 'checksum(qatesting01), any'                    |
            | any                                             |


  @happy_path
  Scenario: Sync images when there are checksum conflicts: rename and replace. Image without metadata.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of master node with name "qatesting02"
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | replace             | checksum(qatesting01) |
            | DEFAULT         | rename              | checksum(qatesting02) |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   the image "qatesting02" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    And   other new image created in the Glance of master node with name "qatesting02" and file "qatesting02b"
    When  I sync images
    Then  the image "qatesting01" is replaced
    And   the image "qatesting02" is renamed and replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02b"
    And   the image "qatesting02.old" is present in all target nodes with the content of file "qatesting02"
    And   the image "qatestubg01.old" is not present in target nodes


  Scenario: Sync images when there are checksum conflicts: rename and replace. Some images with different metadata.
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   a new image created in the Glance of master node with name "qatesting02" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 67890               |
            | sdc_aware       | False               |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  |                       |
            | DEFAULT         | metadata_set        | 'nid, sdc_aware'      |
            | DEFAULT         | replace             | checksum(qatesting01) |
            | DEFAULT         | rename              | checksum(qatesting02) |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   the image "qatesting02" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01", file "qatesting01b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    And   other new image created in the Glance of master node with name "qatesting02", file "qatesting02b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 44444               |
            | sdc_aware       | True                |
    When  I sync images
    Then  the image "qatesting01" is replaced
    And   the image "qatesting02" is renamed and replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02b"
    And   the image "qatesting02.old" is present in all target nodes with the content of file "qatesting02"
    And   the properties values of the image "qatesting01" in all nodes are the following:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 33333               |
            | sdc_aware       | False               |
    And   the properties values of the image "qatesting02" in all nodes are the following:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 44444               |
            | sdc_aware       | True                |
    And   the properties values of the image "qatesting02.old" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |
            | nid             | 67890               |
            | sdc_aware       | False               |


  @skip @bug @CLAUDIA-5301
  Scenario Outline: Sync images when there are checksum conflicts: rename and replace. If both properties are any or IMAGE_ID is in both: rename.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of master node with name "qatesting02"
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | replace             | <replace>             |
            | DEFAULT         | rename              | <rename>              |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   the image "qatesting02" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    And   other new image created in the Glance of master node with name "qatesting02" and file "qatesting02b"
    When  I sync images
    Then  the image "qatesting01" is renamed and replaced
    And   the image "qatesting02" is renamed and replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02b"
    And   the image "qatesting01.old" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatesting02.old" is present in all target nodes with the content of file "qatesting02"

    Examples:
        | replace               | rename                                         |
        | checksum(qatesting01) | 'checksum(qatesting02), checksum(qatesting01)' |
        | any                   | any                                            |


  Scenario: Sync images when there are checksum conflicts: rename and replace. IMAGE_ID overrides 'any' when executing rename behaviour
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | replace             | any                   |
            | DEFAULT         | rename              | checksum(qatesting01) |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    When  I sync images
    Then  the image "qatesting01" is renamed and replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting01.old" is present in all target nodes with the content of file "qatesting01"


  Scenario: Sync images when there are checksum conflicts: rename and replace. IMAGE_ID overrides 'any' when executing replace behaviour (2/2)
    And   a new image created in the Glance of master node with name "qatesting02"
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | replace             | checksum(qatesting02) |
            | DEFAULT         | rename              | any                   |
    And   an already synchronized images
    And   the image "qatesting02" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting02" and file "qatesting02b"
    When  I sync images
    And   the image "qatesting02" is replaced
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02b"


  @happy_path
  Scenario: Sync images when there are checksum conflicts: dontupdate.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | replace             | any                   |
            | DEFAULT         | rename              | any                   |
            | DEFAULT         | dontupdate          | checksum(qatesting01) |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    When  I sync the image
    Then  no images are synchronized
    And   the image "qatesting01" is present in all target nodes with the content of file "qatesting01"


  Scenario: Sync images when there are checksum conflicts: dontupdate. Some images.
    Given a new image created in the Glance of master node with name "qatesting01"
    Given a new image created in the Glance of master node with name "qatesting02"
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | replace             | any                   |
            | DEFAULT         | rename              | any                   |
            | DEFAULT         | dontupdate          | checksum(qatesting01) |
    And   an already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   the image "qatesting02" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    And   other new image created in the Glance of master node with name "qatesting02" and file "qatesting02b"
    When  I sync images
    Then  the image "qatesting01" is not synchronized
    And   the image "qatesting02" is renamed and replaced
    And   the image "qatesting01" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02b"
