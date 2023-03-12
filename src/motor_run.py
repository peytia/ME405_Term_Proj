import motor_driver
import encoder_reader
import motor_controller
import utime
import pyb

"""!
    @file                       motor_run.py
    @brief                      Functions as a main file to run and test code
    @details                    This file will be flashed to the Pyboard and used to run the controller, running
                                closed-loop step response tests.
                                
    @author                     Peyton Archibald
    @author                     Harrison Hirsch
    @date                       February 7, 2023
"""


class Motor:
    def __init__(self, en_pin, in1pin, in2pin, motor_timer, pinA, pinB, encoder_timer, initial_Kp, initial_set_point):
        self.motor = motor_driver.MotorDriver(en_pin, in1pin, in2pin, motor_timer)  # Set up motor
        self.encoder = encoder_reader.EncoderReader(pinA, pinB, encoder_timer)  # Set up encoder
        self.controller = motor_controller.MotorController(initial_Kp, initial_set_point)  # Set up controller


def main():
    """!
        @brief                  Method that will be run when the Pyboard is flashed
        @details                This file will be flashed to the Pyboard and used to run the controller, running
                                closed-loop step response tests.
    """
    pass


def move_yaw(motor, degrees):
    encoderPosSpeed = motor.encoder.read()  # Update and read encoder value
    motor.controller.set_setpoint(degrees * 16384 / 360 * 5.8)  # Set controller setpoint to current step response value
    desiredDuty = motor.controller.run(encoderPosSpeed[0])  # Run controller to calculate duty cycle
    motor.motor.set_duty_cycle(desiredDuty)  # Set calculated duty cycle
    return encoderPosSpeed[0] * 360 / 16384 / 5.8


def move_pitch(motor, degrees):
    encoderPosSpeed = motor.encoder.read()  # Update and read encoder value
    motor.controller.set_setpoint(degrees * 16384 / 360 * 4.2)  # Set controller setpoint to current step response value
    desiredDuty = motor.controller.run(encoderPosSpeed[0])  # Run controller to calculate duty cycle
    motor.motor.set_duty_cycle(desiredDuty)  # Set calculated duty cycle
    return encoderPosSpeed[0] * 360 / 16384 / 4.2


if __name__ == '__main__':
    main()
