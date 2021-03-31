#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Better Coffee Grinder - Proof Of Concept

from time import sleep
from pynput import keyboard

# instead of encoders and buttons we use keyboard keys.
# instead of an I2C display, we use the terminal.

# operating mode:   0 ... manual,
#                   1 ... 1 shot,
#                   2 ... 2 shot,
#                   3 ... weight
mode = 0

# time increment for encoder
time_increment = 0.1
# use half of the increment as sleep-time
sleep_time = time_increment / 2

# those will later be saved in a separate file:
single_shot = 7.0
double_shot = 14.0

"""
def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False


# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

# ...or, in a non-blocking fashion:
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()
"""


def on_press(key):
    global mode, single_shot, double_shot, time_increment, sleep_time
    if key == keyboard.Key.left:
        if mode == 0:
            mode = 3
        else:
            mode -= 1
        print("Mode " + str(mode))
    elif key == keyboard.Key.right:
        if mode == 3:
            mode = 0
        else:
            mode += 1
        print("Mode " + str(mode))
    elif key == keyboard.Key.down:
        if mode == 1:
            if single_shot > 0:
                single_shot -= time_increment
            else:
                single_shot = 0.0
            print("Single: " + str(single_shot))
        elif mode == 2:
            if double_shot > 0:
                double_shot -= time_increment
            else:
                double_shot = 0.0
            print("Double: " + str(double_shot))
    elif key == keyboard.Key.up:
        if mode == 1:
            if single_shot < 60:
                single_shot += time_increment
            else:
                single_shot = 60.0
            print("Single: " + str(single_shot))
        elif mode == 2:
            if double_shot < 60:
                double_shot += time_increment
            else:
                double_shot = 60.0
            print("Double: " + str(double_shot))
    # TODO: Find a way to make a pause feasible.
    elif key == keyboard.Key.space:
        if mode == 1:
            countdown = single_shot
            while countdown > 0:
                countdown -= sleep_time
                print(str(countdown))
                sleep(sleep_time)
        elif mode == 2:
            countdown = double_shot
            while countdown > 0:
                countdown -= sleep_time
                print(str(countdown))
                sleep(sleep_time)
        elif mode == 0:
            countdown = 0.0
            while True:
                countdown += sleep_time
                print(str(countdown))
                sleep(sleep_time)


# Collect events until released
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
