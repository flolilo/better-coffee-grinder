======
README
======


What is better-coffee-grinder
=============================

This is my idea of transforming my coffee grinder - a Eureka Mignon M.C.I. - into a 1/100s exact, two-values saving, pause-allowing grinder with an OLED display.
This project will include a list of all used parts, 3D-print files for every custom part I need/want, and of course the code.

As of now, I plan to use a RP2040-based Microcontroller - perhaps the Adafruit ItsyBitsy RP2040. I also plan to use CircuitPython, though both things might still change; I will have to do some proof of concept before deciding.

In theory, this should work with any grinder, though I cannot test it on any other than my own. It should work with any grinder that uses a relay to power its AC motor (the M.C.I. uses a capacitor start motor, I plan to keep using the OEM capacitor), but of course, there is no guarantee.

Using this project with your grinder will most probably void its warranty, so beware.
Also beware that this project will have components that are connected to the mains (115 / 230 VAC) - it should only be done by trained people who know what they are doing. There is no guarantee that any of my schematics are correct, and if you mess this up (either by following or not following my plan), there is a serious risk of destruction of property (grinder), injury (you) or even death (you).

That being said, I plan to keep this very simple.


Proposed features
=================

- Rotary encoder to adjust timing (rotate) / change mode (push)
- DIP switch to change default mode
- Cherry MX switch for starting/stopping the grinding
- 3+1 modes: timer 1 cup, timer 2 cup, manual, and if feasible: by weighing (e.g. grind 17 grams)
- Every mode can be paused by clicking the start/stop switch (auto-reset after a few seconds)
- OLED display that shows time and mode
    - auto-standby for display (switch of or screen saver)


Details
=======

TBD


Parts
=====

Nothing yet decided, but so far:

- Motor relay: Omron G2RL-1A or Omron G2RL-1A-E (or something alike)
    - also needed to control it: NPN 2N2222, diode 1N4007, resistor 1 kOhm
- If weighing is feasible: any load cell and HX711
- If it fits in the original space: Cherry MX Green
- Encoder: ALPS STEC11B09


Contribution
============

**Any help would be appreciated!**
