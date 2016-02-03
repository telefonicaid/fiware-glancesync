# -*- coding: utf-8 -*-

Feature: Image sync between regions using GlanceSync in the same federation with 'forcesync' mode.
  As a sys-admin of FIWARE federation
  I want to sync images from master node to other nodes in the federation although sync conditions are not complied (master)
  So that I can use the same base images in all nodes and keep them updated


  @happy_path
  Scenario: Sync an image although it does not comply sync conditions: Non-public images. No checksum conflicts.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | forcesyncs          | id(qatesting01)       |
    When  I sync the image
    Then  all images are synchronized
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01"
    And   the properties values of the image "qatesting01" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |


  @happy_path
  Scenario: Sync some images although they do not comply sync conditions: Non-public images. No checksum conflicts.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    Given a new image created in the Glance of master node with name "qatesting02" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    Given a new image created in the Glance of master node with name "qatesting03" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value                                        |
            | DEFAULT         | metadata_condition  | 'image.is_public'                                   |
            | DEFAULT         | metadata_set        |                                                     |
            | DEFAULT         | forcesyncs          | 'id(qatesting01), id(qatesting02), id(qatesting03)' |
    When  I sync the image
    Then  all images are synchronized
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01"
    And   the properties values of the image "qatesting01" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |
    And   the properties values of the image "qatesting02" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |
    And   the properties values of the image "qatesting03" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |


  Scenario: Images are not sync when they do not comply sync condition and its ID is not in forcesyncs property.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | forcesyncs          | 1234567890            |
    When  I sync images
    Then  no images are synchronized


  Scenario: Images are not sync when they do not comply sync condition and its ID is not in forcesyncs property.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | forcesyncs          | 1234567890            |
    When  I sync images
    Then  no images are synchronized


  Scenario: Sync images although the do not comply sync conditions: Public image with metadata but not metadata_set to sync. No checksum conflicts.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
            | att4            | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value                                |
            | DEFAULT         | metadata_condition  | 'image.is_public and "att3" in metadata_set'|
            | DEFAULT         | metadata_set        |                                             |
            | DEFAULT         | forcesyncs          | id(qatesting01)                             |
    When  I sync the image
    Then  all images are synchronized
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01"
    And   the properties values of the image "qatesting01" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |


  Scenario: Sync images although the do not comply sync conditions: Public image with metadata and metadata_set. No checksum conflicts.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
            | att4            | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value                                |
            | DEFAULT         | metadata_condition  | 'image.is_public and "att3" in metadata_set'|
            | DEFAULT         | metadata_set        | att4                                        |
            | DEFAULT         | forcesyncs          | id(qatesting01)                             |
    When  I sync the image
    Then  all images are synchronized
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01"
    And   the properties values of the image "qatesting01" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |
            | att4            | False               |


  Scenario: Sync images although they do not comply sync conditions: Non-public images. Checksum conflicts.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | forcesyncs          | id(qatesting01)       |
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | forcesyncs          | id(qatesting01)       |
    When  I sync the image
    And   a warning message is shown informing about checksum conflict with "qatesting01"
    Then  no images are synchronized


  @happy_path
  Scenario: Sync images although they do not comply sync conditions: Non-public images. Checksum conflicts: replace.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | forcesyncs          | id(qatesting01)       |
            | DEFAULT         | replace             | checksum(qatesting01) |
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01", file "qatesting01b" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | forcesyncs          | id(qatesting01)       |
    When  I sync the image
    Then  all images are replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"


  Scenario: Sync images although they do not comply sync conditions: Non-public images. Checksum conflicts: rename.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | forcesyncs          | id(qatesting01)       |
            | DEFAULT         | rename              | checksum(qatesting01) |
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | forcesyncs          | id(qatesting01)       |
    When  I sync the image
    Then  all images are renamed and replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting01.old" is present in all target nodes with the content of file "qatesting01"


  @happy_path
  Scenario Outline: Sync images although some of them do not comply sync conditions: Public and non-public images. No checksum conflicts.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
    Given a new image created in the Glance of master node with name "qatesting02" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | forcesyncs          | <forcesync_value>     |
    When  I sync the image
    Then  all images are synchronized
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01"
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02"
    And   the properties values of the image "qatesting01" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | True                |
    And   the properties values of the image "qatesting02" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |

    Examples:
            | forcesync_value                       |
            | id(qatesting02)                       |
            | 'id(qatesting01), id(qatesting02)'    |


  @happy_path
  Scenario: Sync images although some of them do not comply sync conditions: Public and non-public images with metadata and checksum conflicts.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | att1            | att1                |
            | att2            | att2                |
    Given a new image created in the Glance of master node with name "qatesting02" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
            | att1            | att1                |
            | att3            | att3                |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value                                   |
            | DEFAULT         | metadata_condition  | 'image.is_public'                              |
            | DEFAULT         | metadata_set        | 'att1, att2'                                   |
            | DEFAULT         | forcesyncs          | id(qatesting02)                                |
            | DEFAULT         | replace             | 'checksum(qatesting01), checksum(qatesting02)' |
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   the image "qatesting02" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01", file "qatesting01b" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | att1            | att1_v2             |
            | att2            | att2_v2             |
    And   other new image created in the Glance of master node with name "qatesting02", file "qatesting02b" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
            | att1            | att1_v2             |
            | att3            | att3_v2             |
    Given a new image created in the Glance of master node with name "qatesting03" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
            | att1            | att1                |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | forcesyncs          | id(qatesting02)       |
    When  I sync the image
    Then  the image "qatesting01" is replaced
    And   the image "qatesting02" is replaced
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02b"
    And   the image "qatesting03" is not present in target nodes
    And   the properties values of the image "qatesting01" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | True                |
            | att1            | att1_v2             |
            | att2            | att2_v2             |
    And   the properties values of the image "qatesting02" in all target nodes are the following:
            | param_name      | param_value         |
            | is_public       | False               |
            | att1            | att1_v2             |
