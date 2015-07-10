# -*- coding: utf-8 -*-

Feature: Image sync between regions using GlanceSync in the same federation but
  taking into account the metadata value to be synchronized.

  As a sys-admin user,
  I want to check the synchronisation of the metadata of the images in the FIWARE Lab federation
  So that the list of synchronized images has the same metadata values after the operation.

  @happy_path
    Scenario: 01: Sync a public image with correct metadata value
     Given a new image created in the Glance of master node with name "qatesting01" and this properties
             | param_name      | param_value         |
             | is_public       | True                |
             | sdc_aware       | NULL                |
             | type            | fiware:apps         |
             | nid             | 453                 |
     And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value           |
            | DEFAULT         | metadata_condition  | image.is_public        |
            | DEFAULT         | metadata_set        | 'nid, type, sdc_aware' |
     When  I sync the image
     Then  all images are synchronized
     And   the image "qatesting01" is present in all nodes with the expected data
     And   the properties values of the image "qatesting01" in all nodes are the following
             | param_name      | param_value         |
             | sdc_aware       | NULL                |
             | type            | fiware:apps         |
             | nid             | 453                 |


   @skip
    Scenario Outline: 02: Sync public images with incorrect metadata value
     Given a new image created in the Glance of master node with name "qatesting01" and this properties
            | is_public    | sdc_aware    | type    | nid    |
            | <is_public>  | <sdc_aware>  | <type>  | <nid>  |
     And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value           |
            | DEFAULT         | metadata_condition  | image.is_public        |
            | DEFAULT         | metadata_set        | 'nid, type, sdc_aware' |
     When  I sync the image
     Then  no images are synchronized
     And   this error message:"<message>" is shown to the user
            | message                                                                   |
            | The image cannot be synchronized due to the metadata value is not correct |

            Examples:
            | is_public  | sdc_aware  | type        | nid   |
            | True       | fake       | fake        | 45555 |
            | True       | fake       | fake        | fake  |
            | True       | fake       | 1234        | 45555 |
            | True       | fake       | 1234        | fake  |
            | True       | fake       |             | 45555 |
            | True       | fake       |             | fake  |
            | True       | fake       | fiware:apps | 45555 |
            | True       | fake       | fiware:apps | fake  |
            | True       | True       | fake        | 45555 |
            | True       | True       | fake        | fake  |
            | True       | True       | 1234        | 45555 |
            | True       | True       | 1234        | fake  |
            | True       | True       |             | 45555 |
            | True       | True       |             | fake  |
            | True       | True       | fiware:apps | 45555 |
            | True       | True       | fiware:apps | fake  |
            | True       | True       | fake        | 45555 |
            | True       | True       | fake        | fake  |
            | True       | True       | 1234        | 45555 |
            | True       | True       | 1234        | fake  |
            | True       | True       |             | 45555 |
            | True       | True       |             | fake  |
            | True       | True       | fiware:apps | 45555 |
            | True       | True       | fiware:apps | fake  |


    Scenario Outline: 03: Sync a public image with correct metadata value but only some metadata_set properties (only one)
     Given a new image created in the Glance of master node with name "qatesting01" and this properties
            | param_name      | param_value         |
            | is_public       | True                |
            | sdc_aware       | NULL                |
            | type            | fiware:apps         |
            | nid             | 453                 |
     And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value     |
            | DEFAULT         | metadata_condition  | image.is_public  |
            | DEFAULT         | metadata_set        | <metadata_set>   |
     When  I sync the image
     Then  all images are synchronized
     And   the image "qatesting01" is present in all nodes with the expected data
     And   the properties values of the image "qatesting01" are only the following
            | param_name      | param_value         |
            | <param_name>    | <param_value>       |

            Examples:
            | metadata_set    | param_name | param_value |
            | 'nid'           | nid        | 453         |
            | 'sdc_aware'     | sdc_aware  | NULL        |
            | 'type'          | type       | fiware:apps |
            | 'fake'          |            |             |


    Scenario Outline: 04: Sync a public image with correct metadata value but only some metadata_set properties (2 of them)
     Given a new image created in the Glance of master node with name "qatesting01" and this properties
            | param_name      | param_value         |
            | is_public       | True                |
            | sdc_aware       | NULL                |
            | type            | fiware:apps         |
            | nid             | 453                 |
     And   GlanceSync configured to sync images using this configuration parameters:
            | config_section  | config_key          | config_value     |
            | DEFAULT         | metadata_condition  | image.is_public  |
            | DEFAULT         | metadata_set        | <metadata_set>   |
     When  I sync the image
     Then  all images are synchronized
     And   the image "qatesting01" is present in all nodes with the expected data
     And   the properties values of the image "qatesting01" are only the following
            | param_name      | param_value       |
            | <param_name_1>  | <param_value_1>   |
            | <param_name_2>  | <param_value_2>   |

            Examples:
            | metadata_set           | param_name_1 | param_value_1 | param_name_2 | param_value_2 |
            | 'nid, sdc_aware'       | nid          | 453           | sdc_aware    | NULL          |
            | 'nid, type'            | nid          | 453           | type         | fiware:apps   |
            | 'sdc_aware, type'      | sdc_aware    | NULL          | type         | fiware:apps   |
            | 'sdc_aware, nid'       | sdc_aware    | NULL          | nid          | 453           |
            | 'type, nid'            | type         | fiware:apps   | nid          | 453           |
            | 'type, sdc_aware'      | type         | fiware:apps   | sdc_aware    | NULL          |
            | 'type, fake'           | type         | fiware:apps   |              |               |
            | 'fake, nid'            |              |               | nid          | 453           |
            | 'fake, fake'           |              |               |              |               |


    @skip @bug @CLAUDIA-5306
    Scenario: 05: All metadata are synchronized when metadata_set property is empty
      Given a new image created in the Glance of master node with name "qatesting01" and this properties
              | param_name      | param_value         |
              | sdc_aware       | True                |
              | type            | fiware:apps         |
              | nid             | 453                 |
      And   GlanceSync configured to sync images using this configuration parameters:
              | config_section  | config_key          | config_value           |
              | DEFAULT         | metadata_condition  | image.is_public        |
              | DEFAULT         | metadata_set        |                        |
      When  I sync the image
      Then  all images are synchronized
      And   the image "qatesting01" is present in all nodes with the expected data
      And   the properties values of the image "qatesting01" in all nodes are the following:
              | param_name      | param_value         |
              | sdc_aware       | True                |
              | type            | fiware:apps         |
              | nid             | 453                 |


    @skip @bug @CLAUDIA-5307 @CLAUDIA-5308
    Scenario Outline: 06: Sync a public image with empty metadata values
      Given a new image created in the Glance of master node with name "qatesting01" and this properties
              | param_name      | param_value         |
              | sdc_aware       | <sdc_aware_value>   |
              | nid             | <nid_value>         |
              | other_att       | <other_att_value>   |
      And   GlanceSync configured to sync images using this configuration parameters:
              | config_section  | config_key          | config_value              |
              | DEFAULT         | metadata_condition  | image.is_public           |
              | DEFAULT         | metadata_set        | 'sdc_aware,nid,other_att' |
      When  I sync the image
      Then  all images are synchronized
      And   the image "qatesting01" is present in all nodes with the expected data
      And   the properties values of the image "qatesting01" are only the following
              | param_name      | param_value         |
              | sdc_aware       | <sdc_aware_value>   |
              | nid             | <nid_value>         |
              | other_att       | <other_att_value>   |

      Examples:
            | sdc_aware_value | nid_value | other_att_value |
            | True            | 12345     |                 |
            | False           |           | abcd            |
            |                 | 678       | abcd            |
            |                 |           | abcd            |


    Scenario: 07: Sync already existent images when its metadata have changed. Update existent values (no FIWARE atts)
      Given a new image created in the Glance of master node with name "qatesting01" and this properties:
              | param_name      | param_value         |
              | nid             | 12345               |
              | new_att         | True                |
      And   GlanceSync configured to sync images using this configuration parameters:
              | config_section  | config_key          | config_value          |
              | DEFAULT         | metadata_condition  | image.is_public       |
              | DEFAULT         | metadata_set        | 'nid, new_att'        |
      And   an already synchronized images
      And   the user properties of the image "qatesting01" are updated in the Glance of master node:
              | param_name      | param_value         |
              | nid             | 67890               |
              | new_att         | False               |
      When  I sync images
      Then  metadata of all images are updated
      And   the image "qatesting01" is present in all nodes with the expected data
      And   the properties values of the image "qatesting01" in all nodes are the following:
              | param_name      | param_value         |
              | new_att         | False               |
              | nid             | 67890               |


    Scenario: 07b: Sync already existent images when its metadata have changed. Update existent values. (Only FIWARE atts)
      Given a new image created in the Glance of master node with name "qatesting01" and this properties:
              | param_name      | param_value         |
              | nid             | 12345               |
              | type            | fiware:util         |
              | nid_version     | 1                   |
      And   GlanceSync configured to sync images using this configuration parameters:
              | config_section  | config_key          | config_value              |
              | DEFAULT         | metadata_condition  | image.is_public           |
              | DEFAULT         | metadata_set        | 'nid, type, nid_version'  |
      And   an already synchronized images
      And   the user properties of the image "qatesting01" are updated in the Glance of master node:
              | param_name      | param_value         |
              | nid             | 67890               |
              | type            | fiware:ops          |
              | nid_version     | 2                   |
      When  I sync images
      Then  metadata of all images are updated
      And   the image "qatesting01" is present in all nodes with the expected data
      And   the properties values of the image "qatesting01" in all nodes are the following:
              | param_name      | param_value         |
              | nid             | 67890               |
              | type            | fiware:ops          |
              | nid_version     | 2                   |


    Scenario: 08: Sync already existent images when its metadata have changed. Add new attibrute. Same configuration properties.
      Given a new image created in the Glance of master node with name "qatesting01" and this properties:
              | param_name      | param_value         |
              | nid             | 12345               |
              | sdc_aware       | True                |
      And   GlanceSync configured to sync images using this configuration parameters:
              | config_section  | config_key          | config_value              |
              | DEFAULT         | metadata_condition  | image.is_public           |
              | DEFAULT         | metadata_set        | 'nid, sdc_aware, new_att' |
      And   an already synchronized images
      And   the user properties of the image "qatesting01" are updated in the Glance of master node:
              | param_name      | param_value         |
              | nid             | 67890               |
              | sdc_aware       | False               |
              | new_att         | qa-test             |
      When  I sync images
      Then  metadata of all images are updated
      And   the image "qatesting01" is present in all nodes with the expected data
      And   the properties values of the image "qatesting01" in all nodes are the following:
              | param_name      | param_value         |
              | sdc_aware       | False               |
              | nid             | 67890               |
              | new_att         | qa-test             |


    Scenario: 09: Sync already existent images when its metadata have changed. Remove attribute. Same configuration properties.
      Given a new image created in the Glance of master node with name "qatesting01" and this properties:
              | param_name      | param_value         |
              | nid             | 12345               |
              | sdc_aware       | True                |
              | new_att         | qa-test             |
      And   GlanceSync configured to sync images using this configuration parameters:
              | config_section  | config_key          | config_value              |
              | DEFAULT         | metadata_condition  | image.is_public           |
              | DEFAULT         | metadata_set        | 'nid, sdc_aware, new_att' |
      And   an already synchronized images
      And   the image "qatesting01" is deleted from the Glance of master node
      And   other new image created in the Glance of master node with name "qatesting01" and these properties:
              | param_name      | param_value         |
              | sdc_aware       | False               |
              | nid             | 67890               |
      When  I sync images
      Then  metadata of all images are updated
      And   the image "qatesting01" is present in all nodes with the expected data
      And   the properties values of the image "qatesting01" in all nodes are the following:
              | param_name      | param_value         |
              | sdc_aware       | False               |
              | nid             | 67890               |


    Scenario: 10: Sync already existent images when its metadata have changed. Add and edit attributes. Same configuration properties.
      Given a new image created in the Glance of master node with name "qatesting01" and this properties:
              | param_name      | param_value         |
              | nid             | 12345               |
              | sdc_aware       | True                |
      And   GlanceSync configured to sync images using this configuration parameters:
              | config_section  | config_key          | config_value              |
              | DEFAULT         | metadata_condition  | image.is_public           |
              | DEFAULT         | metadata_set        | 'nid, sdc_aware, new_att' |
      And   an already synchronized images
      And   the user properties of the image "qatesting01" are updated in the Glance of master node:
              | param_name      | param_value         |
              | nid             | 67890               |
              | sdc_aware       | False               |
              | new_att         | qa-test             |
      When  I sync images
      Then  metadata of all images are updated
      And   the image "qatesting01" is present in all nodes with the expected data
      And   the properties values of the image "qatesting01" in all nodes are the following:
              | param_name      | param_value         |
              | sdc_aware       | False               |
              | nid             | 67890               |
              | new_att         | qa-test             |


    Scenario: 11: Sync already existent images when its metadata have changed. Attributes not present in metadata_set should not be updated.
      Given a new image created in the Glance of master node with name "qatesting01" and this properties:
              | param_name      | param_value         |
              | nid             | 12345               |
              | sdc_aware       | True                |
              | new_att         | qa-test             |
      And   GlanceSync configured to sync images using this configuration parameters:
              | config_section  | config_key          | config_value              |
              | DEFAULT         | metadata_condition  | image.is_public           |
              | DEFAULT         | metadata_set        | 'nid, sdc_aware, new_att' |
      And   an already synchronized images
      And   the user properties of the image "qatesting01" are updated in the Glance of master node:
              | param_name      | param_value         |
              | nid             | 67890               |
              | sdc_aware       | False               |
              | new_att         | qa-test2            |
      And   GlanceSync configured to sync images using this configuration parameters:
              | config_section  | config_key          | config_value              |
              | DEFAULT         | metadata_condition  | image.is_public           |
              | DEFAULT         | metadata_set        | 'nid, sdc_aware'          |
      When  I sync images
      Then  metadata of all images are updated
      And   the image "qatesting01" is present in all nodes with the expected data
      And   the properties values of the image "qatesting01" in all target nodes are the following:
              | param_name      | param_value         |
              | sdc_aware       | False               |
              | nid             | 67890               |
              | new_att         | qa-test             |
