import pyb

button_press = False


def on_button_press():
    global button_press
    button_press = True


def setup():
    pinC13 = pyb.Pin(pyb.Pin.cpu.C13)
    pyb.ExtInt(pinC13, mode=pyb.ExtInt.IRQ_FALLING, pull=pyb.Pin.PULL_NONE, callback=on_button_press)


def main():
    pass


if __name__ == '__main__':
    main()
