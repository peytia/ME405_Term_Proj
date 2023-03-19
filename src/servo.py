"""!
    @file           servo.py
    @brief          Sets up and runs the servo to push a dart from the magazine into the flywheels
    @details        This file sets up the pins and timer to run a servo with PWM. Once the gun is on target,
                    the servo will rotate 180 degrees to push a dart through the spinning flywheels and then return to
                    the original position to prepare to fire again.

    @author         Peyton Archibald
    @author         Harrison Hirsch
    @date           March 14, 2023
"""

import pyb
import utime


def run():
    """!
        @brief      Sets up and runs the servo to push a dart from the magazine into the flywheels
        @details    This file sets up the pins and timer to run a servo with PWM. Once the gun is on target,
                    the servo will rotate 180 degrees to push a dart through the spinning flywheels and then return to
                    the original position to prepare to fire again.
    """
    pinB3 = pyb.Pin(pyb.Pin.cpu.B3, pyb.Pin.OUT_PP)
    tim2 = pyb.Timer(2, prescaler=79, period=19999)
    ch2 = tim2.channel(2, pyb.Timer.PWM, pin=pinB3)
    ch2.pulse_width(2000)
    utime.sleep(.25)
    ch2.pulse_width(800)


# def run2(n):    # No. of darts
#     pinB3 = pyb.Pin(pyb.Pin.cpu.B3, pyb.Pin.OUT_PP)
#     tim2 = pyb.Timer(2, prescaler=79, period=19999)
#     ch2 = tim2.channel(2, pyb.Timer.PWM, pin=pinB3)
#     for i in range(n):
#         ch2.pulse_width(2000)
#         utime.sleep(.25)
#         ch2.pulse_width(800)
#         utime.sleep(.25)


if __name__ == '__main__':
    run()
