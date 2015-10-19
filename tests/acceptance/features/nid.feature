# -*- coding: utf-8 -*-

Feature: Get the corresponding NID of the different Generic Enablers from the catalogue.

  As a sys-admin user,
  I want to obtain the corresponding NID for each of the Generic Enabler (GE) that are registered in the catalog
  So that each GE image can be assigned its corresponding unique identity number.

  @happy_path
    Scenario Outline:: 01: Get the NID of a specific chapter with no version, help and wikitext parameter
     Given a connectivity to the FIWARE Catalogue
     When  I execute the getnid with the following values
             | type_value      | version | help  | wikitext |
             | <type_value>    | False   | False | False    |
     Then  I obtain the following list of nid corresponding to that chapter
             | chapter_value   | resources_value   |
             | <chapter_value> | <resources_value> |

                Examples:
             | type_value    | chapter_value                                          | resources_value    |
             | i2nd          | advanced-middleware-and-interfaces-network-and-devices | nids-i2nd          |
             | cloud         | cloud-hosting                                          | nids-cloud         |
             | userinterface | advanced-web-based-user-interface                      | nids-userinterface |
             | sec           | security                                               | nids-sec           |
             | iot           | internet-things-services-enablement                    | nids-iot           |
             | data          | datacontext-management                                 | nids-data          |
             | apps          | applicationsservices-and-data-delivery                 | nids-apps          |

  @happy_path
    Scenario Outline:: 02: Get the version of the application by invoking the appropriate command line instruction
     Given that I have the gitnid application installed
     When  I execute the gitnid application with the option
             | option_value   |
             | <option_value> |
     Then  the program return the corresponding version of this implementation
             | result_value   |
             | <result_value> |

                Examples:
             | option_value | result_value        |
             | --version    | Get NID code vx.y.z |
             | -v           | Get NID code vx.y.z |

  @happy_path
    Scenario Outline:: 03: Get the help information of the application by invoking the appropriate command line instruction
     Given that I have the gitnid application installed
     When  I execute the gitnid application with the option
             | option_value   |
             | <option_value> |
     Then  the program return the corresponding help information
             | result_value   |
             | <result_value> |

                Examples:
             | option_value | result_value |
             | --help       | help.info    |
             | -h           | help.info    |