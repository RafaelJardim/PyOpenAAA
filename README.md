# PyOpenAAA

Pre-requirements

* python3.x
* pip3
* mysql-server
* nginx
* libmysqlclient-dev
* unzip

apt-get install python3 python3-pip mysql-server nginx libmysqlclient-dev unzip

As root user

    cd /usr/src/

    wget http://www.pro-bono-publico.de/projects/src/DEVEL.201606121104.tar.bz2

    bzip2 -d DEVEL.201606121104.tar.bz2

    tar xf DEVEL.201606121104.tar

    cd PROJECTS

    ./configure tac_plus

     make

     make install

    wget https://github.com/RafaelJardim/PyOpenAAA/archive/master.zip

    unzip -a master.zip

    mkdir -p /opt/django/pyopenaaa

    mv PyOpenAAA-master/* /opt/django/pyopenaaa/

    chown -R APP_USER /opt/django/pyopenaaa

    cd /opt/django/pyopenaaa/MISC

    cp  django_nginx.config /etc/nginx/sites-available/

    rm /etc/nginx/sites-enabled/default

    ln -s /etc/nginx/sites-available/django_nginx.config /etc/nginx/sites-enabled/django

    service nginx restart

    pip3 install virtualenv

As application user

    virtualenv /opt/django/pyopenaaa

    source /opt/django/pyopenaaa/bin/activate

    pip3 install django gunicorn mysqlclient PyMySQL

    cd /opt/django/pyopenaaa/MISC

    chmod +x daemon.sh

    mysql -u root -p < tacacs.sql

    cd ..

    python3 manage.py migrate

    python3 manage.py createsuperuser

Execute as root:

    source /opt/django/pyopenaaa/bin/activate

    gunicorn --chdir /opt/django/pyopenaaa -D PyOpenAAA.wsgi
