# -*- coding: utf-8 -*-

Feature: GlanceSync CLI implementation. Parallel execution.

  As a sys-admin user,
  I want to run GlanceSync in a parallel way
  so that I can synchronize some regions at the same time


  Scenario: Sync images in a parallel way. Only one child process (sequential).
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | main            | max_children        | 1                     |
            | DEFAULT         | metadata_condition  | image.is_public       |
            | DEFAULT         | metadata_set        | 'nid, sdc_aware'      |
    When  I run the sync command with options "--parallel"
    Then  parallel process is executed for all nodes
    And   files are created with output logs
    And   all images are synchronized in a parallel execution
    And   the image "qatesting01" is present in all nodes with the expected data


  Scenario: Sync images in a parallel way. Some children processes (parallel).
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12345               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | main            | max_children        | 3                     |
            | DEFAULT         | metadata_condition  | image.is_public       |
            | DEFAULT         | metadata_set        | 'nid,sdc_aware'       |
    When  I run the sync command with options "--parallel"
    Then  parallel process is executed for all nodes
    And   files are created with output logs
    And   all images are synchronized in a parallel execution
    And   the image "qatesting01" is present in all nodes with the expected data


  Scenario Outline: Sync images in a parallel way when warnings are produced. Image conflicts. No images are synchronized.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | main            | max_children        | 3                     |
            | DEFAULT         | <config_key>        | 123-123-123-1231-2312 |
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    When  I run the sync command with options "--parallel"
    Then  parallel process is executed for all nodes
    And   files are created with output logs
    And   a warning message is logged informing about checksum conflict with "qatesting01" in a parallel execution
    And   no images are synchronized in a parallel execution

    Examples:
            | config_key |
            | replace    |
            | rename     |
            | dontupdate |


  Scenario: Sync images in a parallel way when there are checksum conflicts: rename and replace.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of master node with name "qatesting02"
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        |                       |
            | DEFAULT         | replace             | checksum(qatesting01) |
            | DEFAULT         | rename              | checksum(qatesting02) |
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   the image "qatesting02" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    And   other new image created in the Glance of master node with name "qatesting02" and file "qatesting02b"
    When  I run the sync command with options "--parallel"
    Then  parallel process is executed for all nodes
    And   files are created with output logs
    And   the image "qatesting01" is replaced in a parallel execution
    And   the image "qatesting02" is renamed and replaced in a parallel execution
    And   the image "qatesting01" is present in all nodes with the content of file "qatesting01b"
    And   the image "qatesting02" is present in all nodes with the content of file "qatesting02b"
    And   the image "qatesting02.old" is present in all target nodes with the content of file "qatesting02"
    And   the image "qatestubg01.old" is not present in target nodes
