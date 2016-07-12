yum install sudo
ls -l /var/lib
ls -l /var/lib/glance
chmod 777 /var/lib/glance/images
echo hola >> /var/lib/glance/images/hola
cat /var/lib/glance/images/hola
export OS_REGION_NAME=$Region1
export  OS_USERNAME=$ADM_USERNAME
export OS_PASSWORD=$ADM_PASSWORD
export OS_TENANT_NAME=$ADM_TENANT_NAME
export  OS_AUTH_URL=http://$KEYSTONE_IP:5000/v3
export OS_AUTH_URL_V2=http://$KEYSTONE_IP:5000/v2.0/
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_NAME=Default
export OS_IDENTITY_API_VERSION=3

sed -i -e "s/{ADM_TENANT_NAME}/${ADM_TENANT_NAME}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_PASSWORD}/${ADM_PASSWORD}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{KEYSTONE_IP}/${KEYSTONE_IP}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_TENANT_ID}/${ADM_TENANT_ID}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{ADM_USERNAME}/${ADM_USERNAME}/" /etc/fiware.d/etc/fiware-glancesync.cfg
sed -i -e "s/{Region1}/${Region1}/" /etc/glancesync.conf

export GLANCESYNCAPP_DATABASE_PATH=/usr/lib/python2.7/site-packages/fiwareglancesync/
export GLANCESYNCAPP_CONFIG=$GLANCESYNCAPP_DATABASE_PATH/app/config.py
export PYTHONPATH=../..
run.py db init;run.py db migrate;run.py db upgrade
run.py runserver
