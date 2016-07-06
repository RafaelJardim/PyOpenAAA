# PyOpenAAA

This system was developed and tested on Debian 8.5 (Netinstall) for amd64. You can obtain Debian last version at http://cdimage.debian.org/debian-cd (http://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-8.5.0-amd64-netinst.iso in my case)

## Pre-requirements

* python3.x
* pip3
* mysql-server
* nginx
* libmysqlclient-dev
* unzip

You can install this pre-requiriments with the follow command:

    apt-get update
    
    # On mysql-server package install, you must provide an root user password. Keep this password safe.
    apt-get install python3 python3-pip mysql-server nginx libmysqlclient-dev unzip


## Instalation    

### tac_plus

The follow commands must be used with root user or privileged user:

    # Optional directory 
    cd /usr/src/
    
    # It's recommend to check if a new version of tac_plus is availible on http://www.pro-bono-publico.de
    wget http://www.pro-bono-publico.de/projects/src/DEVEL.201606121104.tar.bz2

    # Decompress bzip2 file
    bzip2 -d DEVEL.201606121104.tar.bz2

    # Decompress tar file
    tar xf DEVEL.201606121104.tar

    cd PROJECTS

    ./configure tac_plus

    make

    make install

### Github Files

The follow commands must be used with root user or privileged user:

    # Optional directory 
    cd /usr/src/
    
    # Download last master branch
    wget https://github.com/RafaelJardim/PyOpenAAA/archive/master.zip

    # Decompress zip file
    unzip -a master.zip

    # Create application folder
    mkdir -p /opt/django/pyopenaaa

    # Move content to application folder
    mv PyOpenAAA-master/* /opt/django/pyopenaaa/

    # Change the own of files on application folder
    chown -R APP_USER /opt/django/pyopenaaa

### Nginx

Nginx is used as webserver to Static file (CSS, JavaScript, images, etc.) and proxy to Django application port

The follow commands must be used with root user or privileged user:

    cd /opt/django/pyopenaaa/MISC

    # Copy nginx configuration file to "sites-avaliable" folder
    cp  django_nginx.config /etc/nginx/sites-available/

    # Remove default installation file to avoid port and page conflits
    rm /etc/nginx/sites-enabled/default

    # Create a symbol link to django configuration file
    ln -s /etc/nginx/sites-available/django_nginx.config /etc/nginx/sites-enabled/django

    # Restart nginx service
    service nginx restart

### Python Virtual Environment    

The follow commands must be used with root user or privileged user:

    pip3 install virtualenv

### Application and Python Packages    

The follow commands can be used with the "application user", root user or privileged user:

    # Create a virtal environment to protect your system and use corrects python packages
    virtualenv /opt/django/pyopenaaa

    # Activate the virtual enviroment
    source /opt/django/pyopenaaa/bin/activate

    # Install python packages from pip
    pip3 install django gunicorn mysqlclient PyMySQL

    cd /opt/django/pyopenaaa/MISC

    # Give execute permission to script responsable to start|stop|restart tac_plus system process
    chmod +x daemon.sh

### Create DataBase

The follow commands can be used with the "application user", root user or privileged user:

    # Create 'tacacs' database. 
    mysql -u root -p < tacacs.sql

    !!! You must edit the follow files to change the database username and password !!!

    * /opt/django/pyopenaaa/PyOpenAAA/settings.py
    * /opt/django/pyopenaaa/tacacs/mysql.py

    cd /opt/django/pyopenaaa/

    # Integrate the database tacacs to Django
    python3 manage.py migrate

    # Create an user to administrate PyOpenAAA system. 
    # If you need to create another users after the system instalation, you can access http://PYOPENAAA URL/admin
    # to administrate the users
    python3 manage.py createsuperuser


### Create DataBase User (Optional)

If you want to create an user to access the database of this application instead of root user, use the follow commands:
    
    # Access the MySQL
    mysql -u root -p
    
    # Create your new user replacing 'myuser' and 'mypassword'
    CREATE USER 'myuser'@'%' IDENTIFIED BY 'mypassword';

    # Grant privileges replacing 'myuser' by your username
    GRANT ALL PRIVILEGES ON tacacs.* TO 'myuser'@'%' WITH GRANT OPTION;
    
    FLUSH PRIVILEGES;

Edit the follow files to update the database username and password:

    /opt/django/pyopenaaa/PyOpenAAA/settings.py
    /opt/django/pyopenaaa/tacacs/mysql.py

## Starting PyOpenAAA

The follow commands must be used with root user or privileged user:
    
    source /opt/django/pyopenaaa/bin/activate

    gunicorn --chdir /opt/django/pyopenaaa -D PyOpenAAA.wsgi
