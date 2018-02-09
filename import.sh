#!/bin/bash

DATADIR="/home/oc_rilasci/${2}"

TMPFILE=`mktemp`
if wget "${1}" -O ${TMPFILE} && unzip ${TMPFILE} -x / -d ${DATADIR} && rm ${TMPFILE}
then
    for F in progetti soggetti localizzazioni pagamenti
    do
      rm media/open_data/${F}_*.zip
      cp ${DATADIR}/${F}_OC_*.zip media/open_data/
      cp ${DATADIR}/totale/${F}_*.zip media/open_data/
    done

    for F in soggetti localizzazioni
    do
      mv media/open_data/${F}_CIPE.zip media/open_data/${F}_assegnazioni_CIPE.zip
    done

    cp ${DATADIR}/totale/assegnazioni_CIPE.zip media/open_data/progetti_assegnazioni_CIPE.zip

    rm media/open_data/corrispondenze_assegnazioni_progetti_*.csv
    cp ${DATADIR}/corrispondenze_assegnazioni_progetti_*.csv media/open_data/

    rm media/open_data/regione/*.zip
    cp ${DATADIR}/regioni/*.zip media/open_data/regione/

    psql -Upostgres open_coesione -c "TRUNCATE soggetti_soggetto RESTART IDENTITY CASCADE"
    psql -Upostgres open_coesione -c "TRUNCATE progetti_progetto RESTART IDENTITY CASCADE"

    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=progetti
    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=progetti-cipe
    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=soggetti
    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=localizzazioni
    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=pagamenti
    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=privacy-progetti
    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=privacy-soggetti
    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=corrispondenze-progetti
    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=sovrapposizioni-fonti
    python manage.py csvimport --csv-path=${DATADIR} --verbosity=2 --import-type=monitoraggi-asoc
    python manage.py csvremoteimport --csv-file=http://www.ponrec.it/opendata/ponrec_opendata.csv --separator=, --verbosity=2 --import-type=descrizioni-ponrec
    python manage.py csvremoteimport --csv-file=http://www.agenziacoesione.gov.it/opencms/export/sites/dps/it/documentazione/pongat/Beneficiari/Beneficiari_PON_GAT_dati_31_10_2015.csv --encoding=latin1 --verbosity=2 --import-type=descrizioni-pongat
fi
