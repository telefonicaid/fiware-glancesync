=============================================
FIWARE | GLANCESYNC | Acceptance test project
=============================================

This project contains the GlanceSync acceptance tests (component, integration and E2E testing).
All test cases have been defined using Gherkin that it is a Business Readable, Domain Specific Language that lets you
describe software’s behaviour without detailing how that behaviour is implemented.
Gherkin has the purpose of serving documentation of test cases.


Test case implementation has been performed using `Python <http://www.python.org/>`_ and the BDD framework
`Behave <http://pythonhosted.org/behave/>`_.

Acceptance Project Structure
----------------------------
 :: 
 
    ├───acceptance
    │   ├───commons
    │   ├───features
    │   │   ├───steps
    │   │   │   ├───synchronization.py
    │   │   │   └───...
    │   │   ├───environment.py
    │   │   ├───synchronization_image.feature
    │   │   └───...
    │   ├───resources
    │   │   ├───settings.json
    │   │   └───images
    │   │       └───...
    │   ├───qautils
    │   └───glancesync
    │


FIWARE GlanceSync Automation Framework
--------------------------------------

Features:

- Behave support
- Settings using json files
- Test report using xUnit output and Behave output
- Assertions using Hamcrest (declaratively define "match" rules)
- GlanceSync Client
- Glance adapter (operations manager)
- Logging
- Remote GlanceSync execution


Acceptance test execution
-------------------------

Execute the following command in the test project root directory:

::

  $> cd $GLANCESYNC_HOME/tests/acceptance
  $> behave features/ --tags ~@skip

With this command, you will execute:

- Test Cases in the environment configured in `resources/settings.json`
- all *.features implemented
- Skipping all Scenarios tagged with "skip"

For more options, execute *behave --help*

**Prerequisites**

- Python 2.7 or newer (2.x) (https://www.python.org/downloads/)
- pip (https://pypi.python.org/pypi/pip)
- virtualenv (https://pypi.python.org/pypi/virtualenv)
- GlanceSync (https://pdihub.hi.inet/fiware/fiware-glancesync/)

**Test case execution using virtualenv**

1. Create a virtual environment somewhere *(virtualenv $WORKON_HOME/venv)*
#. Activate the virtual environment *(source $WORKON_HOME/venv/bin/activate)*
#. Go to *$GLANCESYNC_HOME/tests/acceptance* folder in the project
#. Install the requirements for the acceptance tests in the virtual environment *(pip install -r requirements.txt --allow-all-external)*

**Test case execution using Vagrant (optional)**

Instead of using virtualenv, you can use the provided Vagrantfile to deploy a local VM using `Vagrant <https://www.vagrantup.com/>`_,
that will provide all environment configurations for launching test cases.

1. Download and install Vagrant (https://www.vagrantup.com/downloads.html)
#. Go to *ngsi_adapter/src/test/acceptance* folder in the project
#. Execute *vagrant up* to launch a VM based on Vagrantfile provided.
#. After Vagrant provision, your VM is properly configured to launch acceptance tests. You have to access to the VM using *vagrant ssh* and change to */vagrant* directory that will have mounted your workspace *(test/acceptance)*.

If you need more information about how to use Vagrant, you can see
`Vagrant Getting Started <https://docs.vagrantup.com/v2/getting-started/index.html>`_

**Settings**

Before executing the acceptance tests, you will need configure the properties file. To execute acceptance test on the
experimentation environment, you will have to configured the file `resources/settings.json` properly:

- You will have to configure two nodes in the same federation (same IdM/Keystone) at least.
- For multi-target testing, you will have to configure two nodes in the same federation and another one in other federation.


You will need a valid private key (*host_key*) to connect to master node by SSH (remote GlanceSync execution)
and a valid OpenStack credentials for E2E validation against Glance servers on each node.


Configuration parameters (settings):

- **credential_type**: Type of the credentials configured in the section (base_admin, host, secondary_admin):

  - base_admin: The credentials defined in the section are relative to the GlanceSync user on each Glance server (the same as the configured in glancesync.conf)
  - host: The credentials defined in the section have got host information for SSH connections.
  - secondary_admin: The credentials defined in the section are relative to a secondary admin user to be used in some test cases. Different from configured GlanceSync user

- **federation_name**: Name of the federation (nodes under the same keystone). To group credentials.
- **region_name**: Name of the region
- **keystone_url**: Keystone URL
- **tenant_id**: Tenant ID
- **tenant_name**: Tenant Name
- **user_domain_name**: Domain Name for the user (Keystone v3)
- **user**: Username
- **password**: User password
- **host_name**: Name of the host (to be used as part as a ssh connection)
- **host_user**: User name of the host
- **host_password**: Password for the previous user
- **host_key**: RSA key for ssh connections instead of previous user/password. If protected, _host_password_ should be set with the correct value to decrypt
