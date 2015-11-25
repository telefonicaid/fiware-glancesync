# -*- coding: utf-8 -*-

Feature: GlanceSync CLI implementation: Show target regions

  As a sys-admin user,
  I want to list the regions of all configured targets
  so that I can know what regions will be considered in the synchronization process


  Scenario: Configured regions managed by acceptance tests are listed
    Given the GlanceSync command line interface is installed
    When  I run the sync command with options "--show-regions"
    Then  configured regions are listed


  @env_dependant @experimentation
  Scenario: All regions from configured targets in the experimentation environment are listed
    Given the GlanceSync command line interface is installed
    When  I run the sync command with options "--show-regions"
    Then  I can see this list of regions:
          """
          Caceres Burgos federation2:Madrid
          """
