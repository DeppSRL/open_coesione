#!/bin/sh
cd /home/open_coesione
. /home/virtualenvs/open-coesione/bin/activate
 python manage.py istatupdate_new --verbosity=2 --collectstatic
deactivate

