This procedure describes how to install an open_coesione environment,
using Vagrant + Ansible, on your laptop (or desktop) PC.

Prerequisites
=============

As a prerequisite, you need to have ansible installed as a global package,
and correctly configured on your machine, in order to locate the
depp-ansible roles.

.. code::

    # ansible installation
    sudo pip install ansible

    # clone depp-ansible repository from gitlab
    pushd ~/Workspace
    git clone ssh://git@gitlab.equi.openpolis.it:9822/eraclitux/ansible.git depp-ansible

    # configure ansible, to use depp-ansible repository
    car > ~/.ansible.cfg < EOF
    [defaults]
    roles_path = ~/Workspace/depp-ansible/playbooks/roles
    nocows = 1
    remote_user = vagrant
    private_key_file = ~/.vagrant.d/insecure_private_key
    host_key_checking = False
    EOF


VM Installation
===============

A vagrant machine is launched and provisioned with all OS packages and
python packages needed to properly run the django app and all needed services
in the virtual machine, leaving the source code in the host.

.. code::

    cd ~/Workspace/open-coesione
    vagrant up
    ansible-playbook -i inventory/vagrant playbook/vagrant.yml



At this point, data from the backup area may be downloaded and added to
postgres, redis, solr and the media materials.
Of course you need the proper permissions to access the S3 area,
in order to do that.

.. code::
    DATE=20151101
    pushd ~/Workspace/open-coesione/dati
    s3cmd get --recursive s3://open_coesione/daily/$DATE .
    popd

Access the VM, in order to complete data transfer


.. code::
    vagrant ssh

Once there, source code and data are under the /vagrant path,
which is shared with the project path.

.. code::
    DATE=20151101
    pushd /vagrant/dati/$DATE

    # postgres
    createdb -Upostgres open_coesione
    psql -Upostgres open_coesione -c "create extension postgis;"
    psql -Upostgres open_coesione -c "create extension postgis_topology;"
    gunzip pg_dump.gz
    psql -Upostgres open_coesione < pg_dump

    # redis
    gunzip $DATE/pg_dump.gz
    sudo service redis-server stop
    sudo mv redis_dump.rdb /var/lib/redis/dump.rdb
    sudo service redis-server start

    # solr
    sudo service solr stop
    sudo mv /var/solr/conf/schema.xml /var/solr/conf/schema_original.xml
    sudo ln -s /vagrant/config/solr/schema.xml /var/solr/conf/
    sudo rm -rf /var/solr/data
    cd /var
    sudo tar xvzf /vagrant/data/$DATE/solr_dump.tgz
    sudo chown -R solr:solr solr/data
    cd solr/
    sudo mv data/open_coesione/* data/
    sudo rm -rf data/open_coesione/
    sudo service solr start

    popd

    python manage.py runserver 0.0.0.0:80


Now, open http://localhost:8000 in your browser!
