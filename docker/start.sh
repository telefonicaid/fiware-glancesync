sed -i -e "s/{ADM_TENANT_NAME}/${ADM_TENANT_NAME}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_PASSWORD}/${ADM_PASSWORD}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_TENANT_ID}/${ADM_TENANT_ID}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_USERNAME}/${ADM_USERNAME}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{Region1}/${Region1}/" /etc/glancesync.conf

cp /usr/glancesync.conf /etc/glancesync.conf
export GLANCESYNCAPP_DATABASE_PATH=/usr/lib/python2.7/site-packages/fiwareglancesync/
export GLANCESYNCAPP_CONFIG=$GLANCESYNCAPP_DATABASE_PATH/app/config.py
export PYTHONPATH=../..
run.py db init;run.py db migrate;run.py db upgrade
run.py runserver
