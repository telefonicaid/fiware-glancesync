# -*- coding: utf-8 -*-

Feature: Image sync between regions using GlanceSync in the same federation and images managed by different tenants.
  As a sys-admin of FIWARE federation
  I want to sync images managed by different tenants using the GlanceSync configuration property 'only_tenant_images'
  So that I can use the same base images in all nodes and keep them updated


  @happy_path
  Scenario: Image synchronization when exists an image with the same name, content and tenant (base tenant credentials). Only tenant images.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of any target node with name "qatesting01", file "qatesting01" and using a credential type "base_admin"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | only_tenant_images  | True                  |
    When  I sync images
    Then  no images are synchronized


  Scenario: Image synchronization when exists an image with the same name and content but different tenant. Only tenant images.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of any target node with name "qatesting01", file "qatesting01" and using a credential type "secondary_admin"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | only_tenant_images  | True                  |
    When  I sync images
    Then  the image "qatesting01" is synchronized


  Scenario: Image synchronization when exists an image with the same name but different content and tenant in a target node. NOT only tenant images.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of any target node with name "qatesting01", file "qatesting01b" and using a credential type "secondary_admin"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | only_tenant_images  | False                 |
    When  I sync images
    Then  no images are synchronized
    And   a warning message is shown informing about different owner for image "qatesting01"


  Scenario: Image synchronization when exists an image with the same name but different content and tenant in a target node. NOT only tenant images. Does NOT match metadata condition.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of any target node with name "qatesting01", file "qatesting01b" and using a credential type "secondary_admin"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  |                       |
            | DEFAULT         | metadata_set        | meta                  |
            | DEFAULT         | replace             | any                   |
            | DEFAULT         | only_tenant_images  | False                 |
    When  I sync images
    Then  no images are synchronized


  @happy_path
  Scenario: Image synchronization when exists an image with the same name but different content and tenant in a target node. NOT only tenant images. Replace.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of any target node with name "qatesting01", file "qatesting01b" and using a credential type "secondary_admin"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | replace             | any                   |
            | DEFAULT         | only_tenant_images  | False                 |
    When  I sync images
    Then  the image "qatesting01" is replaced
    And   a warning message is shown informing about different owner for image "qatesting01"
