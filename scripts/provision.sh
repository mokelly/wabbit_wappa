#!/bin/bash

cd ~
sudo apt-get update
sudo apt-get -yqqu install git
sudo apt-get -yqqu install python-pip
sudo apt-get -yqqu install python-dev
sudo apt-get -yqqu install make
sudo pip install -r /vagrant/requirements.txt
/vagrant/scripts/vw-install.sh

cd /vagrant

cat /vagrant/scripts/bashrc.sh >> /home/vagrant/.bashrc
sudo python setup.py install
