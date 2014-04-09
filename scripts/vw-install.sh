#!/bin/bash
sudo apt-get -yqqu install libboost-all-dev

wget https://github.com/JohnLangford/vowpal_wabbit/archive/7.6.tar.gz
tar -zxvf 7.6.tar.gz
cd vowpal_wabbit-7.6

./autogen.sh
./configure
make
sudo make install
# LD_LIBRARY_PATH is necessary for vw to find required .so file(s)
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib;


