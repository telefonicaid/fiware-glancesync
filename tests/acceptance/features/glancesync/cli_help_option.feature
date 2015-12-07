# -*- coding: utf-8 -*-

Feature: GlanceSync CLI implementation of basic operations: help.

  As a sys-admin user,
  I want to see the GlanceSync CLI help info
  so that I can know what to do with this tool.

  Scenario Outline: GlanceSync CLI: Help command.
    Given the GlanceSync command line interface is installed
    When  I run the sync command with options <help_option>
    Then  I can see the command usage:
      """
      usage: sync.py [-h] [--parallel] [--config CONFIG [CONFIG ...]]
               [--dry-run | --show-status | --show-regions | --make-backup]
               [region [region ...]]
      """
    And   I can see the help of the tool:
      """
      A tool to sync images from a master region to other regions

      positional arguments:
        region                region where the images are uploaded to

      optional arguments:
        -h, --help            show this help message and exit
        --parallel            sync several regions in parallel
        --config CONFIG [CONFIG ...]
                              override configuration options. (e.g.
                              main.master_region=Valladolid
                              metadata_condition='image.name=name1')
        --dry-run             do not upload actually the images
        --show-status         do not sync, but show the synchronisation status
        --show-regions        don not sync, only show the available regions
        --make-backup         do no sync, make a backup of the regions' metadata
      """

    Examples:
        | help_option |
        | "--help"    |
        | "-h"        |
