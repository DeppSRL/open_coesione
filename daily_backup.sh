#!/bin/bash

# data di oggi
DATE_TAG=`date +%Y%m%d`

# bucket s3 con i backup
BUCKET_NAME=open_coesione

# comando s3
S3CMD="/usr/bin/s3cmd -c /root/.s3cfg"

# logs
BACKUPS_ROOT_DIR=/home/backups

# parametri database
DB_NAME=open_coesione
DB_USER=oc_db

# path dati solr
SOLR_DATA_PATH="/home/solr/data"


#
# comandi
#

# creazione path del backup
BACKUP_DIR=${BACKUP_ROOT_DIR}/${DATE_TAG}
if [[ ! -d "${BACKUP_DIR}/${DATE_TAG}" ]]; then mkdir -p ${BACKUP_DIR}/${DATE_TAG}; fi
pushd ${BACKUP_DIR}

# creazione, invio e rimozione del dump del DB
echo `date +"%Y.%h.%d %H:%M:%S"` dump del database ${DB_NAME}
pg_dump -U${DB_USER} ${DB_NAME} > ${BACKUP_DIR}/dump.sql
gzip ${BACKUP_DIR}/dump.sql  2>&1

echo `date +"%Y.%h.%d %H:%M:%S"` spostamento del dump su s3://${BUCKET_NAME}/${DATE_TAG}
$S3CMD put -f ${BACKUP_DIR}/dump.sql.gz s3://${BUCKET_NAME}/daily/${DATE_TAG}/

echo `date +"%Y.%h.%d %H:%M:%S"` rimozione del dump locale ${BACKUP_DIR}/dump.sql.gz
rm -f ${BACKUP_DIR}/dump.sql.gz


# creazione, invio e rimozione dump SOLR
pushd $SOLR_DATA_PATH
tar cvzf solr.tgz open_coesione/*

$S3CMD put solr.tgz s3://${BUCKET_NAME}/daily/${DATE_TAG}/ 2>&1
rm -f solr.tgz
popd


 
echo `date +"%Y.%h.%d %H:%M:%S"` backup mensile 2>&1
MONTHLY_BUCKET=${BUCKET_NAME}/monthly
DAY=`date +%d`
if [[ $DAY = 01 ]]; then
  echo `date +"%Y.%h.%d %H:%M:%S"` copia del dump mensile su s3://${MONTHLY_BUCKET}
  $S3CMD cp s3://${BUCKET_NAME}/daily/${DATE_TAG}/dump.sql.gz ${MONTHLY_BUCKET}/  2>&1
  $S3CMD cp s3://${BUCKET_NAME}/daily/${DATE_TAG}/solr.gz ${MONTHLY_BUCKET}/ 2>&1
fi

# rimuove i backup piu' vecchi di una settimana (tranne dentro monthly)
# TODO in python

popd

echo `date +"%Y.%h.%d %H:%M:%S"` operazione completata
