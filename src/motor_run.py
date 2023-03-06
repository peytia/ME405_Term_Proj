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
    # periodic_step_test()            # Rotate one revolution and stop
    step_response_test()            # Run a step response, store the results, and plot the step response


def periodic_step_test():
    """!
        @brief                  Rotate the motor one revolution and stop
        @details                Runs the controller, running closed-loop step response tests in which the setpoint is
                                changed to rotate the motor by one revolution and stop at the final position every 3
                                seconds.
    """
    motor1 = motor_driver.MotorDriver('A10', 'B4', 'B5', 3)  # Set up motor 1
    encoder1 = encoder_reader.EncoderReader('C6', 'C7', 8)  # Set up encoder 1
    setpt = 16348
    controller1 = motor_controller.MotorController(.01, setpt)  # Set up controller 1
    startTime = utime.ticks_ms()        # Begin start time counter
    currTime = 0                        # Allocate memory for current time
    while True:
        try:
            if currTime >= 3000:        # Once the current time reaches 3 seconds
                startTime = utime.ticks_ms()        # Restart start time counter
                setpt += 16348                      # Add one revolution to the setpoint
                controller1.set_setpoint(setpt)     # Set controller setpoint
            encoderPosSpeed = encoder1.read()       # Read current motor position
            desiredDuty = controller1.run(encoderPosSpeed[0])   # Run controller with current position
            motor1.set_duty_cycle(desiredDuty)      # Set motor duty cycle
            utime.sleep_ms(10)                      # Match rate of execution
            stopTime = utime.ticks_ms()             # Begin stop time counter
            currTime = utime.ticks_diff(stopTime, startTime)    # Calculate current time
        except KeyboardInterrupt:
            break       # Stop motor on KeyboardInterrupt
    motor1.set_duty_cycle(0)


def step_response_test():
    """!
        @brief                  Run and record a step response test
        @details                Runs the controller, running closed-loop a step response test. The time and
                                corresponding motor position is stored in a list and written to a serial port to be
                                graphed
    """
    while True:
        motor1 = motor_driver.MotorDriver('A10', 'B4', 'B5', 3)  # Set up motor 1
        encoder1 = encoder_reader.EncoderReader('C6', 'C7', 8)  # Set up encoder 1
        setpt = 16348
        Kp_input = input('Enter a Kp: ')        # Prompt user to enter a proportional gain
        if is_number(Kp_input):             # Test for valid input
            Kp_input = float(Kp_input)
        else:
            raise ValueError('Input must be a number')
        controller1 = motor_controller.MotorController(Kp_input, setpt)  # Set up controller 1
        u2 = pyb.UART(2, baudrate=115200)   # Set up the second USB-serial port
        startTime = utime.ticks_ms()        # Begin start time counter
        currTime = 0                        # Allocate memory for current time
        initial_val_lst = 100 * [0]         # 1 second before step
        final_value_lst = 500 * [24000]     # 5 seconds of about 1.5 revolutions
        step_lst = initial_val_lst + final_value_lst    # Concatenate lists to make step response positions
        storedData = []                     # Allocate memory for stored data
        for value in step_lst:              # For each position in step response
            encoderPosSpeed = encoder1.read()   # Update and read encoder value
            controller1.set_setpoint(value)     # Set controller setpoint to current step response value
            desiredDuty = controller1.run(encoderPosSpeed[0])   # Run controller to calculate duty cycle
            motor1.set_duty_cycle(desiredDuty)  # Set calculated duty cycle
            stopTime = utime.ticks_ms()         # Begin stop time counter
            currTime = utime.ticks_diff(stopTime, startTime)    # Calculate current time
            currPos = encoderPosSpeed[0]        # Current encoder position
            controller1.store_data(storedData, currTime, currPos)   # Store motor position in a data list
            utime.sleep_ms(10)                  # Match rate of execution
        for dataPt in storedData:               # Write stored data to serial port
            u2.write(f'{dataPt[0]}, {dataPt[1]}\r\n')


def is_number(pt):
    """!
        @brief          Helper function to test for valid user input
        @details        This is a helper function to determine if the user input a valid value for Kp. A valid Kp is a
                        floating point number.
        @param  pt      The input to be tested
        @return         A boolean True if the input can be cast to a float, and False otherwise.
    """
    try:
        float(pt)       # Return true if able to cast to a float
        return True
    except ValueError:
        return False    # Return false if not


if __name__ == '__main__':
    main()
