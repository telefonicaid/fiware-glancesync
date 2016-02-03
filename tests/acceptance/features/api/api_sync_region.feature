# -*- coding: utf-8 -*-

Feature: Synchronize the images of the corresponding region defined by its regionId.
         The operation is asynchronous it responses with a taskId in order that
         you can follow the execution of the process.

  As a GlanceSync API user
  I want to sync images in a region using the GlanceSync API
  So that I can have all FIWARE images up to date in all FIWARE nodes.

  GlanceSync API operation under testing:
    POST regions/regionId


  @happy_path @env_dependant @experimentation @skip # needs a real environment.
  Scenario: Sync all images to the region
    Given a new image created in the Glance of master node with name "qatesting01"
    When  I sync the region "Caceres"
    Then  a new task is created
    And   the task finishes with status "synced"
    And   the image "qatesting01" is only present in target node "Caceres"
