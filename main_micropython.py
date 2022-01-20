# SPDX-License-Identifier: GPL-3.0-only
"""better-coffee-grinder - For a better coffee grinder experience"""
__author__ = "flolilo"
__license__ = "See SPDX-License-Identifier"
__contact__ = "See github.com/flolilo/better-coffee-grinder"
__version__ = "0.1-ALPHA"
import time
import machine
try:
    from rotary_irq_rp2 import RotaryIRQ
    import rp2
    import ssd1306
except Exception as e:
    print("Import failed!!! " + str(e))
print("Welcome to BCG!")

# Setting the pins up:
""" Pinout Sparkfun Pro Micro RP2040 (DEV-17717):
    <GPIO#> <Alt-Fn>    <Use>
    0       UART TX0    -
    1       UART RX0    -
    2       -           DIP 1 
    3       -           DIP 2 
    4       -           Button Portafilter
    5       -           Encoder A
    6       -           Encoder B
    7       -           Button Encoder; LED manual mode
    8       UART TX1    Debug: LED Encoder; LED Pause
    9       UART RX1    -
    16      Qwiic SDA   Qwiic OLED
    17      Qwiic SCL   Qwiic OLED
    20      SPI CIPO    -
    21      SPI CS      -
    22      SPI SCK     -
    23      SPI COPI    -
    25      LED         -
    26      ADC0        Debug: LED DIP1
    27      ADC1        Debug: LED DIP2
    28      ADC2        Debug: LED Button Porta
    29      ADC3        Relay (Debug: LED)
"""
dip1 = machine.Pin(2, machine.Pin.IN)
dip2 = machine.Pin(3, machine.Pin.IN)
btn_porta = machine.Pin(4, machine.Pin.IN)
rotary = RotaryIRQ(pin_num_clk=5, pin_num_dt=6, min_val=0, max_val=0)
btn_enc = machine.Pin(7, machine.Pin.IN)
relay = machine.Pin(29, machine.Pin.OUT)
i2c = machine.I2C(id=0, sda=machine.Pin(16), scl=machine.Pin(17), freq=40000)
# print(str(i2c.scan()))
display = ssd1306.SSD1306_I2C(width=128, height=64, i2c=i2c, addr=0x3D)
# maybe comment these out for final version?
debug_led_dip1 = machine.Pin(26, machine.Pin.OUT)
debug_led_dip2 = machine.Pin(27, machine.Pin.OUT)
debug_led_btn_porta = machine.Pin(28, machine.Pin.OUT)
debug_led_btn_enc_pause = machine.Pin(8, machine.Pin.OUT)
debug_led_dip1.value(dip1.value())
debug_led_dip2.value(dip2.value())
debug_led_btn_porta.value(0)
debug_led_btn_enc_pause.value(0)

relay.value(0)
timer = machine.Timer()

""" DEBUG: if ./mode_values gets ruined, uncomment this code for one runtime:
    which_mode_value = [900, 70, 140]
    with open("./mode_values", "w") as f:
        for element in which_mode_value:
            f.write(str(element) + "\n")
"""

# FIRST TRY OF OLED:
display.text('Welcome to BCG!', 0, 0, 1)
display.show()
display.poweron()
time.sleep(5)
display.poweroff()


def read_mode_values(which_mode):
    value = []
    try:
        with open("./mode_values", "r") as f:
            for line in f:
                value.append((int(line.strip())))

        print("Value for mode " + str(which_mode) + " is: " + str(value[which_mode]))

    except Exception as e:
        print("Error in read_mode_values!!! " + str(e))
        print("Using fallback values...")
        # Scales-Mode: add fourth value to list (e.g. 170 for 17.0 g)
        value = [1, 70, 140]

    return value


def write_mode_values(which_mode_value):
    try:
        with open("./mode_values", "w") as f:
            for element in which_mode_value:
                f.write(str(element) + "\n")

        print("  Saving values " + str(which_mode_value))

    except Exception as e:
        print("Error in write_mode_values!!! " + str(e))

    return 0


def handle_interrupt(timer):
    global counter_fresh_interrupts
    counter_fresh_interrupts += 1


# Read the DIPs:
""" DIP modes:
    OFF/OFF 0   manual
    ON/OFF  1   single
    OFF/ON  2   double
    ON/ON   3   manual (NOT IMPLEMENTED: weight)
"""
current_mode = dip1.value() + (2 * dip2.value())
if current_mode == 3:
    current_mode = 0
print("DIP set to mode " + str(current_mode))

# Denominator for timers, e.g. a value of ten means one tenth of a second. Must be integer.
#   Check variables granularity, sane_maximum_times and mode_values if you change this!
timer_denominator = 10
# Sane maximum times for your machine in 1/timer_denominator secs.
#   - Scales-Mode: Add fourth value (e.g. 500 for 50.0 g)
#   - First is in fact used for manual mode and should be the maximum time the grinder's motor
#     may run continuously. E.g. the sticker on the Eureka Mignon MCI says
sane_maximum_times = [900, 450, 900]
# Time until pausing results in abortion of operation. Also in 1/timer_denominator secs.
time_pause = 70
# Granularity for encoder
#   Higher values make for faster, coarser changes. Must be integer - in case you need finer
#     values, change variable timer_denominator to higher value (e.g. 100)
granularity = 1

# Read saved values for modes:
mode_values = read_mode_values(current_mode)

# Preparing variables for buttons:
btn_enc_state = None
btn_porta_state = None
val_old = rotary.value()

# Starting the hardware timer:
counter_fresh_interrupts = 0
timer.init(freq=timer_denominator, mode=timer.PERIODIC, callback=handle_interrupt)

# Perma-Loop
while True:
    # Timer change:
    val_new = rotary.value()
    if current_mode != 0 and val_old > val_new:
        if mode_values[current_mode] < sane_maximum_times[current_mode]:
            mode_values[current_mode] += granularity
        else:
            mode_values[current_mode] = 1
        val_old = val_new
        print('Timer:\t', str(mode_values[current_mode]))
    elif current_mode != 0 and val_old < val_new:
        if mode_values[current_mode] > 1:
            mode_values[current_mode] -= granularity
        else:
            mode_values[current_mode] = sane_maximum_times[current_mode]
        val_old = val_new
        print('Timer:\t', str(mode_values[current_mode]))

    # Mode change:
    if not btn_enc.value() == 1 and btn_enc_state is None:
        btn_enc_state = 1
    elif btn_enc.value() == 1 and btn_enc_state == 1:
        if current_mode < 2:  # No mode 3 as of now
            current_mode += 1
            debug_led_btn_porta.value(0)
        else:
            current_mode = 0
            debug_led_btn_porta.value(1)

        print("Mode changed to " + str(current_mode))
        mode_values = read_mode_values(current_mode)
        btn_enc_state = None

    # Start/Stop:
    if not btn_porta.value() == 1 and btn_porta_state is None:
        btn_porta_state = 1
    elif btn_porta.value() == 1 and btn_porta_state == 1:
        # try:
        relay.value(1)
        btn_porta_state = None
        write_mode_values(mode_values)
        counter_fresh_interrupts = 0
        print("Start grinding!")
        time.sleep_ms(150)

        # Timer modes:
        if current_mode > 0:
            i = mode_values[current_mode]
            # Double-break!  CREDIT: stackoverflow.com/a/6564670
            double_breaker = False
            while i > 0:
                if counter_fresh_interrupts > 0:
                    state = machine.disable_irq()
                    counter_fresh_interrupts -= 1
                    machine.enable_irq(state)
                    i -= 1
                    print("  |>  " + str(i))  # + "\t" + str(time.monotonic()))
                if not btn_porta.value() == 1 and btn_porta_state is None:
                    btn_porta_state = 1
                elif btn_porta.value() == 1 and btn_porta_state == 1:
                    relay.value(0)
                    btn_porta_state = None
                    counter_fresh_interrupts = 0
                    counter_pause_interrupts = 0
                    debug_led_btn_enc_pause.value(1)
                    print("Pause grinding")
                    time.sleep_ms(150)
                    while True:
                        if counter_fresh_interrupts > 0:
                            state = machine.disable_irq()
                            counter_fresh_interrupts -= 1
                            machine.enable_irq(state)
                            counter_pause_interrupts += 1
                            print("  ||  " + str(counter_pause_interrupts))
                        if btn_porta.value():
                            print("Pause ended")
                            relay.value(1)
                            break
                        if counter_pause_interrupts >= time_pause:
                            print("Abort (pause timed out)")
                            double_breaker = True
                            break
                    debug_led_btn_enc_pause.value(0)
                if double_breaker:
                    relay.value(0)
                    break
        # Manual mode:
        else:
            i = 0
            # Double-break!  CREDIT: stackoverflow.com/a/6564670
            double_breaker = False
            while i < sane_maximum_times[current_mode]:
                if counter_fresh_interrupts > 0:
                    state = machine.disable_irq()
                    counter_fresh_interrupts -= 1
                    machine.enable_irq(state)
                    i += 1
                    print("  |>  " + str(i))  # + "\t" + str(time.monotonic()))
                if not btn_porta.value() == 1 and btn_porta_state is None:
                    btn_porta_state = 1
                elif btn_porta.value() == 1 and btn_porta_state == 1:
                    relay.value(0)
                    btn_porta_state = None
                    counter_fresh_interrupts = 0
                    counter_pause_interrupts = 0
                    debug_led_btn_enc_pause.value(1)
                    print("Pause grinding")
                    time.sleep_ms(150)
                    while True:
                        if counter_fresh_interrupts > 0:
                            state = machine.disable_irq()
                            counter_fresh_interrupts -= 1
                            machine.enable_irq(state)
                            counter_pause_interrupts += 1
                            print("  ||  " + str(counter_pause_interrupts))
                        if btn_porta.value():
                            print("Pause ended")
                            relay.value(1)
                            break
                        if counter_pause_interrupts >= time_pause:
                            print("Abort (pause timed out)")
                            double_breaker = True
                            break
                    debug_led_btn_enc_pause.value(0)
                if double_breaker:
                    relay.value(0)
                    break
        relay.value(0)
        print("Done grinding!")
        debug_led_btn_porta.value(0)
        # except Exception as e:
        #    print("ERROR! " + str(e))
        #    relay.value(0)
    time.sleep_ms(1)
