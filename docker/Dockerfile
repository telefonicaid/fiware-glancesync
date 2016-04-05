FROM centos
RUN yum install -y epel-release
RUN yum update -y 
RUN yum install -y crudini gcc libffi-devel  openssl-devel git gcc build-essentials python-devel python-pip
RUN mkdir /opt/fiware
RUN git clone https://github.com/telefonicaid/fiware-glancesync/ /opt/fiware/glancesync/
WORKDIR /opt/fiware/glancesync/
RUN sed -i -e "s/six==1.8.0/six/" requirements.txt
RUN pip install -r requirements.txt
RUN pip install -r scripts/getnids/requirements.txt
RUN pip install behave
RUN mkdir /etc/fiware.d/
RUN mkdir /etc/fiware.d/etc/
COPY fiware-glancesync.cfg /etc/fiware.d/etc/fiware-glancesync.cfg
COPY fiware-glancesync-logging.cfg /etc/fiware.d/etc/fiware-glancesync-logging.cfg
ENV GLANCESYNC_SETTINGS_FILE=/etc/fiware.d/etc/fiware-glancesync.cfg
ENV GLANCESYNC_LOGGING_SETTINGS_FILE=/etc/fiware.d/etc/fiware-glancesync-logging.cfg
RUN python setup.py install
WORKDIR /opt/fiware/glancesync/tests/acceptance/
COPY settings.json conf/settings.json
RUN pip install -r requirements.txt
COPY glancesync.conf /etc/glancesync.conf
RUN useradd -p glancesync glancesync
RUN mkdir /home/glancesync/.ssh
RUN mkdir /root/.ssh
RUN chmod 700 /home/glancesync/.ssh
RUN chmod 700 /root/.ssh
RUN ssh-keygen -q -t rsa -N '' -f /home/glancesync/.ssh/id_rsa
RUN cp /home/glancesync/.ssh/* /root/.ssh

COPY start.sh .
CMD ./start.sh

