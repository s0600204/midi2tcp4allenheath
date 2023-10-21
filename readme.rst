
MIDI ⮂ TCP for Allen & Heath Digital Audio Mixers
=================================================

Console interface for sending MIDI messages to Allen & Heath's digital audio
mixers over TCP.

.. Note:: *Receiving* messages currently doesn't work properly due to mido_ not
          currently supporting MIDI Running Status (`Issue 341`_).

This utility creates a virtual MIDI input that will forward all MIDI messages
sent to it to an attached sound desk, and a virtual MIDI output that will emit
*most* of the MIDI messages received from said attached sound desk.


Device Support
--------------

Supported and Tested:

* GLD80

Should also be supported, but needs testing:

* D-Live
* GLD112


Usage
-----

Run without arguments to get a list of discoverable devices:

.. code:: bash

  midi2tcp4allenheath

Once you've determined which device you wish to connect to, pass its IP address
with the ``-a`` or ``--address`` flag:

.. code:: bash

  midi2tcp4allenheath -a <ip-address>

Then connect your application to the MIDI ports now locally available on the
computer.


.. _mido: https://mido.readthedocs.io
.. _Issue 341: https://github.com/mido/mido/pull/341
