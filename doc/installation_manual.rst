Installation
------------

At the moment, Glancesync is designed to run in the glance server of the master region, because it reads the images content directly from disk. This will be fixed in a feature version.

It's not necessary to install the software, after unzipping the package or running 'git clone' the tool is ready to work.

Glancesync works mainly as a front-end to the glance and keystone python tool, therefore they must be installed (note that in Essex OpenStack release, python-glanceclient was named as glance-client):::

   $ apt-get install python-glanceclient python-keystoneclient

Configuration file is optional, but its default location is */etc/glancesync.conf*. Another path may be set with ``GLANCESYNC_CONF`` environment variable.

Security considerations
_______________________

Glancesyncs does not require root access. At this version it requires read-only access to image directory */var/lib/glance/images*

It is strongly recommended:

* creating an account to run glancesync only
* creating a configuration file only readable by the glancesync account. This is because the credentials should not be exposed to other users.
