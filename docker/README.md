
# How to use GlanceSync with Docker

There are several options to use GlanceSync very easily using docker. These are (in order of complexity):

- _"Have everything automatically done for me"_. See Section **1. The Fastest Way** (recommended).
- _"Check the unit tests associated to the component"_. See Section **2. Run Unit Test of GlanceSync**.
- _"Check the acceptance tests are running properly"_ or _"I want to check that my GlanceSync instance run properly"_ . See Section **3. Run Acceptance tests**.

You do not need to do all of them, just use the first one if you want to have a fully operational GlanceSync instance and maybe third one to check if your GlanceSync instance run properly.

You need to have docker in your machine. See the [documentation](https://docs.docker.com/installation/) on how to do this. Additionally, you can use the proper FIWARE Lab docker functionality to deploy dockers image there. See the [documentation](https://docs.docker.com/installation/)

----
## 1. The Fastest Way

Docker allows you to deploy an GlanceSync container in a few minutes. This method requires that you have installed docker or can deploy container into the FIWARE Lab (see previous details about it).

Consider this method if you want to try GlanceSync and do not want to bother about losing data.

Follow these steps:

1. Download [GlanceSync' source code](https://github.com/telefonicaid/fiware-glancesync) from GitHub (`git clone https://github.com/telefonicaid/fiware-glancesync.git`)
2. `cd fiware-glancesync/docker`
3. Using the command-line and within the directory you created type: `docker build -t fiware-glancesync -f Dockerfile .`.

After a few seconds you should have your GlanceSync image created. Just run the command `docker images` and you see the following response:

    REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
    fiware-glancesync   latest              e9ffdd94adfe        58 seconds ago      714.4 MB
    centos              latest              50dae1ee8677        6 days ago          196.7 MB
    ...

To execute the GlanceSync image, execute the command `docker run -p 8080:8080 -d fiware-glancesync`. It will launch the GlanceSync service listening on port `8080`.

Check that everything works with

	curl <IP address of a machine>:8080

You can obtain the IP address of the machine just executing `docker-machine ip`. What you have done with this method is the creation of the [GlanceSync](https://hub.docker.com/r/fiware/glancesync/) image from the public repository of images called [Docker Hub](https://hub.docker.com/).

If you want to stop the scenario you have to execute `docker ps` and you see something like this:

    CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
    36af661ae2c6        fiware-glancesync   "/bin/sh -c ./start.s"   2 minutes ago       Up 2 minutes        0.0.0.0:8080->8080/tcp   pensive_jang


Take the Container ID and execute `docker stop 36af661ae2c6` or `docker kill 36af661ae2c6`. Note that you will lose any data that was being used in GlanceSync using this method.

----
## 2. Run Unit Test of GlanceSync

Taking into account that you download the repository from GitHub (See Section **1. The Fastest Way**), this method will launch a container running GlanceSync, and execute the unit tests associated to the component. You should move to the UnitTests folder `./UnitTests`. Just create a new docker image executing `docker build -t fiware-glancesync-unittests -f Dockerfile .`. Please keep in mind that if you do not change the name of the image it will automatically create a new one for unit tests and change the previous one to tag none.

To see that the image is created run `docker images` and you see something like this:

    REPOSITORY                    TAG                 IMAGE ID            CREATED             SIZE
    fiware-glancesync-unittests   latest              e9ffdd94adfe        2 minutes ago       714.4 MB
    centos                        latest              904d6c400333        2 weeks ago         196.8 MB

To execute the unit tests of this component, just execute `docker run --name fiware-glancesync-unittests fiware-glancesync-unittests`. Finally you can extract the information of the executed tests just executing `docker cp fiware-glancesync-unittests:/opt/fiware/glancesync/test_results .`


> TIP: If you are trying these methods or run them more than once and come across an error saying that the container already exists you can delete it with `docker rm fiware-glancesync-unittests`. If you have to stop it first do `docker stop fiware-glancesync-unittests`.

Keep in mind that if you use these commands you get access to the tags and specific versions of GlanceSync. If you do not specify a version you are pulling from `latest` by default.

----
## 3. Run Acceptance tests

Taking into account that you download the repository from GitHub (See Section **1. The Fastest Way**). This method will launch a container to run the E2E tests of the GlanceSync component, previously you should launch or configure a FIWARE Lab access. You have to define the following environment variables:

    export BRANCH=develop
    export KEYSTONE_IP=<IP of the keystone instance>
    export ADM_TENANT_ID=<admin tenant id in the OpenStack environment>
    export USER_TENANT_ID=<admin tenant id in the OpenStack environment>
    export ADM_TENANT_NAME=<admin tenant name>
    export USER_TENANT_NAME=<user tenant name>
    export ADM_USERNAME=<admin username>
    export USER_USERNAME=<username>
    export ADM_PASSWORD=<admin password>
    export USER_PASSWORD=<user password>
    export Region1=<region name 1>
    export Region2=<region name 2>
    export Region3=<region name 3>
    export KEYSTONE_IP2=<IP of the keystone instance 2>
    export OS_USER_DOMAIN_NAME=<OpenStack user domain name>
    export OS_PROJECT_DOMAIN_NAME=<OpenStack project domain name>	

Take it, You should move to the UnitTests folder `./AcceptanceTests`. Just create a new docker image executing `docker build -t fiware-glancesync-acceptance .`. To see that the image is created run `docker images` and you see something like this:

    REPOSITORY                     TAG                 IMAGE ID            CREATED             SIZE
    fiware-glancesync-acceptance   latest              844ba0241502        40 seconds ago      807.3 MB
    fiware-glancesync              latest              5a4ef7a160e4        38 seconds ago      715.3 MB
    centos                         latest              50dae1ee8677        7 days ago          196.7 MB
    ...

Now is time to execute the container. This time, we take advantage of the docker compose. Just execute `docker-compose up` to launch the architecture. You can take a look to the log generated executing `docker-compose logs`. If you want to get the result of the acceptance tests, just execute `docker cp acceptancetests_fiwareglancesync-acceptance_1:/opt/fiware/glancesync/tests/acceptance/testreport .`

Please keep in mind that if you do not change the name of the image it will automatically create a new one for unit tests and change the previous one to tag none.

> TIP: you can launch a FIWARE Lab testbed container to execute the GlanceSync E2E test. Just follow the indications in [FIWARE Testbed Deploy](https://hub.docker.com/r/fiware/testbed-deploy/). It will launch a virtual machine in which a reproduction of the FIWARE Lab is installed.

----
## 4. Other info

Things to keep in mind while working with docker containers and GlanceSync.

### 4.1 Data persistence
Everything you do with GlanceSync when dockerized is non-persistent. *You will lose all your data* if you turn off the GlanceSync container. This will happen with either method presented in this README.

### 4.2 Using `sudo`

If you do not want to have to use `sudo` follow [these instructions](http://askubuntu.com/questions/477551/how-can-i-use-docker-without-sudo).
   