# -*- coding: utf-8 -*-

Feature: Image sync between regions using GlanceSync, when images are obsoletes.
  As a sys-admin of FIWARE federation
  I want to manage obsolete images and sync them from master node to other nodes in the federation
  So that I can deprecate and hide old images in all FIWARE nodes


  Scenario: Obsolete image is not synchronized.
    Given a new image created in the Glance of master node with name "qatesting01_obsolete" and file "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  no images are synchronized
    And   the image "qatesting01_obsolete" is not present in target nodes


  Scenario: Sync an obsolete image when the same image exists in the target node.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatesting01" is mark as obsolete in the Glance of master node
    When  I sync images
    Then  the obsolete image "qatesting01" is synchronized
    And   the image "qatesting01_obsolete" is present in all nodes with the content of file "qatesting01"


  Scenario: Sync an obsolete image with same name but different checksum.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    And   the image "qatesting01" is mark as obsolete in the Glance of master node
    When  I sync images
    Then  no images are synchronized
    And   the image "qatesting01" is present in all target nodes with the content of file "qatesting01"


  Scenario: Obsoletes images are not considered when 'support_obsolete_images' configuration property is False.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key              | config_value          |
            | DEFAULT         | metadata_condition      | 'image.is_public'     |
            | DEFAULT         | metadata_set            |                       |
            | DEFAULT         | support_obsolete_images | False                 |
    And   already synchronized images
    And   the image "qatesting01" is mark as obsolete in the Glance of master node
    When  I sync images
    Then  no images are synchronized
    And   the image "qatesting01_obsolete" is not present in target nodes


  Scenario: Sync a new image with the same name as the obsolete one (already sync) and same checksum (Obsolete is deleted before sync).
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatesting01" is mark as obsolete in the Glance of master node
    And   I sync images
    And   the image "qatesting01_onsolete" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01"
    When  I sync images
    Then  the image "qatesting01" is synchronized
    And   the image "qatesting01_obsolete" is not synchronized
    And   the image "qatesting01_obsolete" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatesting01" is present in all nodes with the expected data
    And   a warning message is shown informing about ignored obsolete image "qatesting01"


  Scenario: Sync a new image with the same name as the obsolete one (already sync) and same checksum (Obsolete is not deleted before sync).
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatesting01" is mark as obsolete in the Glance of master node
    And   I sync images
    And   other new image created in the Glance of master node with name "qatesting01"
    When  I sync images
    Then  the image "qatesting01" is synchronized
    And   the image "qatesting01_obsolete" is not synchronized
    And   the image "qatesting01_obsolete" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatesting01" is present in all nodes with the expected data
    And   a warning message is shown informing about ignored obsolete image "qatesting01"


  Scenario: Sync an image with same name as obsolete one and different checksum.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatesting01" is mark as obsolete in the Glance of master node
    And   I sync images
    And   the image "qatesting01_onsolete" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    When  I sync images
    Then  the image "qatesting01" is synchronized
    And   the image "qatesting01_obsolete" is not synchronized
    And   the image "qatesting01_obsolete" is present in all target nodes with the content of file "qatesting01"
    And   the image "qatesting01" is present in all target nodes with the content of file "qatesting01b"
    And   a warning message is shown informing about ignored obsolete image "qatesting01"


  Scenario: Visibility of the image is synchronized to its corresponding 'obsolete'.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value             |
            | is_public       | True                    |
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatesting01" is mark as obsolete in the Glance of master node
    And   the user properties of the image "qatesting01_obsolete" are updated in the Glance of master node:
            | param_name      | param_value             |
            | is_public       | False                   |
    When  I sync images
    Then  the obsolete image "qatesting01" is synchronized
    And   the image "qatesting01_obsolete" is present in all nodes with the content of file "qatesting01"
    And   the properties values of the image "qatesting01_obsolete" in all nodes are the following:
            | param_name      | param_value             |
            | is_public       | False                   |


  Scenario: Custom properties of the image are synchronized to its corresponding 'obsolete'.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value             |
            | is_public       | True                    |
            | param01         | VALUE-A                 |
            | sdc_aware       | True                    |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key              | config_value          |
            | DEFAULT         | metadata_condition      | 'image.is_public'     |
            | DEFAULT         | metadata_set            | 'param01,sdc_aware'   |
            | master          | obsolete_syncprops       | 'sdc_aware'           |
    And   already synchronized images
    And   the image "qatesting01" is mark as obsolete in the Glance of master node
    And   the user properties of the image "qatesting01_obsolete" are updated in the Glance of master node:
            | param_name      | param_value             |
            | is_public       | False                   |
            | sdc_aware       | False                   |
            | param01         | VALUE-B                 |
    When  I sync images
    Then  the obsolete image "qatesting01" is synchronized
    And   the image "qatesting01_obsolete" is present in all nodes with the content of file "qatesting01"
    And   the properties values of the image "qatesting01_obsolete" in all target nodes are the following:
            | param_name      | param_value             |
            | is_public       | False                   |
            | sdc_aware       | False                   |
            | param01         | VALUE-A                 |


  Scenario: Sync more than one obsolete images when the same images exist in the target node.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of master node with name "qatesting02"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatesting01" is mark as obsolete in the Glance of master node
    And   the image "qatesting02" is mark as obsolete in the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting03"
    When  I sync images
    Then  the obsolete image "qatesting01" is synchronized
    And   the obsolete image "qatesting02" is synchronized
    And   the image "qatesting03" is synchronized
    And   the image "qatesting01_obsolete" is present in all nodes with the content of file "qatesting01"
    And   the image "qatesting02_obsolete" is present in all nodes with the content of file "qatesting02"
    And   the image "qatesting03" is present in all nodes with the content of file "qatesting03"


  Scenario: Images with the same name and checksum but different tenants are not considered obsoletes.
    Given a new image created in the Glance of master node with name "qatesting01_obsolete" and file "qatesting01"
    And   a new image created in the Glance of all target node with name "qatesting01", file "qatesting01" and using a credential type "secondary_admin"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
    When  I sync images
    And   the image "qatesting01_obsolete" is not synchronized
    And   the image "qatesting01_obsolete" is not present in target nodes
    And   the image "qatesting01" is present in all target nodes with the content of file "qatesting01"
