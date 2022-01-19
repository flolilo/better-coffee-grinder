import time
import machine
try:
    from rotary_irq_rp2 import RotaryIRQ
    import rp2
except Exception:
    print("FAIL")
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
    7       -           Button Encoder
    8       UART TX1    Debug: LED Encoder
    9       UART RX1    Debug: LED Button Encoder
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
rotary = RotaryIRQ(pin_num_clk=5, pin_num_dt=6,
                   min_val=0, max_val=0)
btn_enc = machine.Pin(7, machine.Pin.IN)

relay = machine.Pin(29, machine.Pin.OUT)

debug_led_dip1 = machine.Pin(26, machine.Pin.OUT)
debug_led_dip2 = machine.Pin(27, machine.Pin.OUT)
debug_led_btn_porta = machine.Pin(28, machine.Pin.OUT)
debug_led_btn_enc = machine.Pin(29, machine.Pin.OUT)

# maybe delete these for final version?
relay.value(0)
debug_led_dip1.value(0)
debug_led_dip2.value(0)
debug_led_btn_porta.value(0)
debug_led_btn_enc.value(0)

""" DEBUG: if ./mode_values gets ruined, uncomment this code for one runtime:
    which_mode_value = [1, 70, 140]
    with open("./mode_values", "w") as f:
        for element in which_mode_value:
            f.write(str(element) + "\n")
"""


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


# Read the DIPs:
""" DIP modes:
    OFF/OFF 0   manual
    ON/OFF  1   single
    OFF/ON  2   double
    ON/ON   3   manual (NOT IMPLEMENTED: weight)
"""
current_mode = 0 + dip1.value() + (2 * dip2.value())
# No mode 3 (proposed for using scales) as of now, so 3=0:
if current_mode == 3:
    current_mode = 0
print("DIP set to mode " + str(current_mode))
mode_values = read_mode_values(current_mode)

# Code so far:
btn_enc_state = None
btn_porta_state = None
val_old = rotary.value()
# Scales-Mode: Add fourth value (e.g. 500 for 50.0 g)
sane_maximum_times = [None, 450, 900]
while True:
    # Timer change:
    val_new = rotary.value()
    if current_mode != 0 and val_old > val_new:
        if mode_values[current_mode] < sane_maximum_times[current_mode]:
            mode_values[current_mode] += 1
        else:
            mode_values[current_mode] = 1
        val_old = val_new
        print('Timer:\t', str(mode_values[current_mode]))
    elif current_mode != 0 and val_old < val_new:
        if mode_values[current_mode] > 1:
            mode_values[current_mode] -= 1
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
        else:
            current_mode = 0
        print("Mode changed to " + str(current_mode))
        mode_values = read_mode_values(current_mode)
        btn_enc_state = None

    # Start/Stop:
    if not btn_porta.value() == 1 and btn_porta_state is None:
        btn_porta_state = 1
    elif btn_porta.value() == 1 and btn_porta_state == 1:
        # try:
        write_mode_values(mode_values)
        print("Start!")
        btn_porta_state = None
        relay.value(1)
        if current_mode > 0:
            i = mode_values[current_mode]
            while i > 0:
                i -= 1
                print(str(i))  # + "\t" + str(time.monotonic()))
                time.sleep(0.1)
        else:
            i = 0
            while i < 900:
                i += 1
                print(str(i))  # + "\t" + str(time.monotonic()))
                time.sleep(0.1)
        relay.value(0)
        print("Done!")
        # except Exception as e:
        #    print("ERROR! " + str(e))
        #    relay.value(0)
        time.sleep(0.001)
