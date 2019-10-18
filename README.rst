Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-miniqr/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/miniqr/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://discord.gg/nBQh6qu
    :alt: Discord

.. image:: https://travis-ci.com/adafruit/Adafruit_CircuitPython_miniQR.svg?branch=master
    :target: https://travis-ci.com/adafruit/Adafruit_CircuitPython_miniQR
    :alt: Build Status

A non-hardware dependant miniature QR generator library. All native Python!

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Usage Example
=============

.. code-block:: python

	import adafruit_miniqr

	qr = adafruit_miniqr.QRCode()
	qr.add_data(b'https://www.adafruit.com')
	qr.make()
	print(qr.matrix)

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_miniQR/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
