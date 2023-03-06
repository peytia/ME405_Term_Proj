import pyb

"""!
    @file                       motor_driver.py
    @brief                      This class implements a DC motor driver for an ME405 kit.
    @details                    This is a driver for interfacing with a brushed DC motor through
                                the L6206 motor "shield" or "hat" for the ME 405 kit.

    @author                     Peyton Archibald
    @author                     Harrison Hirsch
    @date                       January 31, 2023
"""


class MotorDriver:
    """!
    @brief                      This class implements a DC motor driver for an ME405 kit.
    @details                    This is a driver for interfacing with a brushed DC motor through
                                the L6206 motor "shield" or "hat" for the ME 405 kit.
    """

    def __init__(self, en_pin, in1pin, in2pin, timer):
        """!
            @brief              Constructs an motor object
            @details            Upon instantiation, the motor object is created with the input parameters
                                of the timer and input pins which the motor driver uses to control the
                                speed of the motor using a PWM signal. Additionally, upon instantiation,
                                the enable pin for the motor controler is set to high, enabling the motor
                                for use.
            @param  en_pin      The enable pin which is used to enable the motor controler
            @param  in1pin      The pin 1 for the motor
            @param  in2pin      The pin 2 for the
        """

        print("Creating a motor driver")
        # Enable pin
        self.enable_pin = pyb.Pin(en_pin, pyb.Pin.OUT_OD, pyb.Pin.PULL_UP)  # Setting up the enable pin, and setting it high
        self.enable_pin.high()
        # Input pin 1
        self.input1pin = pyb.Pin(in1pin, pyb.Pin.OUT_PP)  # Defining the pin 1 of the motor
        # Input pin 2
        self.input2pin = pyb.Pin(in2pin, pyb.Pin.OUT_PP)  # Defining the pin 2 of the motor

        self.motortimer = pyb.Timer(timer, freq=20000)  # Setting up the timer channel for PWM signal
        self.CCW = self.motortimer.channel(1, pyb.Timer.PWM, pin=self.input1pin)  # Setting up channels for motor
        self.CW = self.motortimer.channel(2, pyb.Timer.PWM, pin=self.input2pin)

    def set_duty_cycle(self, level):
        """!
            @brief 				Sets the duty cycle of the PWM signal to a motor
            @details			This method sets the duty cycle to be sent to the motor to the given
                                level. Positive values cause torque in one direction, negative values
                                in the opposite direction.
            @param level		A signed integer holding the duty cycle of the voltage sent to the motor
        """
        # print(f"Setting duty cycle to {level}")

        # This below section of code is for determining if the duty cycle is saturated
        # and needs to be set to 100
        if level > 100:
            level = 100
        elif level < -100:
            level = -100
        # Then the sign of the level determines the direction and magnitude determines power
        # If zero or anything else is passed in, the motor is stopped.
        if -100 <= level < 0:
            self.CW.pulse_width_percent(-level)
            self.CCW.pulse_width_percent(0)
        elif 0 < level <= 100:
            self.CW.pulse_width_percent(0)
            self.CCW.pulse_width_percent(level)
        else:
            self.CW.pulse_width_percent(0)
            self.CCW.pulse_width_percent(0)


if __name__ == '__main__':
    motor1 = MotorDriver(pyb.Pin.cpu.A10, pyb.Pin.cpu.B4, pyb.Pin.cpu.B5, 3)
    motor1.set_duty_cycle(100)
