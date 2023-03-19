"""!
    @file                       motor_run.py
    @brief                      A wrapper to set up a motor with one method
    @details                    This file sets up the motor driver, encoder, and controller all with one method call.
                                This allows for quick instantiation and method calling

    @author                     Peyton Archibald
    @author                     Harrison Hirsch
    @date                       March 14, 2023
"""

import motor_driver
import encoder_reader
import motor_controller


class Motor:
    """!
        @brief                  A class for creating a motor object, which includes a driver, encoder, and controller
        @details                Instead of having to separately instantiate a motor driver, encoder, and controller,
                                this class wraps them all into one motor object. All the same methods can be called from
                                this motor object
    """
    def __init__(self, en_pin, in1pin, in2pin, motor_timer, pinA, pinB, encoder_timer, initial_Kp, initial_set_point):
        """!
            @brief                      Constructs a motor object
            @details                    Takes all the necessary pins and automatically instantiates everything needed to
                                        control a motor
            @param  en_pin              The enable pin which is used to enable the motor controller
            @param  in1pin              The pin 1 for the motor
            @param  in2pin              The pin 2 for the motor
            @param  motor_timer         The timer number that the motor uses
            @param  pinA                The pin A for the encoder which channel 1 output is on
            @param  pinB                The pin B for the encoder which channel 2 output is on.
            @param  encoder_timer       The timer number that the encoder uses
            @param  initial_Kp          The proportional gain to be used
            @param  initial_set_point   The initial setpoint to aim for

        """
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
    """!
        @brief              Moves the yaw motor by a specified number of degrees
        @details            Updates and reads the yaw motor encoder value, sets the controller setpoint to the desired
                            number of degrees, runs the controller to calculate and set the duty cycle. The input and
                            output is converted between gun rotation degrees and motor encoder tics. This method is
                            meant to be run in a loop, continuously updating the yaw desired position
        @param  motor       The motor object that is to be controlled
        @param  degrees     The desired end yaw position of the gun
        @return             The current motor yaw position, in gun degrees
    """
    encoderPosSpeed = motor.encoder.read()  # Update and read encoder value
    motor.controller.set_setpoint(degrees * 16384 / 360 * 5.8)  # Set controller setpoint to current step response value
    desiredDuty = motor.controller.run(encoderPosSpeed[0])  # Run controller to calculate duty cycle
    motor.motor.set_duty_cycle(desiredDuty)  # Set calculated duty cycle
    return encoderPosSpeed[0] * 360 / 16384 / 5.8


def move_pitch(motor, degrees):
    """!
        @brief              Moves the pitch motor by a specified number of degrees
        @details            Updates and reads the pitch motor encoder value, sets the controller setpoint to the desired
                            number of degrees, runs the controller to calculate and set the duty cycle. The input and
                            output is converted between gun rotation degrees and motor encoder tics. This method is
                            meant to be run in a loop, continuously updating the pitch desired position
        @param  motor       The motor object that is to be controlled
        @param  degrees     The desired end pitch position of the gun
        @return             The current motor pitch position, in gun degrees
    """
    encoderPosSpeed = motor.encoder.read()  # Update and read encoder value
    motor.controller.set_setpoint(degrees * 16384 / 360 * 4.2)  # Set controller setpoint to current step response value
    desiredDuty = motor.controller.run(encoderPosSpeed[0])  # Run controller to calculate duty cycle
    motor.motor.set_duty_cycle(desiredDuty)  # Set calculated duty cycle
    return encoderPosSpeed[0] * 360 / 16384 / 4.2


if __name__ == '__main__':
    main()
