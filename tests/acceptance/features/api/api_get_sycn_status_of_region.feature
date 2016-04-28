# -*- coding: utf-8 -*-

Feature: Lists information about the status of the synchronization of the images in a region.
  As a GlanceSync API user
  I want to ask for the status of the synchronization
  So that I can check for each image if it has been synchronized or not.

  GlanceSync API operations:
    GET /regions/regionId?image=imageName


  @happy_path @env_dependant @experimentation # needs a real environment.
  Scenario: Get all synchronized images.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   a new image created in the Glance of master node with name "qatesting02"
    And   GlanceSync configured to sync images without specifying any condition
    And   the synchronization is executed in "Caceres"
    When  I request the status of the image synchronization
    Then  I get the status of all images
    And   I remove the task
