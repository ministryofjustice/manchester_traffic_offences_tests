#!/bin/bash

SELENIUM_JAR="selenium-server-standalone-2.46.0.jar"
SELENIUM_URL="http://selenium-release.storage.googleapis.com/2.46/selenium-server-standalone-2.46.0.jar"

if [ -d "/vagrant" ]
then
    SCRIPT_HOME = "/vagrant"
    VAGRANT=1
else
    SCRIPT_HOME = "~/jenkins/"
fi

cd "$SCRIPT_HOME"

# Some convenience functions
function _link {
    sudo rm -rf $2
    if [ -n "${3+1}" ]
    then
        echo "Removed $2, linking $1 to $2 for $3"
        sudo -u $3 ln -sv $1 $2
    else
        echo "Removed $2, linking $1 to $2 for root"
        sudo ln -sv $1 $2
    fi
}

function linkfile {
    # $1 - local path
    # $2 - target
    # $3 - user
    if [ -f $(realpath $1) ]
    then
        _link $(realpath $1) $2 $3
    else
        echo "$(realpath $1) does not exist to link!"
    fi
}

function linkdir {
    # $1 - local path
    # $2 - target
    # $3 - user
    if [ -d $(realpath $1) ]
    then
        _link $(realpath $1) $2 $3
    else
        echo "$(realpath $1) does not exist to link!"
    fi
}

function apt-get-install {
    sudo apt-get install -y --force-yes "$@"
}

# Setup
if [ ! -f "/etc/apt/sources.list.d/jenkins.list" ]; then
    echo "Installing Jenkins"
	wget -q -O - https://jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -
	sudo sh -c 'echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list'
	sudo apt-get update
	apt-get-install jenkins
fi

if [ ! -d "/home/jenkins" ]; then
    sudo mkdir -pv /home/jenkins
fi
sudo chmod 777 /home/jenkins

# General dependencies
apt-get-install realpath unzip swig

# Dependencies for MaP unit tests
apt-get-install git python-setuptools build-essential libxml2 libxslt1-dev postgresql-9.3
sudo apt-get -y build-dep python-psycopg2
sudo -u postgres createuser --superuser jenkins
sudo -u postgres psql -c "ALTER USER jenkins WITH PASSWORD 'moomoo';"

# Dependencies for MaP Integration tests
apt-get-install python3-setuptools firefox xvfb xserver-xorg-core xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic dbus-x11

# Jenkins setup
sudo usermod -d /home/jenkins jenkins
if [ -n "${VAGRANT+1}" ]; then
    sudo usermod -a -G vagrant jenkins
fi
linkdir jenkins/.ssh /home/jenkins/.ssh
linkdir jenkins/config /home/jenkins/config
linkfile jenkins/files/etc/default/jenkins /etc/default/jenkins
sudo easy_install pip
sudo pip install -r jenkins/requirements.txt

sudo easy_install3 pip
sudo pip3 install -r selenium/requirements.txt

# Git crypt setup
cd /tmp
wget https://github.com/AGWA/git-crypt/archive/0.4.2.zip
unzip 0.4.2.zip
cd git-crypt-0.4.2/
make
sudo make install
cd $SCRIPT_HOME

gpg --import /home/jenkins/.ssh/jenkins.gpg

# Selenium setup
linkfile selenium/files/var/spool/cron/crontabs/root /var/spool/cron/crontabs/root
linkfile selenium/files/etc/init.d/selenium /etc/init.d/selenium

sudo mkdir -p /usr/lib/selenium
cd /usr/lib/selenium
if [ ! -f $SELENIUM_JAR ]; then
	sudo wget $SELENIUM_URL
fi
sudo rm -f selenium-server-standalone.jar
sudo ln -s $SELENIUM_JAR selenium-server-standalone.jar
cd -

sudo mkdir -p /var/log/selenium
sudo chmod a+w /var/log/selenium
sudo chmod 755 /etc/init.d/selenium
sudo update-rc.d selenium defaults

sudo curl -L https://raw.githubusercontent.com/hgomez/devops-incubator/master/forge-tricks/batch-install-jenkins-plugins.sh -o batch-install-jenkins-plugins.sh
sudo chmod +x batch-install-jenkins-plugins.sh
./batch-install-jenkins-plugins.sh --plugins "$SCRIPT_HOME/jenkins/iplugins" --plugindir /home/jenkins/config/plugins

# Restart services
sudo service selenium restart
sudo service jenkins restart
