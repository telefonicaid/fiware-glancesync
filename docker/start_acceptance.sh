export OS_REGION_NAME=$Region1
export OS_USERNAME=$ADM_USERNAME
export OS_PASSWORD=$ADM_PASSWORD
export OS_TENANT_NAME=$ADM_TENANT_NAME
export OS_AUTH_URL=http://$KEYSTONE_IP:5000/v3
export OS_AUTH_URL_V2=http://$KEYSTONE_IP:5000/v2.0/
export OS_IDENTITY_API_VERSION=3

openstack project create qa
openstack user create qa --password qa --project qa

openstack project show qa > qa

export TENANT_ID_QA=`grep "| id" qa | awk 'NR==1{print $4}'`

export OS_REGION_NAME=$Region3
export OS_USERNAME=$ADM_USERNAME
export OS_PASSWORD=$ADM_PASSWORD
export OS_TENANT_NAME=$ADM_TENANT_NAME
export OS_AUTH_URL=http://$KEYSTONE_IP2:5000/v3
export OS_AUTH_URL_V2=http://$KEYSTONE_IP2:5000/v2.0/
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
sed -i -e "s/{Region1}/${Region1}/" /etc/glancesync.conf
sed -i -e "s/{Region1}/${Region1}/" conf/settings.json
sed -i -e "s/{Region2}/${Region2}/" conf/settings.json
sed -i -e "s/{Region3}/${Region3}/" conf/settings.json
export PYTHONPATH=../..
behave features/glancesync/ --tags ~@skip --junit --junit-directory testreport
# Execute Behave features of script components:
behave features/scripts/ --tags ~@skip --junit --junit-directory testreport
# Execute Behave features of API:
behave features/api/ --tags ~@skip --junit --junit-directory testreport
