#!/bin/sh

pushd /home/open_coesione
. /home/virtualenvs/open_coesione/bin/activate
python manage.py istat_dps_update --collectstatic
deactivate
