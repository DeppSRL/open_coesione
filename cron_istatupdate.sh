#!/bin/sh
pushd /home/open_coesione
. /home/virtualenvs/open_coesione/bin/activate
 python manage.py istatupdate_new --verbosity=2 --collectstatic
deactivate
popd

