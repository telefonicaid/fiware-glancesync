# -*- coding: utf-8 -*-

Feature: GlanceSync CLI implementation. Configuration given by CLI params.

  As a sys-admin user,
  I want to pass configuration parameters by CLI params.
  so that I can change the GlanceSync configuration easily.


  Scenario Outline: Sync a private image using configuration parameters given by CLI params (1/2).
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images without specifying any condition
    When  I run the sync command with options "<option_string>"
    Then  all images are synchronized
    And   the image "qatesting01" is present in all nodes with the expected data

    Examples:
          | option_string                                             |
          | --config DEFAULT.metadata_condition='not image.is_public' |
          | --config metadata_condition='not image.is_public'         |

  Scenario: Sync a private image using configuration parameters given by CLI params (2/2).
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images without specifying any condition
    When  I run the sync command with options "--config master.ignore_regions='Caceres' metadata_condition='not image.is_public'"
    Then  the image "qatesting01" is only present in target node "Burgos"


  Scenario: Image is not synchronized due to the given configuration parameters by CLI.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images without specifying any condition
    When  I run the sync command with options "--config metadata_condition=image.is_public"
    Then  no images are synchronized
    And   the image "qatesting01" is not present in target nodes


  Scenario: Image is not synchronized due to the given configuration parameters by CLI and different configuration in config file.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        | ''                    |
    When  I run the sync command with options "--config metadata_condition='' metadata_set='nid, sdc_aware'"
    Then  no images are synchronized
    And   the image "qatesting01" is not present in target nodes


  Scenario: Sync an image using configuration parameters given by CLI params and different configuration in config file.
    Given a new image created in the Glance of master node with name "qatesting01" and these properties:
            | param_name      | param_value         |
            | is_public       | True                |
            | nid             | 12344               |
            | sdc_aware       | True                |
    And   GlanceSync configured to sync images using these configuration parameters:
            | config_section  | config_key          | config_value          |
            | DEFAULT         | metadata_condition  | 'image.is_public'     |
            | DEFAULT         | metadata_set        | ''                    |
    When  I run the sync command with options "--config metadata_condition='image.is_public' metadata_set=nid,sdc_aware"
    Then  all images are synchronized
    And   the image "qatesting01" is present in all nodes with the expected data
