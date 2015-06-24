# -*- coding: utf-8 -*-

Feature: Image sync between regions using GlanceSync in the same federation with metadata conditions.
  As a sys-admin of FIWARE federation
  I want to sync images from master node to other nodes in the federation using 'custom' configuration
  So that I can use the same base images in all nodes and keep them updated

  @happy_path
  Scenario: Sync a private image
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'not image.is_public' |
            | DEFAULT         | metadata_set        |                       |
    When  I sync the image
    Then  all images are synchronized
    And   the image "qatesting01" is present in all nodes with the expected data


  @happy_path
  Scenario Outline: Sync a private image with image attributes in metadata set
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | ''                    |
            | DEFAULT         | metadata_set        | <config_value>        |
    When  I sync the image
    Then  all images are synchronized
    And   the image "qatesting01" is present in all nodes with the expected data

    Examples:
            | config_value          |
            | nid                   |
            | sdc_aware             |
            | nid, sdc_aware        |
            | nid, sdc_aware, type  |


  Scenario: Sync a private image with image attributes not in metadata set: Empty image properties
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | ''                    |
            | DEFAULT         | metadata_set        | 'nid, sdc_aware'      |
    When  I sync the image
    Then  no images are synchronized


  Scenario Outline: Sync a private image with image attributes not in metadata set. Image properties not in metadata set
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | ''                    |
            | DEFAULT         | metadata_set        | <config_value>        |
    When  I sync the image
    Then  no images are synchronized

    Examples:
            | config_value          |
            | nid_version           |
            | nid_version, type     |


  Scenario: Sync a private image with image attributes in metadata set but not passing the metadata condition
    Given a new image created in the Glance of master node with name "qatesting01" and this properties:
            | param_name      | param_value         |
            | is_public       | False               |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | image.is_public       |
            | DEFAULT         | metadata_set        | nid                   |
    When  I sync the image
    Then  no images are synchronized
