# -*- coding: utf-8 -*-

Feature: Get information about GlanceSync API
  As a GlanceSync API user
  I want to see some information of the API that is running
  So that I can check the version, owner, documentation location and other info parameters.

  GlanceSync API operations:
    GET /


  Scenario: Request API information when user is authenticate.
    Given the API running properly
    And   the user is successfully authenticated
    When  I request the API version
    Then  the request finishes with status HTTP "200" OK
    And   I receive the API information with these attributes:
           | attribute_name | value          |
           | id             | [NOT_EMPTY]    |
           | owner          | Telefonica I+D |
           | status         | SUPPORTED      |
           | version        | [NOT_EMPTY]    |
           | updated        | [NOT_EMPTY]    |
           | runningfrom    | [NOT_EMPTY]    |
           | href           | [NOT_EMPTY]    |


  Scenario Outline: Request API information when user is not authenticated (invalid/empty/missing X-Auth-Token).
    Given the API running properly
    And   the X-Auth-Token "<token>"
    When  I request the API version
    Then  the request finishes with status HTTP "200" OK
    And   I receive the API information with these attributes:
           | attribute_name | value          |
           | id             | [NOT_EMPTY]    |
           | owner          | Telefonica I+D |
           | status         | SUPPORTED      |
           | version        | [NOT_EMPTY]    |
           | updated        | [NOT_EMPTY]    |
           | runningfrom    | [NOT_EMPTY]    |
           | href           | [NOT_EMPTY]    |

    Examples:
      | token           |
      | [MISSING_PARAM] |
      |                 |
      | abcde-fgh       |


  @skip # GlanceSync Mock is not returning the body as JSON format.
  Scenario Outline: Request API information with invalid HTTP operations.
    Given the API running properly
    When  I send a HTTP "<verb>" request to the API version resource
    Then  the request finishes with status HTTP "405" Method not allowed
    And   I receive an error response with these data:
           | attribute_name | value      |
           | message        | Bad method |
           | code           | 405        |

    Examples:
      | verb   |
      | post   |
      | put    |
      | delete |
