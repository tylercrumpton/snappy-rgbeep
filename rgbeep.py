D1 = 5
D2 = 6
D3 = 20
D4 = 21
D5 = 26
D6 = 18
D7 = 25
D8 = 16

LP301_BUTTON1 = 5
LP301_BUTTON2 = 6

LP301_LED1 = 13
LP301_LED2 = 14

RGBEEP_BUTTON1 = D1
RGBEEP_BUTTON2 = D2
RGBEEP_BUTTON3 = D3
RGBEEP_BUTTON4 = D4

LED_CLK = D5
LED_DATA = D7

NUM_PIXELS = 16

PRESSED = False
RELEASED = True
current_button_state = RELEASED
color_selected = None

count = 0
brightness = 31
rainbow_step = 0
do_run_rainbow = False
do_run_rainbow_2 = False

def set_color(color_string):
    led_data_string = ""
    for i in xrange(len(color_string) / 3):
        led_data_string += chr(0b11100000 | brightness)
        led_data_string += color_string[i*3:i*3+3]
    spiWrite("\x00\x00\x00\x00" + led_data_string + "\xff\xff\xff\xff")
    return led_data_string

def set_all(color):
    color_string = ""
    for i in xrange(NUM_PIXELS):
        color_string += color
    return len(set_color(color_string))

def get_rainbow_offset(offset):
    offset = offset % 256
    if offset < 85:
        return chr(255 - offset * 3) + chr(0) + chr(offset * 3)
    elif offset < 170:
        offset -= 85
        return chr(0) + chr(offset * 3) + chr(255 - offset *3)
    else:
        offset -= 170
        return chr(offset * 3) + chr(255 - offset * 3) + chr(0)

def set_rainbow(offset):
    color_string = ""
    for i in xrange(NUM_PIXELS):
        color_string += get_rainbow_offset((i*256/NUM_PIXELS) + offset)
    set_color(color_string)

@setHook(HOOK_10MS)
def run_rainbow():
    global rainbow_step
    if do_run_rainbow:
        rainbow_step += 1
        rainbow_step %= 256
        set_rainbow(rainbow_step)
    elif do_run_rainbow_2:
        rainbow_step += 1
        rainbow_step %= 256
        set_all(get_rainbow_offset(rainbow_step))

@setHook(HOOK_100MS)
def reset_release():
    global current_button_state
    if readPin(RGBEEP_BUTTON1) and readPin(RGBEEP_BUTTON2) and readPin(RGBEEP_BUTTON3) and readPin(RGBEEP_BUTTON4):
        current_button_state = RELEASED

def start_rainbow():
    global do_run_rainbow, do_run_rainbow_2
    do_run_rainbow_2 = False
    do_run_rainbow = True

def start_rainbow_2():
    global do_run_rainbow_2, do_run_rainbow
    do_run_rainbow = False
    do_run_rainbow_2 = True

@setHook(HOOK_STARTUP)
def startup():
    clock_polarity = False
    clock_phase = False
    is_msb_first = True
    is_four_wire = True
    spiInit(clock_polarity, clock_phase, is_msb_first, is_four_wire)


    setPinDir(RGBEEP_BUTTON1, False)
    setPinPullup(RGBEEP_BUTTON1, True)
    monitorPin(RGBEEP_BUTTON1, True)

    setPinDir(RGBEEP_BUTTON2, False)
    setPinPullup(RGBEEP_BUTTON2, True)
    monitorPin(RGBEEP_BUTTON2, True)

    setPinDir(RGBEEP_BUTTON3, False)
    setPinPullup(RGBEEP_BUTTON3, True)
    monitorPin(RGBEEP_BUTTON3, True)

    setPinDir(RGBEEP_BUTTON4, False)
    setPinPullup(RGBEEP_BUTTON4, True)
    monitorPin(RGBEEP_BUTTON4, True)

    start_rainbow_2()

@setHook(HOOK_GPIN)
def button_pressed(pin, is_high):
    global current_button_state, color_selected, rainbow_step, do_run_rainbow_2

    if not readPin(RGBEEP_BUTTON1) or not readPin(RGBEEP_BUTTON2) or not readPin(RGBEEP_BUTTON3) or not readPin(RGBEEP_BUTTON4):

        if color_selected is None and do_run_rainbow_2:
            color_selected = get_rainbow_offset(rainbow_step)
            do_run_rainbow_2 = False
        elif current_button_state is RELEASED:
            mcastRpc(1, 2, "report_press", pin, is_high)
            current_button_state = PRESSED

    else:
        current_button_state = RELEASED

def get_count():
    global count
    return count
