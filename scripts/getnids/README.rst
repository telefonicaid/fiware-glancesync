GlanceSync - How to obtain the NID of the different Generic Enabler
*******************************************************************


Overview
========

The file *getnit.py* is used to recover all the Generic Enablers with their corresponding NID
from the `FIWARE Catalogue`_. NID value is the unique identifier assigned to each Generic Enabler
in order to identify any instance in production. It is implemented in a specific class NID
that could be called to recover the information in any other python code. In the same way,
there is implemented a specific Command-line Interface to execute the process. You can execute:

The result obtained in the execution of the script, specially with the --wikitext option activated,
will be used to generate the corresponding `FIWARE GE identification page`_.

.. code::

     $ ./getnid.py -h

To see the help information about the use of this script, like the following:

.. code::
     Get the NID of the different GE(r)i.

     Usage:
       getnid [--wikitext]
       getnid --type (i2nd | cloud | ui | sec | iot | data | apps)
       getnid -h | --help
       getnid -v | --version

     Options:
       -h --help     Show this screen.
       -v --version  Show version.
       --wikitext    Generate content in Wiki Markup format.
       --type        Show details about the specific chapter

The type value corresponding to each of the chapter that we have in FIWARE and are the following:

- i2nd: `Advanced Middleware and Interfaces Network and Devices`_.
- cloud: `Cloud Hosting`_.
- ui: `Advanced Web-based User Interface`_.
- sec: `Security`_.
- iot: `Internet of Things (Io) Services Enablement`_.
- data: `Data/Context Management`_.
- apps: `Architecture of Applications/Services Ecosystem and Delivery Framework`_.


License
=======

The scripts are licensed under Apache v2.0 license.

.. REFERENCES

.. _FIWARE Catalogue: http://catalogue.fiware.org/
.. _Advanced Middleware and Interfaces Network and Devices: http://catalogue.fiware.org/chapter/advanced-middleware-and-interfaces-network-and-devices
.. _Cloud Hosting: http://catalogue.fiware.org/chapter/cloud-hosting
.. _Advanced Web-based User Interface: http://catalogue.fiware.org/chapter/advanced-web-based-user-interface
.. _Security: http://catalogue.fiware.org/chapter/security
.. _Internet of Things (Io) Services Enablement: http://catalogue.fiware.org/chapter/internet-things-services-enablement
.. _Data/Context Management: http://catalogue.fiware.org/chapter/datacontext-management
.. _Architecture of Applications/Services Ecosystem and Delivery Framework: http://catalogue.fiware.org/chapter/applicationsservices-and-data-delivery
.. _FIWARE GE identification page_: https://forge.fiware.org/plugins/mediawiki/wiki/fiware/index.php/GE-identification