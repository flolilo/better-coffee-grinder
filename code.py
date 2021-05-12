import time
import board
from digitalio import DigitalInOut, Direction
import rotaryio
import time

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
dip1 = DigitalInOut(board.D2)
dip1.direction = Direction.INPUT
dip2 = DigitalInOut(board.D3)
dip2.direction = Direction.INPUT
btn_porta = DigitalInOut(board.D4)
btn_porta.direction = Direction.INPUT
encoder = rotaryio.IncrementalEncoder(board.D5, board.D6)
btn_enc = DigitalInOut(board.D7)
btn_enc.direction = Direction.INPUT

relay = DigitalInOut(board.D29)
relay.direction = Direction.OUTPUT

debug_led_dip1 = DigitalInOut(board.D26)
debug_led_dip1.direction = Direction.OUTPUT
debug_led_dip2 = DigitalInOut(board.D27)
debug_led_dip2.direction = Direction.OUTPUT
debug_led_btn_porta = DigitalInOut(board.D28)
debug_led_btn_porta.direction = Direction.OUTPUT
debug_led_btn_enc = DigitalInOut(board.D9)
debug_led_btn_enc.direction = Direction.OUTPUT


# Read the DIPs:
mode = 0
""" DIP modes:
    OFF/OFF 0   manual
    ON/OFF  1   single
    OFF/ON  2   double
    ON/ON   3   manual (TODO: weight)
"""
if dip1.value:
    mode += 1
if dip2.value:
    mode += 2
print("DIP set to mode " + str(mode))


# Code so far:
timer_time = 7.0
btn_enc_state = None
btn_porta_state = None
last_position = encoder.position
while True:
    current_position = encoder.position
    position_change = current_position - last_position
    if position_change != 0:
        if timer_time <= 0.1 and position_change < 0:
            timer_time = 60.1
        elif timer_time >= 60.0 and position_change > 0:
            timer_time = 0.0
        timer_time = round(timer_time + position_change / 10, 1)
        print(str(timer_time))
    last_position = current_position
    if not btn_enc.value and btn_enc_state is None:
        btn_enc_state = "pressed"
    if btn_enc.value and btn_enc_state == "pressed":
        if mode < 3:
            mode += 1
        else:
            mode = 0
        print("Mode changed to " + str(mode))
        btn_enc_state = None
    if not btn_porta.value and btn_porta_state is None:
        btn_porta_state = "pressed"
    if btn_porta.value and btn_porta_state == "pressed":
        print("Start!")
        btn_porta_state = None
        relay.value = True
        i = timer_time
        while i > 0:
            i -= 0.1
            print(str(i))
            time.sleep(0.1)
        print("Done!")
