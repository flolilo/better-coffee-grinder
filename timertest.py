import machine
import utime

interruptCounter = 0
totalInterruptsCounter = 0
pauseCounter = 0

timer = machine.Timer()
dip1 = machine.Pin(2, machine.Pin.IN)
dip2 = machine.Pin(3, machine.Pin.IN)
btn_porta = machine.Pin(4, machine.Pin.IN)
# r = RotaryIRQ(pin_num_clk=5, pin_num_dt=6,
#               min_val=0, max_val=0)
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


def handle_interrupt(timer):
    global interruptCounter
    interruptCounter += 1

time_go = 70
time_pause = 15
btn_enc_state = 0
btn_porta_state = 0

while True:
    if btn_porta.value() != 1 and btn_porta_state == 0:
        btn_porta_state = 1
        print("BUT-")
    if btn_porta.value() == 1 and btn_porta_state == 1:
        btn_porta_state = 0
        print("-TON!")
        utime.sleep(0.2)
        timer.init(freq=10, mode=machine.Timer.PERIODIC, callback=handle_interrupt)
        interruptCounter = 0
        totalInterruptsCounter = 0
        while totalInterruptsCounter < time_go:
            if interruptCounter > 0:
                state = machine.disable_irq()
                interruptCounter -= 1
                machine.enable_irq(state)
                totalInterruptsCounter += 1
                relay.toggle()
                print("Go timer interrupt # " + str(totalInterruptsCounter))
            # TODO: something like stackoverflow.com/a/3150107
            if btn_porta.value() != 1 and btn_porta_state == 0:
                btn_porta_state = 1
                print("but-")
            if btn_porta.value() == 1 and btn_porta_state == 1:
                btn_porta_state = 0
                print("-ton!")
                utime.sleep(0.2)
                timer.deinit()
                interruptCounter = 0
                pauseCounter = 0
                debug_led_btn_porta.value(1)
                timer.init(freq=1, mode=machine.Timer.PERIODIC, callback=handle_interrupt)
                while pauseCounter < time_pause:
                    if interruptCounter > 0:
                        state = machine.disable_irq()
                        interruptCounter -= 1
                        machine.enable_irq(state)
                        pauseCounter += 1
                        relay.toggle()
                        print("Pause timer interrupt # " + str(pauseCounter))
                    if btn_porta.value():
                        timer.deinit()
                        debug_led_btn_porta.value(0)
                        break
                debug_led_btn_porta.value(0)
                timer.init(freq=10, mode=machine.Timer.PERIODIC, callback=handle_interrupt)
            debug_led_dip2.value(1)
        relay.value(0)
        timer.deinit()
        debug_led_dip2.value(0)
        debug_led_dip1.value(0)
