# -*- coding: utf-8 -*-

Feature: GlanceSync CLI implementation: dry-run

  As a sys-admin user,
  I want to simulate a new synchronization operation without creating real objects
  so that I see what operations are going to be performed.


  Scenario: Simple image synchronization between regions using CLI dry-run option
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    When  I run the sync command with options "--dry-run"
    Then  the image "qatesting01" is pending for synchronization
    And   the image "qatesting01" is not present in target nodes


  Scenario: Simple image synchronization between regions with correct metadata value using CLI dry-run option
    Given a new image created in the Glance of master node with name "qatesting01" and these properties
             | param_name      | param_value         |
             | is_public       | True                |
             | sdc_aware       | NULL                |
             | type            | fiware:apps         |
             | nid             | 453                 |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value           |
            | DEFAULT         | metadata_condition  | image.is_public        |
            | DEFAULT         | metadata_set        | 'nid, type, sdc_aware' |
    When  I run the sync command with options "--dry-run"
    Then  the image "qatesting01" is pending for synchronization
    And   the image "qatesting01" is not present in target nodes
