#!/bin/sh
cd /home/open_coesione
. /home/virtualenvs/open-coesione/bin/activate
python manage.py istatupdate --verbosity=3
deactivate

