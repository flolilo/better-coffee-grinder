======
README
======


What is Better Coffee Grinder (BCG)?
====================================

This is my idea of transforming any conventional coffee grinder into an (at least) 1/10s exact,
two-values saving, pause-allowing grinder with an OLED display.
This project consists of two parts:

1) The "Better Coffee Grinder" part: the software and all parts that are needed to run it,

2) The "mounting" part: step-by-step guides - and 3D files and/or additional parts where needed -
   to get the BCG running on a specific grinder.

In theory, this project should work with any grinder, though I cannot test it on any other than my
own. It should work with any grinder that uses a relay to power its AC motor (my Eureka M.C.I. uses
an induction motor, I plan to keep using the OEM starter capacitor), but of course, there is no
guarantee.

**Using this project with your grinder will most probably void its warranty, so beware. Also beware
that this project will have components that are connected to the mains (115 / 230 VAC) - it should
only be done by trained people who know what they are doing. There is no guarantee that any of my
schematics are correct, and if you mess this up (either by following or not following my
schematics), there is a serious risk of destruction of property, injury or even
death.**

That being said, I plan to keep this very simple. See the Fritzing file(s) and/or SVG(s) in the
``diagram`` folder.


Proposed features
=================

- 3+1 modes: timer 1 cup, timer 2 cup, manual, and if feasible: by weighing (e.g. grind 17 grams)

  - DIP switch to change default mode

- Rotary encoder to adjust timing (rotate) / change mode (push)

- *Best case*: Grinding in all modes can be paused by clicking the start/stop switch (auto-reset
  after a few seconds)

- OLED display that shows time and mode

  - Auto-standby for display (switch off or screen saver)


Details
=======

As of now, I plan to use a RP2040-based Microcontroller.

Pull-ups and de-bouncing are done with dedicated hardware - you can probably get away with adding
``utime.sleep()`` and of course µC-internal pull-ups, but parts are cheap and soldering is fun. ;-)

I plan to use either Micro- or CircuitPython, though all of this might still change; I will have to
do some proof of concept before deciding.


Parts
=====

As of now:

- µC: Sparkfun Pro Micro RP2040 (DEV-17717)

- Power supply: 110/230VAC --> 5VDC, 1A(?)

- Motor relay: Something comparable to the OEM one, but with 5VDC coil voltage.

  - Also needed to control it: NPN 2N2222 (+ NPN BC109), diode 1N4007 (or Schottky), resistor 1 kOhm

- *If weighing is feasible*: Any load cell <1kg + HX711

- Encoder: ALPS STEC11B09 or similar


Installation
============

- Install MicroPython on your device.

- ``git clone -recurse-submodules`` this repository.

- Using ``rshell`` (or a similar tool): ``cp ./main_micropython.py /pyboard/main.py``

- Also, follow ``./micropython-rotary/README.md``'s instructions for its installation.


Contribution
============

**Any help** -- both related to hardware and/or software --  **would be appreciated!**
