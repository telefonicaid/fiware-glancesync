sed -i -e "s/{ADM_TENANT_NAME}/${ADM_TENANT_NAME}/" conf/settings.json
sed -i -e "s/{ADM_PASSWORD}/${ADM_PASSWORD}/" conf/settings.json
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" conf/settings.json
sed -i -e "s/{ADM_TENANT_ID}/${ADM_TENANT_ID}/" conf/settings.json
sed -i -e "s/{ADM_USERNAME}/${ADM_USERNAME}/" conf/settings.json
sed -i -e "s/{ADM_TENANT_NAME}/${ADM_TENANT_NAME}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_PASSWORD}/${ADM_PASSWORD}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_TENANT_ID}/${ADM_TENANT_ID}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_USERNAME}/${ADM_USERNAME}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{Region1}/${Region1}/" /etc/glancesync.conf
sed -i -e "s/{Region1}/${Region1}/" conf/settings.json
sed -i -e "s/{Region2}/${Region2}/" conf/settings.json
sed -i -e "s/{Region3}/${Region3}/" conf/settings.json

export OS_REGION_NAME=$Region1
export  OS_USERNAME=$ADM_USERNAME
export OS_PASSWORD=$ADM_PASSWORD
export OS_TENANT_NAME=$ADM_TENANT_NAME
export  OS_AUTH_URL=http://$KEYSTONE_IP:5000/v2.0
export PYTHONPATH=../..
sleep 120020
behave features/glancesync/ --tags ~@skip --junit --junit-directory testreport

# Execute Behave features of script components:
behave features/scripts/ --tags ~@skip --junit --junit-directory testreport
# Execute Behave features of API:
behave features/api/ --tags ~@skip --junit --junit-directory testreport
