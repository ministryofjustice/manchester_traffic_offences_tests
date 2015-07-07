#!/bin/bash

# Setup
sudo usermod -d /home/jenkins jenkins
sudo chown jenkins:jenkins /home/jenkins
sudo cp -r * /home/jenkins
sudo cp -r .ssh /home/jenkins
sudo chown -R jenkins:jenkins /home/jenkins/config
sudo chown -R jenkins:jenkins /home/jenkins/.ssh
sudo cp files/etc/default/jenkins /etc/default/jenkins

# Dependencies for MaP unit tests
sudo apt-get install -y git python-setuptools build-essential libxml2 libxslt1-dev postgresql-9.3
sudo apt-get -y build-dep python-psycopg2

# Dependencies for MaP Integration tests
sudo apt-get install -y python3-setuptools firefox xvfb xserver-xorg-core xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic dbus-x11
sudo easy_install3 pip
sudo pip3 install -r requirements.txt

sudo cp files/var/spool/cron/crontabs/root /var/spool/cron/crontabs/root
sudo cp files/etc/init.d/selenium /etc/init.d/selenium
sudo mkdir /usr/lib/selenium
cd /usr/lib/selenium
sudo wget http://selenium-release.storage.googleapis.com/2.46/selenium-server-standalone-2.46.0.jar
sudo rm selenium-server-standalone.jar
sudo ln -s selenium-server-standalone-2.46.0.jar selenium-server-standalone.jar

sudo mkdir -p /var/log/selenium
sudo chmod a+w /var/log/selenium
sudo chmod 755 /etc/init.d/selenium
sudo update-rc.d selenium defaults

# Restart services
sudo service selenium restart
sudo service jenkins restart
