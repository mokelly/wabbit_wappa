##############
Wabbit Wappa
##############

**Wabbit Wappa** is a full-featured Python wrapper for the lightning fast `Vorpal Wabbit <https://github.com/JohnLangford/vowpal_wabbit/wiki>`_ ("VW") machine learning utility.  Wabbit Wappa makes it easy to use VW's powerful features while not dealing with its idiosyncratic syntax and interface.

****************
Features
****************

* Complete Pythonic wrapper for the Vorpal Wabbit training and test syntax
* Online training and testing, with no need to restart VW or reload the trained model to go between them
* Save the trained model on the fly

****************
Getting Started
****************

If you're unfamiliar with Vorpal Wabbit, this documentation is no substitute for 
the `detailed tutorials <https://github.com/JohnLangford/vowpal_wabbit/wiki/Tutorial>`_
at the VW wiki.  You'll eventually need to read those to understand VW's advanced features.

Installation
===============

*Coming soon: install via Pip*

Start by cloning the WW repository::

    git clone https://github.com/mokelly/wabbit_wappa.git
    cd wabbit_wappa

You have three installation options, depending on your comfort with compiling and installing the VW utility.

**If you already have Vorpal Wabbit installed**::

     python setup.py install

**If you still need to install VW and its dependencies**::

     scripts/vw-install.sh
     export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib;
     python setup.py install

(The "export" line should be added to your .profile if you don't want to run it every time you use Vorpal Wabbit.)

**If you want a virtual machine with everything all set up for you:**
    
*Windows users, this is your only option at present*

First install the virtual machine manager `Vagrant <http://www.vagrantup.com/>`_ along with your favorite virtualization system (such as `VirtualBox <https://www.virtualbox.org/>`_).
Then from the Wabbit Wappa source directory type::

    vagrant up

This will launch an Ubuntu VM and provision it with VW and WW, completely automatically!  Once that's all complete, just SSH to your new VM with::

    vagrant ssh
    
Testing
---------

Make sure everything is installed and configured correctly by running the tests::

    py.test

Usage Example
===============

 *TODO*

****************
Documentation
****************

For now, read the docstrings::

    import wabbit_wappa
    help(wabbit_wappa)

