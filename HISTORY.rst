.. :changelog:

****************
History
****************

0.0.1 (2014-03-31)
=====================

* First release on GitHub

0.0.2 (2014-04-07)
=====================

* Good unit test coverage
* Full documentation, instructions and demo
* Added command line builder with Pythonic interface

0.1.2 (2014-04-09)
=====================

* Now installable using pip
* Updated VW version to 7.6
* Tweaked line detection to speed up process communication

0.2.0 (2014-04-13)
=====================

* Active Learning interface, with documentation and example script
* Minor performance boosts
* **Backwards-incompatible change:** ``get_prediction()`` now returns a ``VWResult`` object, with the predicted value accessible as ``result.prediction``.
  
0.3.0 (2014-10-16)
======================

* Python 3 compatibility (thanks `Antti Haapala <https://github.com/ztane>`_!)
* Much faster line buffering (50% overall speed improvement) (thanks `Antti Haapala <https://github.com/ztane>`_!)
* Updated VW version to 7.7
* Updated Ubuntu in VM to Trusty
* Travis integration
