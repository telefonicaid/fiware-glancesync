# -*- coding: utf-8 -*-

Feature: Image sync between regions, choosing the preferable order or regions for synchronization.
  As a sys-admin of FIWARE federation
  I want to sync images from master node to other nodes in the federation using 'custom' properties to keep the sync order
  So that I can use the same base images in all nodes and keep them updated in regions following the preferable order


  @skip @block @CLAUDIA-4552 @happy_path @env_dependant @experimentation
  Scenario Outline: Sync images following a preferable order (default behaviour).
    Given a new image created in the Glance of master node with name "qatesting10meg"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value           |
            | DEFAULT         | metadata_condition  | 'image.is_public'      |
            | DEFAULT         | metadata_set        |                        |
            | main            | preferable_order    | <preferable_order>     |
    When  I sync images
    Then  all images are synchronized
    And   the timestamp of image "qatesting10meg" in "<node_greater>" is greater than the image in "<node_lesser>"

    Examples:
            | preferable_order       | node_greater | node_lesser |
            | 'Burgos, Salamanca'    | Salamanca    | Burgos      |
            | 'Salamanca, Burgos'    | Burgos       | Madrid      |


  @skip @bug @CLAUDIA-5323 @env_dependant @experimentation
  Scenario Outline: Sync images between different targets, following a preferable order.
    Given a new image created in the Glance of master node with name "qatesting10meg"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value           |
            | DEFAULT         | metadata_condition  | 'image.is_public'      |
            | DEFAULT         | metadata_set        |                        |
            | main            | preferable_order    | <preferable_order>     |
    When  I sync images on "master:Burgos federation2:Madrid"
    Then  all images are synchronized
    And   the timestamp of image "qatesting10meg" in "<node_greater>" is greater than the image in "<node_lesser>"

    Examples:
            | preferable_order             | node_greater | node_lesser |
            | 'Burgos, federation2:Madrid' | Madrid       | Burgos      |
            | 'federation2:Madrid, Burgos' | Burgos       | Madrid      |
