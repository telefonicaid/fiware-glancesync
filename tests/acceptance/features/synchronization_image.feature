# -*- coding: utf-8 -*-

Feature: Image sync between regions using GlanceSync in the same federation.
  As a sys-admin of FIWARE federation
  I want to sync images from master node to other nodes in the federation
  So that I can use the same base images in all nodes and keep them updated

  @happy_path
  Scenario: Simple image synchronization between regions
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  the image "qatesting01" is synchronized
    And   the image "qatesting01" is present in all nodes with the expected data


  Scenario: Synchronization of more than one images
    Given the following images created in the Glance of master node with name:
          | image_name  |
          | qatesting01 |
          | qatesting02 |
          | qatesting03 |
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  all images are synchronized
    And   all synchronized images are present in all nodes with the expected data


  Scenario: Image synchronization when master node has not got images in Glance
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  no images are synchronized


  Scenario: Already synchronized images are not sync again
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    When  I sync images
    Then  the image "qatesting01" is not synchronized again
    And   the image "qatesting01" is present in all nodes with the expected data


  Scenario: Sync some images when they have already been synchronized
    Given the following images created in the Glance of master node with name:
          | image_name  |
          | qatesting01 |
          | qatesting02 |
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    When  I sync images
    Then  no images are synchronized
    And   the image "qatesting01" is not synchronized again
    And   the image "qatesting02" is not synchronized again
    And   all synchronized images are present in all nodes with the expected data


  Scenario: Sync some new images when other ones have already been synchronized
    Given the following images created in the Glance of master node with name:
          | image_name  |
          | qatesting01 |
          | qatesting02 |
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   other new image created in the Glance of master node with name "qatesting03"
    When  I sync images
    Then  the image "qatesting03" is synchronized
    And   the image "qatesting01" is not synchronized again
    And   the image "qatesting02" is not synchronized again
    And   all synchronized images are present in all nodes with the expected data


  @happy_path
  Scenario: Non-Public images are not synchronized by default
    Given a new image created in the Glance of master node with name "qatesting01" and these properties
            | param_name      | param_value         |
            | is_public       | False               |
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    And   the image "qatesting01" is not synchronized
    And   the image "qatesting01" is not present in target nodes


  Scenario: Images with the same name are not sync again by default
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   other new image created in the Glance of master node with name "qatesting01"
    When  I sync images
    Then  no images are synchronized
    And   the image "qatesting01" is present in all nodes with the expected data


  @skip @bug @CLAUDIA-5188
  Scenario: Sync two images with the same name uploaded to master node
    Given the following images created in the Glance of master node with name:
          | image_name  |
          | qatesting01 |
          | qatesting01 |
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  the image "qatesting01" is synchronized
    And   a warning message is shown informing about images with the same name "qatesting01"
    And   the image "qatesting01" is present in all nodes with the expected data


  @skip @bug @CLAUDIA-5189
  Scenario: Sync an image with the same name that have changed its content (differente checksum)
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    And   already synchronized images
    And   the image "qatesting01" is deleted from the Glance of master node
    And   other new image created in the Glance of master node with name "qatesting01" and file "qatesting01b"
    When  I sync images
    Then  no images are synchronized
    And   a warning message is shown informing about checksum conflict with "qatesting01"


  Scenario: Sync an image when exists more than one image with the same name in target node
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of all target nodes with name "qatesting01"
    And   a new image created in the Glance of all target nodes with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  a warning message is shown informing about image duplicity for "qatesting01"


  @env_dependant @experimentation
  Scenario: Sync an image in a specific node given by params.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images on "Burgos"
    Then  the image "qatesting01" is synchronized
    And   the image "qatesting01" is only present in target node "Burgos"


  Scenario: Sync an image when it has got a non-final status in some target nodes.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of all target nodes with name "qatesting01" and without upload an image file
    And   GlanceSync configured to sync images without specifying any condition
    When  I sync images
    Then  the image "qatesting01" is synchronized
    And   a warning message is shown informing about not active status in the image "qatesting01"
