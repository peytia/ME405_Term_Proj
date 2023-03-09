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


def main():
    """!
        @brief                  Method that will be run when the Pyboard is flashed
        @details                This file will be flashed to the Pyboard and used to run the controller, running
                                closed-loop step response tests.
    """
    pass


def move_yaw(degrees):
    yaw_motor = motor_driver.MotorDriver('A10', 'B4', 'B5', 3)  # Set up motor 1
    yaw_encoder = encoder_reader.EncoderReader('C6', 'C7', 8)  # Set up encoder 1
    yaw_controller = motor_controller.MotorController(0.1, 0)  # Set up controller 1
    yield 0
    while True:
        encoderPosSpeed = yaw_encoder.read()  # Update and read encoder value
        yaw_controller.set_setpoint(degrees * 16384 / 360)  # Set controller setpoint to current step response value
        desiredDuty = yaw_controller.run(encoderPosSpeed[0])  # Run controller to calculate duty cycle
        yaw_motor.set_duty_cycle(desiredDuty)  # Set calculated duty cycle
        yield encoderPosSpeed[0] * 360 / 16384


def move_pitch(degrees):
    pitch_motor = motor_driver.MotorDriver('C1', 'A0', 'A1', 5)  # Set up pitch motor
    pitch_encoder = encoder_reader.EncoderReader('B6', 'B7', 4)  # Set up pitch encoder
    pitch_controller = motor_controller.MotorController(0.1, 0)  # Set up pitch controller
    yield 0
    while True:
        encoderPosSpeed = pitch_encoder.read()  # Update and read encoder value
        pitch_controller.set_setpoint(degrees * 16384 / 360)  # Set controller setpoint to current step response value
        desiredDuty = pitch_controller.run(encoderPosSpeed[0])  # Run controller to calculate duty cycle
        pitch_motor.set_duty_cycle(desiredDuty)  # Set calculated duty cycle
        yield encoderPosSpeed[0] * 360 / 16384


if __name__ == '__main__':
    main()
