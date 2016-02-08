FROM centos
RUN yum install -y epel-release
RUN yum update -y 
RUN yum install -y gcc python-devel python-pip
RUN pip install fiware-glancesync
CMD sync.py
