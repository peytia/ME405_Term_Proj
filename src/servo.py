import pyb
import utime


def run():
    pinB3 = pyb.Pin(pyb.Pin.cpu.B3, pyb.Pin.OUT_PP)
    tim2 = pyb.Timer(2, prescaler=79, period=19999)
    ch2 = tim2.channel(2, pyb.Timer.PWM, pin=pinB3)
    ch2.pulse_width(2000)
    utime.sleep(.25)
    ch2.pulse_width(800)


def run2(n):    # No. of darts
    pinB3 = pyb.Pin(pyb.Pin.cpu.B3, pyb.Pin.OUT_PP)
    tim2 = pyb.Timer(2, prescaler=79, period=19999)
    ch2 = tim2.channel(2, pyb.Timer.PWM, pin=pinB3)
    for i in range(n):
        ch2.pulse_width(2000)
        utime.sleep(.25)
        ch2.pulse_width(800)
        utime.sleep(.25)


if __name__ == '__main__':
    run()
