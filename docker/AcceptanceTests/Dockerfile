FROM centos
RUN yum install -y epel-release
RUN yum update -y 
RUN yum install -y crudini gcc libffi-devel  openssl-devel git gcc build-essentials python-devel python-pip
RUN mkdir /opt/fiware
RUN git clone https://github.com/telefonicaid/fiware-glancesync/ /opt/fiware/glancesync/
RUN mkdir /opt/fiware; mkdir /etc/fiware.d/; mkdir /etc/fiware.d/etc/
ENV GLANCESYNC_SETTINGS_FILE=/etc/fiware.d/etc/fiware-glancesync.cfg
ENV GLANCESYNC_LOGGING_SETTINGS_FILE=/etc/fiware.d/etc/fiware-glancesync-logging.cfg
COPY fiware-glancesync.cfg /etc/fiware.d/etc/fiware-glancesync.cfg
COPY fiware-glancesync-logging.cfg /etc/fiware.d/etc/fiware-glancesync-logging.cfg
RUN pip install --upgrade pip
WORKDIR /opt/fiware/glancesync
RUN pip install  -r requirements.txt
RUN python setup.py install
WORKDIR /opt/fiware/glancesync/tests/acceptance/
COPY settings.json conf/settings.json
RUN pip install -r requirements.txt
RUN pip install docopt
COPY glancesync.conf /etc/glancesync.conf
RUN pip install python-openstackclient
COPY start_acceptance.sh start.sh
CMD ./start.sh

