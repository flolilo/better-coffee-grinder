===================
Eureka Mignon M.C.I
===================

*Also known as Nuova Simonelli MCI?*

**TBD**. As of now, this is just a "how to contribute to this project so I can share my awesome
modifications?" showcase.


OEM parts worth considering
===========================

Parts found in what I assume to be one of the latter model iterations (IC board rev. 1.1, presumably
manufactured Q2/2019):

- OEM Motor capacitor is a Sintex 45M.B3D 8

- OEM relay is an Omron G2RL-1A @ 12VDC

- Original IC power supply is a Myrra 44327

- (Confirmation/details needed!) There are three 6,3mm blade connectors for mains/motor

- (Confirmation/details needed!) There is a 2 pin connector for the porta switch


Step-by-step guide
==================

Use at your own risk. Injuries, loss of warranty, damage to the equipment and all other risks and
dangers of this tutorial are for you to consider!

**Aside from the soldering iron, these are the needed tools**:

- Long, thin PH2 screw driver (to open the case)

- A utility blade if you decide to replace the OEM switch with an MX one


**Aside from the RP2040-style µC, these parts are specifically needed (because)**:

- 6,3mm blade connectors (same as on OEM IC)

- Optional: Cherry MX-style switch (OEM switch has poor tactile feeling)

  - A few cm of high pressure rim tape (to mount it without needing 3D files)

  - Two 2,54mm connectors, both male and female (for the cable)

  - Two isolated wires/2-wire cable, >= 30cm (for connecting it to the IC)

- If you decide against the switch, you need another connector matching the OEM one (TBD: measure
  it, find model).


----------------
Opening the case
----------------

- Unplug the device *(duh)*

- Remove the hopper

- Turn the grinder upside down

- Remove the rubber feet

- Loosen the screws

- Carefully separate the bottom part from the rest of the grinder (careful: wires!)

For details, see picture ``TBD``.


---------------------
Removing the IC board
---------------------

- Disconnect the porta switch cable (connector roughly top-mid)

- Disconnect the three wires (connectors bottom right)


-------------------------------
Replacing the switch (optional)
-------------------------------

- Remove the Eureka-Logo on the funnel (only fingers needed)

- Loosen the screw behind it

- Very carefully remove the funnel part (careful: wires!)

- Loosen the screws of the switch

- TBD


---------------------
Fitting the BCG board
---------------------

This will probably involve a freshly 3D-printed bottom part (same dimensions, but DIP, USB and the
encoder will probably need different holes) - if so, the 3D file will be shared.
