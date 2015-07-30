#!/bin/bash

cd $(dirname $0)/..
install -d target/site/cobertura
install -d target/surefire-reports
PROJECT=$(pwd)
export PYTHONPATH=$PROJECT
cd tests/unit
#python -m unittest discover
nosetests --exe --with-coverage --cover-package=glancesync,glancesync_ami,glancesync_config,glancesync_image,glancesync_region,glancesync_serversfacade --cover-xml --cover-xml-file=$PROJECT/target/site/cobertura/coverage.xml --with-xunit --xunit-file=$PROJECT/target/surefire-reports/TEST-nosetest.xml
