# GlanceSync - Glance Synchronization Component

This is the code repository for the GlanceSync component, the FIWARE Ops tool used to sincronize the glance images in the different Glance servers connected in the FIWARE Lab.

This project is part of [FIWARE](http://www.fiware.org).

Any feedback on this documentation is highly welcome, including bugs, typos
or things you think should be included but are not. You can use [github issues](https://github.com/telefonicaid/fiware-glancesync/issues/new) to provide feedback.

## Overall description

GlanceSync is a python ....

## Build and Install

The recommended procedure is to install using ...

### Requirements


### Installation

#### Using pip (recommended)

#### Optional packages

## Running

Once installed, there is a way to run GlanceSync manually from the command line ...

### Configuration file

The configuration used by the GlanceSync component is stored in the
<directory>glancesync.conf file, which typical content is:

    # master_region - Region where are the images in the "master" target that are synchronized to
    # the other regions of "master" regions and/or to regions in other targets.
    master_region = Spain
    
    # preferable_order - A sorted list of regions. Regions that are not present are silently
    # ignored. Synchronization is done also to the other regions, but first this list is
    # revised and then the Regions are prefixed with target: This parameter is not used when 
    # target is master.
    preferable_order = Trento, Lannion, Waterford, Berlin, Prague
    
### Checking status

In order to check the status of the GlanceSync, use the following command:

## Testing

### Ent-to-end tests

The acceptance tests can be executed in the following way:

<<<<....>>>>>

Please have a look to the section ... in order to get more information about how to prepare the environment to run the functional_test target.

### Unit tets

The unit_test ...:

    .....

Please have a look to the section ... in order to get more information about how to prepare the environment to run the unit_test target.

## Advanced topics:

* Installation and administration
  * [Building from sources](doc/manuals/admin/build_source.md)
  * [Running GlanceSync from command line](doc/manuals/admin/cli.md)
  * [Logs](doc/manuals/admin/logs.md)
  * [Resources & I/O Flows](doc/manuals/admin/resources.md)
  * [Problem diagnosis procedures](doc/manuals/admin/diagnosis.md)
* Container-based deployment
  * [Vagrant](doc/manuals/vagrant.md)
  * [Sample code contributions](doc/manuals/code_contributions.md)

## License

GlanceSync is licensed under Apache v2.0 license.