import utime
import machine
from rotary_irq_rp2 import RotaryIRQ
import rp2
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
r = RotaryIRQ(pin_num_clk=5, pin_num_dt=6,
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


def read_mode_value(which_mode):
    if which_mode == 1:
        try:
            value = int(open('./mode1', 'r').read())
        except Exception:
            value = 70
    elif which_mode == 2:
        try:
            value = int(open('./mode2', 'r').read())
        except Exception:
            value = 140
    elif which_mode == 3:
        try:
            value = int(open('./mode3', 'r').read())
        except Exception:
            value = 170
    else:
        value = None

    print("Value for mode " + str(which_mode) + " is: " + str(value))
    return value


def write_mode_value(which_mode, which_mode_value):
    if which_mode == 1:
        mode_file = "./mode1"
    elif which_mode == 2:
        mode_file = "./mode2"
    elif which_mode == 3:
        mode_file = "./mode3"
    else:
        return 0

    print("  Writing " + str(which_mode_value) + " to " + str(which_mode))

    try:
        with open(mode_file, 'w') as f:
            f.write(str(which_mode_value))
            f.close()
    except Exception:
        return 1

    return 0


# Read the DIPs:
mode = 0
""" DIP modes:
    OFF/OFF 0   manual
    ON/OFF  1   single
    OFF/ON  2   double
    ON/ON   3   manual (TODO: weight)
"""
if dip1.value() == 1:
    mode += 1
if dip2.value() == 1:
    mode += 2
# No mode 3 as of now, so 3=0:
if mode == 3:
    mode = 0
print("DIP set to mode " + str(mode))
mode_value = read_mode_value(mode)

# Code so far:
btn_enc_state = None
btn_porta_state = None
val_old = r.value()
while True:
    val_new = r.value()
    if val_old > val_new:
        mode_value += 1
        val_old = val_new
        print('Timer:\t', str(mode_value))
    elif val_old < val_new:
        mode_value -= 1
        val_old = val_new
        print('Timer:\t', str(mode_value))
    if not btn_enc.value() == 1 and btn_enc_state is None:
        btn_enc_state = 1
    if btn_enc.value() == 1 and btn_enc_state == 1:
        if mode < 2:  # No mode 3 as of now
            write_mode_value(mode, mode_value)
            mode += 1
            mode_value = read_mode_value(mode)
        else:
            write_mode_value(mode, mode_value)
            mode = 0
            mode_value = read_mode_value(mode)
        print("Mode changed to " + str(mode))
        btn_enc_state = None
    if not btn_porta.value() == 1 and btn_porta_state is None:
        btn_porta_state = 1
    if btn_porta.value() == 1 and btn_porta_state == 1:
        #try:
        print("Start!")
        btn_porta_state = None
        relay.value(1)
        if mode > 0:
            i = mode_value
            while i > 0:
                i -= 1
                print(str(i))  # + "\t" + str(utime.monotonic()))
                utime.sleep(0.1)
        else:
            i = 0
            while i < 900:
                i += 1
                print(str(i))  # + "\t" + str(utime.monotonic()))
                utime.sleep(0.1)
        relay.value(0)
        print("Done!")
        #except Exception as e:
        #    print("ERROR! " + str(e))
        #    relay.value(0)
        utime.sleep(0.001)
