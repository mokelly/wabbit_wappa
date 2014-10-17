#!/bin/bash
sudo apt-get -yqqu install libboost-all-dev
# sudo apt-get -yqqu install boost-all-dev
# sudo apt-get -yqqu install automake
# sudo apt-get -yqqu install libtool

wget https://github.com/JohnLangford/vowpal_wabbit/archive/7.7.tar.gz
tar -zxvf 7.7.tar.gz
cd vowpal_wabbit-7.7

# ./autogen.sh --with-boost-libdir=/usr/lib/x86_64-linux-gnu
# ./configure
make
sudo make install
# LD_LIBRARY_PATH is necessary for vw to find required .so file(s)
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib;


