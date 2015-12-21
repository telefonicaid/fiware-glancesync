# -*- coding: utf-8 -*-

Feature: Manage tasks to get the status of the synchronization process
         and remove the information related to that process.
  As a GlanceSync API user
  I want to manage task
  So that I can request the status of the sync process and remove all related information.

  GlanceSync API operations:
    GET     /tasks/{task_id}
    DELETE  /tasks/{task_id}

  @happy_path @env_dependant @experimentation
  Scenario: Get task status of the synchornization process.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   I sync the region "Caceres"
    And   a new task is created
    When  I request the status of the related task
    Then  the task information is retrieved


  @happy_path @env_dependant @experimentation @skip # needs a real environment.
  Scenario: Remove task.
    Given a new image created in the Glance of master node with name "qatesting01"
    And   the synchronization is executed in "Caceres"
    When  I remove the task
    Then  the task is deleted
