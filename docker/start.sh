export OS_REGION_NAME=$Region1
export OS_USERNAME=$ADM_USERNAME
export OS_PASSWORD=$ADM_PASSWORD
export OS_TENANT_NAME=$ADM_TENANT_NAME
export OS_AUTH_URL=http://$KEYSTONE_IP:5000/v3
export OS_AUTH_URL_V2=http://$KEYSTONE_IP:5000/v2.0/
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=3

openstack project show qa > qa

export TENANT_ID_QA=`grep "| id" qa | awk 'NR==1{print $4}'`

export OS_REGION_NAME=$Region3
export OS_USERNAME=$ADM_USERNAME
export OS_PASSWORD=$ADM_PASSWORD
export OS_TENANT_NAME=$ADM_TENANT_NAME
export OS_AUTH_URL=http://$KEYSTONE_IP2:5000/v3
export OS_AUTH_URL_V2=http://$KEYSTONE_IP2:5000/v2.0/
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=3

openstack project show qa > qa

export TENANT_ID_QA2=`grep "| id" qa | awk 'NR==1{print $4}'`

sed -i -e "s/{ADM_TENANT_NAME}/${ADM_TENANT_NAME}/" conf/settings.json
sed -i -e "s/{ADM_PASSWORD}/${ADM_PASSWORD}/" conf/settings.json
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" conf/settings.json
sed -i -e "s/{KEYSTONE_IP2}/${KEYSTONE_IP2}/" conf/settings.json
sed -i -e "s/{ADM_TENANT_ID}/${ADM_TENANT_ID}/" conf/settings.json
sed -i -e "s/{ADM_USERNAME}/${ADM_USERNAME}/" conf/settings.json
sed -i -e "s/{TENANT_ID_QA}/${TENANT_ID_QA}/" conf/settings.json
sed -i -e "s/{TENANT_ID_QA2}/${TENANT_ID_QA2}/" conf/settings.json
sed -i -e "s/{ADM_TENANT_NAME}/${ADM_TENANT_NAME}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_PASSWORD}/${ADM_PASSWORD}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_TENANT_ID}/${ADM_TENANT_ID}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_USERNAME}/${ADM_USERNAME}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{Region1}/${Region1}/" /etc/glancesync.conf
sed -i -e "s/{Region1}/${Region1}/" conf/settings.json
sed -i -e "s/{Region2}/${Region2}/" conf/settings.json
sed -i -e "s/{Region3}/${Region3}/" conf/settings.json


export PYTHONPATH=../..
behave features/glancesync/ --tags ~@skip --junit --junit-directory testreport

# Execute Behave features of script components:
behave features/scripts/ --tags ~@skip --junit --junit-directory testreport

# Start glancesync API server:

cd /opt/fiware/glancesync/fiwareglancesync
export GLANCESYNCAPP_DATABASE_PATH=$PWD
export GLANCESYNCAPP_CONFIG=$PWD/app/config.py
python run.py db init;python run.py db migrate;python run.py db upgrade
python run.py runserver&
cd /opt/fiware/glancesync/tests/acceptance
# Execute Behave features of API:
behave features/api/ --tags ~@skip --junit --junit-directory testreport
