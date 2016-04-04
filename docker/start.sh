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

pip install virtualenv
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=../..
  
behave features/glancesync/ --tags ~@skip --junit --junit-directory testreport

# Execute Behave features of script components:
behave features/scripts/ --tags ~@skip --junit --junit-directory testreport

# Execute Behave features of API:
behave features/api/ --tags ~@skip --junit --junit-directory testreport
sleep 12000
