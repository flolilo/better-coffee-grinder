# SPDX-License-Identifier: GPL-3.0-only
"""better-coffee-grinder - For a better coffee grinder experience. MicroPython Edition"""
__author__ = "flolilo"
__license__ = "See SPDX-License-Identifier"
__contact__ = "See github.com/flolilo/better-coffee-grinder"
__version__ = "0.1-ALPHA"
try:
    import time
    import rp2
    import machine
    from rotary_irq_rp2 import RotaryIRQ
    from ssd1306 import SSD1306_I2C
    import framebuf
except Exception as e:
    print("Import failed!!! " + str(e))
print("###  Welcome to BCG!  ###\n")

# ? Setting the pins up:
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
try:
    dip1 = machine.Pin(2, machine.Pin.IN)
    dip2 = machine.Pin(3, machine.Pin.IN)
    btn_porta = machine.Pin(4, machine.Pin.IN)
    rotary = RotaryIRQ(pin_num_clk=5, pin_num_dt=6, min_val=0, range_mode=RotaryIRQ.RANGE_UNBOUNDED)
    btn_enc = machine.Pin(7, machine.Pin.IN)
    relay = machine.Pin(29, machine.Pin.OUT)
    # ? I2C (Qwiic) for OLED. NOTE: github.com/micropython/micropython/issues/8167
    # * Use only one of these!
    i2c = machine.SoftI2C(sda=machine.Pin(16), scl=machine.Pin(17), freq=100000)
    # i2c = machine.I2C(id=0, sda=machine.Pin(16), scl=machine.Pin(17), freq=100000)
    # ? Just to find your OLED's address (typically 0x3C or 0x3D) :
    # print(str(i2c.scan()))
    # ? Define the display
    display = SSD1306_I2C(width=128, height=64, i2c=i2c, addr=0x3D)
    display.rotate(True)
    display.invert(0)
    display.contrast(0)
    # ! maybe comment these out for final version?
    debug_led_dip1 = machine.Pin(26, machine.Pin.OUT)
    debug_led_dip2 = machine.Pin(27, machine.Pin.OUT)
    debug_led_btn_porta = machine.Pin(28, machine.Pin.OUT)
    debug_led_btn_enc_pause = machine.Pin(8, machine.Pin.OUT)
except Exception as e:
    print("Could not initiate GPIOs!\t" + str(e))
    raise

debug_led_dip1.value(dip1.value())
debug_led_dip2.value(dip2.value())
debug_led_btn_porta.value(0)
debug_led_btn_enc_pause.value(0)

relay.value(0)
timer_grind = machine.Timer()
timer_button_hyst = machine.Timer()
timer_display = machine.Timer()

""" DEBUG: if ./mode_values gets ruined, uncomment this code for one runtime:
    which_mode_value = [900, 70, 140]
    with open("./mode_values", "w") as f:
        for element in which_mode_value:
            f.write(str(element) + "\n")
"""

display.text('Welcome to BCG!', 4, 23, 1)
display.show()


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
        # ! Scales-Mode: add fourth value to list (e.g. 170 for 17.0 g)
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


def irq_handle_timer_grind(timer_grind):
    global grind_timer_IRQs
    grind_timer_IRQs += 1


def irq_handle_timer_display(timer_display):
    global disp_timer_IRQs
    disp_timer_IRQs += 1


def irq_handle_btn_porta(_):
    global porta_btn_IRQs
    porta_btn_IRQs += 1


def irq_handle_btn_encoder(_):
    global encoder_btn_IRQs
    encoder_btn_IRQs += 1


# ? Read the DIPs:
""" DIP modes:
    OFF/OFF 0   manual
    ON/OFF  1   single
    OFF/ON  2   double
    ON/ON   3   manual (NOT IMPLEMENTED: weight)
"""
current_mode = dip1.value() + (2 * dip2.value())
modes_plain_english = ["Manual", "Single", "Double"]
if current_mode == 3:
    current_mode = 0
print("DIPs set to mode\t" + str(current_mode))

# * Denominator for timers in Hz ([sec]^-1). Must be integer.
# *   Check variables granularity, sane_maximum_times and mode_values if you change this!
timer_denominator = 10
# * Sane maximum times for your machine in 1/timer_denominator secs.
# *   - Scales-Mode: Add fourth value (e.g. 500 for 50.0 g)
# *   - First is in fact used for manual mode and should be the maximum time the grinder's motor
# *     may run continuously. E.g. the sticker on the Eureka Mignon MCI says
sane_maximum_times = [900, 450, 900]
# * Time until pausing results in abortion of operation. Also in 1/timer_denominator secs.
time_pause = 70
# * Granularity for encoder
# *   Higher values make for faster, coarser changes. Must be integer - in case you need finer
# *     values, change variable timer_denominator to higher value (e.g. 100)
granularity = 1

# * Logos as frame buffers:
# * Credit: "coffee bean": flolilo
fb_coffee_bean = framebuf.FrameBuffer(bytearray(b'\x00~\x00\x00\xc3\x00\x01\x99\x80\x03\x08\xc0\x06'
                                                b'\x0c`\x0c\x040\x0c\x040\x18\x04\x18\x18\x04\x18'
                                                b'\x18\x04\x180\x0c\x0c0\x18\x0c0\x10\x0c0\x10\x0c0'
                                                b'\x18\x0c\x18\x08\x18\x18\x0c\x18\x18\x04\x18\x0c'
                                                b'\x040\x06\x0c`\x03\x08\xc0\x01\x89\x80\x00\xc3'
                                                b'\x00\x00~\x00'), 24, 24, framebuf.MONO_HLSB)
# * Credit: "M": flolilo
fb_manual = framebuf.FrameBuffer(bytearray(b'\x00\x00\x00p\x00\x0ex\x00\x1e|\x00>n\x00vg\x00\xe6c'
                                           b'\x81\xc6a\xc3\x86`\xe7\x06`~\x06`<\x06`\x18\x06`\x00'
                                           b'\x06`\x00\x06`\x00\x06`\x00\x06`\x00\x06`\x00\x06`\x00'
                                           b'\x06`\x00\x06`\x00\x06`\x00\x06`\x00\x06\x00\x00\x00'),
                                           24, 24, framebuf.MONO_HLSB)

# * Read saved values for modes:
mode_values = read_mode_values(current_mode)

rot_val_old = rotary.value()

# * Starting the hardware timer:
grind_timer_IRQs = 0
timer_grind.init(freq=timer_denominator, mode=timer_grind.PERIODIC, callback=irq_handle_timer_grind)
disp_timer_IRQs = 0
timer_display.init(freq=1, mode=timer_display.PERIODIC, callback=irq_handle_timer_display)
# * IRQ for buttons:
porta_btn_IRQs = 0
btn_porta.irq(handler=irq_handle_btn_porta, trigger=machine.Pin.IRQ_RISING, hard=False)
encoder_btn_IRQs = 0
btn_enc.irq(handler=irq_handle_btn_encoder, trigger=machine.Pin.IRQ_RISING, hard=False)

# * Variable to stop permanent screen re-drawing. Spawned as True so it refreshes on first loop.
refresh_display = True

# ? Perma-Loop
while True:
    # ? Timer change:
    rot_val_new = rotary.value()
    if current_mode != 0 and rot_val_old != rot_val_new:
        if 1 < mode_values[current_mode] < sane_maximum_times[current_mode]:
            mode_values[current_mode] += ((rot_val_old - rot_val_new) * granularity)
        elif mode_values[current_mode] >= sane_maximum_times[current_mode]:
            mode_values[current_mode] = 1
        elif mode_values[current_mode] <= 1:
            mode_values[current_mode] = sane_maximum_times[current_mode]
        print('Timer:\t', str(mode_values[current_mode]))
        rot_val_old = rot_val_new
        refresh_display = True

    # ? Mode change:
    if encoder_btn_IRQs > 0:
        if current_mode < 2:  # ! No mode 3 as of now
            current_mode += 1
            debug_led_btn_porta.value(0)
        else:
            current_mode = 0
            debug_led_btn_porta.value(1)

        print("Mode changed to " + str(current_mode))
        mode_values = read_mode_values(current_mode)
        refresh_display = True
        encoder_btn_IRQs = 0

    # ? Start/Stop:
    if porta_btn_IRQs > 0:
        # try:
        display.poweron()
        write_mode_values(mode_values)
        print("Start grinding!")
        relay.value(1)
        grind_timer_IRQs = 0

        i = mode_values[current_mode]
        # * Double-break  CREDIT: stackoverflow.com/a/6564670
        double_breaker = False
        while i > 0:
            if grind_timer_IRQs > 0:
                state = machine.disable_irq()
                grind_timer_IRQs -= 1
                machine.enable_irq(state)
                i -= 1
                print("  |>  " + str(i))  # + "\t" + str(time.monotonic()))
                display.fill(0)
                display.text("|> GRIND", 0, 0, 1)
                display.text(str(i)[0:-1] + "." + str(i)[-1] + " s", 0, 48, 1)
                display.show()
            # ? Pause
            if porta_btn_IRQs > 1:
                relay.value(0)
                grind_timer_IRQs = 0
                counter_pause_interrupts = 0
                debug_led_btn_enc_pause.value(1)
                print("Pause grinding")
                while True:
                    if grind_timer_IRQs > 0:
                        state = machine.disable_irq()
                        grind_timer_IRQs -= 1
                        machine.enable_irq(state)
                        counter_pause_interrupts += 1
                        print("  ||  " + str(counter_pause_interrupts))
                        display.fill(0)
                        display.text("|| PAUSE", 0, 0, 1)
                        display.text(str(int((time_pause - counter_pause_interrupts) / 10)), 0, 48, 1)
                        display.show()
                    if porta_btn_IRQs > 2:
                        print("Pause ended")
                        porta_btn_IRQs = 1
                        relay.value(1)
                        break
                    if counter_pause_interrupts >= time_pause:
                        print("Abort (pause timed out)")
                        double_breaker = True
                        break
                debug_led_btn_enc_pause.value(0)
            if double_breaker:
                relay.value(0)
                porta_btn_IRQs = 0
                break
        relay.value(0)
        print("Done grinding!")
        refresh_display = True
        debug_led_btn_porta.value(0)
        # except Exception as e:
        #    print("ERROR! " + str(e))
        #    relay.value(0)
        porta_btn_IRQs = 0
    if refresh_display:
        print("LCD working...")
        display_time_value = str(mode_values[current_mode])
        try:
            # pass
            display.fill(0)
            display.blit(fb_coffee_bean, 100, 10)
            display.blit(fb_manual, 100, 40)
            display.text(str(modes_plain_english[current_mode]), 0, 0, 1)
            if int(display_time_value) > 99:
                display.text(display_time_value[0:-1] + "." + display_time_value[-1] + " s", 0, 48, 1)
            elif 99 >= int(display_time_value) > 9:
                display.text(display_time_value[0:-1] + "." + display_time_value[-1] + " s", 8, 48, 1)
            else:
                display.text(display_time_value[0:-1] + "." + display_time_value[-1] + " s", 16, 48, 1)
            display.show()
            display.poweron()
            disp_timer_IRQs = 0
        except Exception as e:
            print("LCD error - " + str(e))
        refresh_display = False
    elif not refresh_display and disp_timer_IRQs > 900:
        print("LCD standby...")
        try:
            display.poweroff()
        except Exception as e:
            print("Poweroff failed - " + str(e))
        disp_timer_IRQs = 0
    time.sleep_us(100)
