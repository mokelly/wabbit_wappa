##############
Wabbit Wappa
##############

.. image:: https://travis-ci.org/mokelly/wabbit_wappa.svg?branch=master
    :target: https://travis-ci.org/mokelly/wabbit_wappa

**Wabbit Wappa** is a full-featured Python wrapper for the lightning fast `Vowpal Wabbit <https://github.com/JohnLangford/vowpal_wabbit/wiki>`_ ("VW") 
machine learning utility.  Wabbit Wappa makes it easier to use VW's powerful features while abstracting away its idiosyncratic syntax and interface.

.. contents:: :local:

****************
Features
****************

* Complete Pythonic wrapper for the Vowpal Wabbit training and test syntax
* Online training and testing, with no need to restart VW or reload the trained model to go between them
* Save the trained model on the fly

****************
Getting Started
****************

If you're unfamiliar with Vowpal Wabbit, this documentation is no substitute for 
the `detailed tutorials <https://github.com/JohnLangford/vowpal_wabbit/wiki/Tutorial>`_
at the VW wiki.  You'll eventually need to read those to understand VW's advanced features.

Installation
===============

You have three installation options, depending on your comfort with compiling and installing the VW utility.

**If you already have Vowpal Wabbit installed**::

    pip install wabbit_wappa

**If you still need to install VW (currently version 7.7) and its dependencies**:

Start by cloning the WW repository::

    git clone https://github.com/mokelly/wabbit_wappa.git
    cd wabbit_wappa

Then run the included install script (which more or less follows the VW instructions)::

    scripts/vw-install.sh
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib;
    python setup.py install

(The "export" line should be added to your .profile if you don't want to run it every time you use Vowpal Wabbit.)

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

Let's walk through an example of using Wabbit Wappa.  We will teach VW to recognize
capitalized characters.
(You can find the whole script at ``examples/capitalization_demo.py``.)

Start a default VW process in Logistic Regression mode::

    >>> from wabbit_wappa import *
    >>> vw = VW(loss_function='logistic')
    >>> print vw.command
    vw --save_resume --quiet --loss_function logistic --predictions /dev/stdout

Behind the scenes, Wabbit Wappa generates a command line including default parameters critical
to interaction with this wrapper.  VW is immediately run as a subprocess.

Now train the logistic model by sending 10 labeled examples to the VW learner::

    for i in range(10):
        label, features = get_example()  # Random example; see capitalization_demo.py
        vw.send_example(label, features=features)

From examples like these::

    Label -1: ['z', 'x', 'n', 'F', 'C', 'B', 'f', 'p', 'O'] is mostly lowercase
    Label -1: ['S', 'u', 'e', 'K', 'f', 'w', 'l', 'C', 'd'] is mostly lowercase
    Label -1: ['g', 'v', 'q', 'z', 'x', 'B', 'T', 'p', 'M'] is mostly lowercase
    Label 1: ['j', 'i', 'k', 'D', 'm', 'N', 'Q', 'Z', 'L'] is mostly uppercase
    Label 1: ['B', 'U', 'V', 'R', 'i', 'h', 'T', 'A', 'v'] is mostly uppercase
    Label 1: ['Y', 'u', 'R', 'K', 's', 'X', 'g', 'M', 'j'] is mostly uppercase
    Label -1: ['t', 'L', 'a', 'g', 'D', 'E', 'f', 'G', 'u'] is mostly lowercase
    Label 1: ['F', 'W', 'y', 'i', 'U', 'E', 'X', 'r', 'e'] is mostly uppercase
    Label -1: ['s', 'e', 'h', 'U', 'J', 'C', 'j', 'P', 'b'] is mostly lowercase
    Label 1: ['A', 'k', 'H', 'G', 'a', 'b', 'w', 'Q', 'V'] is mostly uppercase

VW begins to find the pattern: a +1 label if the capital letters outnumber the
lowercase, and -1 otherwise.

How well trained is our model?  Let's run 100 tests on new random examples::

    for i in range(num_tests):
        label, features = get_example()
        # Give the features to the model, witholding the label
        response = vw.get_prediction(features)
        prediction = response.prediction
        # Test whether the floating-point prediction is in the right direction
        if cmp(prediction, 0) == label:
            num_good_tests += 1

(For logistic regression, a ``prediction`` value greater than zero representa
a label of +1; that is why ``cmp(prediction, 0)`` is used.)

    >>> print "Correctly predicted", num_good_tests, "out of", num_tests
    Correctly predicted 60 out of 100

We can go on training, without restarting the process.  Let's train on 1,000 more examples::

    for i in range(1000):
        label, features = get_example()
        vw.send_example(label, features=features)

Now how good are our predictions?

    Correctly predicted 98 out of 100

We can save the model to disk at any point in the process::

    filename = 'capitalization.saved.model'
    vw.save_model(filename)

and reload our model using the 'i' argument::

    >>> vw2 = VW(loss_function='logistic', i=filename)
    >>> print vw2.command
    vw -i capitalization.saved.model --save_resume --quiet --loss_function logistic --predictions /dev/stdout

The ``vw2`` model will now give just the same predictions that ``vw`` would have; and the default ``save_resume=True`` parameter
means we can continue training from where we left off.

To shut down the VW subprocess before your program exits, call ``vw.close()``.


****************
Documentation
****************

Namespaces
===============

The most important Vowpal Wabbit feature not discussed above is namespaces.  VW
uses namespaces to divide features into groups, which is used for some of its
advanced features.  Without discussing in detail *why* you would use them,
here's *how* to use namespaces in Wabbit Wappa.

To reproduce an example from this `Vowpal Wabbit tutorial <https://github.com/JohnLangford/vowpal_wabbit/wiki/v6.1_tutorial.pdf>`_::

    namespace1 = Namespace('excuses', 0.1, [('the', 0.01), 'dog', 'ate', 'my', 'homework'])
    namespace2 = Namespace('teacher', features='male white Bagnell AI ate breakfast'.split())

These namespaces can then be used as examples in training and prediction::

    vw.send_example(response=1.,
                    importance=.5,
                    tag="example_39",
                    namespaces=[namespace1, namespace2])
    response = vw.get_prediction(namespaces=[namespace1, namespace2])
    prediction = response.prediction

Alternatively, Namespaces can be queued up to be used automatically in the next
example or prediction sent to the VW subprocess::

    vw.add_namespace(namespace1)
    vw.add_namespace(namespace2)
    vw.send_example(response=-1., importance=.5, tag="example_39")

or::

    vw.add_namespace('excuses', 0.1, [('the', 0.01), 'dog', 'ate', 'my', 'homework'])
    vw.add_namespace('teacher', features='male white Bagnell AI ate breakfast'.split())
    response = vw.get_prediction()
    prediction = response.prediction

Tokens in Vowpal Wabbit may not contain the space character, ``:`` or ``|``.  By default,
Wabbit Wappa will detect and escape these characters::

    >>> namespace = Namespace('Metric Features', 3.28, [('hei|ght', 1.5), ('len:gth', 2.0)])
    >>> print namespace.to_string()
    Metric\_Features:3.28 hei\\ght:1.5 len\;gth:2.0

If you wish, you can get the raw VW input lines and pass them to the subprocess directly::

    vw.add_namespace(namespace1)
    vw.add_namespace(namespace2)
    raw_line = vw.make_line(response=1., importance=.5, tag="example_39")
    vw.send_line(raw_line)

    >>> print raw_line
    1.0 0.5 'example_39|excuses:0.1 the:0.01 dog ate my homework |teacher male white Bagnell AI ate breakfast


VW Options
===============

In the ``VW()`` constructor, each named argument corresponds
to a Vowpal Wabbit option.  Single character keys are mapped to single-dash options;
e.g. ``b=20`` yields ``-b 20``.  Multiple character keys map to double-dash options:
``quiet=True`` yields ``--quiet``.

Boolean values are interpreted as flags: present if True, absent if False (or not given).
All non-boolean values are treated as option arguments, as in the `-b` example above.

If an option argument is a list, that option is repeated multiple times;
e.g. ``q=['ab', 'bc']`` yields ``-q ab -q bc``.

Run ``vw -h`` from your terminal for a listing of most options.

Note that Wabbit Wappa makes no attempt to validate the inputs or
ensure they are compatible with its functionality.  For instance, changing the
default ``predictions='/dev/stdout'`` will probably make that ``VW()`` instance
non-functional.

Active Learning
=================

Active Learning is an approach to training somewhere between supervised and unsupervised.
When getting labeled data is very expensive (such as when users must be solicited for
their preferences), an Active Learning approach assigns an "importance" value to each
unlabeled example, so that only the most critical labels need be acquired.

Vowpal Wabbit's `Active Learning <https://github.com/JohnLangford/vowpal_wabbit/wiki/active_learning.pdf>`_
interface requires you to start a VW instance in server mode and communicate with it
via a socket.  Wabbit Wappa abstracts all that away, providing the same interface for both
regular and Active learning::

    vw = VW(loss_function='logistic', active_mode=True, active_mellowness=0.1)
    response = vw.get_prediction(features)
    if response.importance >= 1.:
        label = get_expensive_label(features)
        vw.send_example(label, features=features)

See ``examples/active_learning_demo.py`` for a fully worked example.


API Documentation
===================

For complete explanation of all parameters, refer to the docstrings::

    import wabbit_wappa
    help(wabbit_wappa)

