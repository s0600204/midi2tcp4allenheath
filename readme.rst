
MIDI <--> TCP for Allen & Heath Sounddesks
==========================================

Console interface for sending MIDI messages to Allen & Heath's sounddesks over TCP.

... Note: *Receiving* messages won't work properly as mido does not currently
          support MIDI Running Status.

This utility creates a virtual MIDI input that will forward all MIDI messages
sent to it to an attached sound desk, and a virtual MIDI output that will emit
all MIDI message recieved from said attached sound desk.


Device Support
--------------

Supported and Tested:

* ...

Should also be supported, but needs testing:

* D-Live
* GLD80 / GLD112


Usage
-----

'''
midi2tcp4allenheath -a <ip-address>
'''

Then connect your applications to the MIDI ports now made available on the PC.
