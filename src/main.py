"""!
    @file           main.py
    @details        This file contains a program that runs some tasks, and some
                    inter-task communication variables. The tasks set up two separate
                    motors, run each of them through a different step response, and
                    outputs the results to a serial port.

    @author         Peyton Archibald
    @author         Harrison Hirsch
    @date           March 14, 2023
"""

import utime
import mlx_cam
import gc
import motor_run
import servo
import cotask
import task_share


def main():
    input('Press enter to start')
    utime.sleep(5)

    # motor_run.move_yaw(30)
    # motor_run.move_pitch(10)
    # mlx_cam.run()
    # servo.run2(9)

    s_button_pushed = task_share.Share('h', thread_protect=True, name='button_pushed')
    s_yaw_pos = task_share.Share('f', thread_protect=True, name='yaw_pos')
    s_yaw_vel = task_share.Share('f', thread_protect=True, name='yaw_vel')
    s_pitch_pos = task_share.Share('f', thread_protect=True, name='pitch_pos')
    s_pitch_vel = task_share.Share('f', thread_protect=True, name='pitch_vel')
    s_desired_pos_x = task_share.Share('f', thread_protect=True, name='desired_pos_x')
    s_desired_pos_y = task_share.Share('f', thread_protect=True, name='desired_pos_y')
    s_on_target = task_share.Share('h', thread_protect=True, name='on_target')
    s_fired = task_share.Share('h', thread_protect=True, name='fired')

    shares = s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target, s_fired

    init_task0 = cotask.Task(task0_init, name='Task_0', priority=100, shares=shares)
    yaw_task1 = cotask.Task(task1_yaw, name='Task_1', priority=11, period=10, shares=shares)
    camera_task2 = cotask.Task(task2_camera, name='Task_2', priority=9, period=100, shares=shares)
    pitch_task3 = cotask.Task(task3_pitch, name='Task_3', priority=10, period=10, shares=shares)
    fire_task4 = cotask.Task(task4_fire, name='Task_4', priority=12, period=50, shares=shares)
    # button_task5 = cotask.Task(task5_button, name='Task_5', priority=200, shares=shares)

    cotask.task_list.append(init_task0)
    cotask.task_list.append(yaw_task1)
    cotask.task_list.append(camera_task2)
    cotask.task_list.append(pitch_task3)
    cotask.task_list.append(fire_task4)
    # cotask.task_list.append(button_task5)

    gc.collect()

    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break
    print('Done')


def task0_init(shares):     # Initialization of shares on startup
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target, s_fired = shares

    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target, s_fired = shares
    s_button_pushed.put(True)       # Button is not pushed
    s_yaw_pos.put(0)                # Yaw at 0 degrees
    s_yaw_vel.put(0)                # Yaw velocity 0
    s_pitch_pos.put(0)              # Pitch at 0 degrees
    s_pitch_vel.put(0)              # Pitch velocity 0
    s_desired_pos_x.put(180)        # Desired x at 180
    s_desired_pos_y.put(0)         # Desired y at 10
    s_on_target.put(False)          # Not on target
    s_fired.put(0)                  # Not fired


def task1_yaw(shares):
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target, s_fired = shares

    yaw_motor = motor_run.Motor('A10', 'B4', 'B5', 3, 'C6', 'C7', 8, 0.1, 0)    # Initialize yaw motor

    while True:
        if not s_on_target.get():
            s_yaw_pos.put(motor_run.move_yaw(yaw_motor, s_desired_pos_x.get()))
            s_yaw_vel.put(yaw_motor.encoder.read()[1])
        else:
            motor_run.move_yaw(yaw_motor, s_yaw_pos.get())
            print('Motor locked')
        yield 0


def task2_camera(shares):
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target, s_fired = shares

    camera = mlx_cam.camera_setup()
    # start_time = utime.ticks_ms()

    S1 = 1  # Idle
    S2 = 2  # Take picture
    S3 = 3  # Return

    picture_precount = 0
    state = S1
    while True:

        if state == S1:
            # print(s_yaw_vel.get(), s_pitch_vel.get())
            # if s_yaw_vel.get() == 0 and s_pitch_vel.get() == 0:    # If ready to take picture
            if (s_desired_pos_x.get() - 2) < s_yaw_pos.get() < (s_desired_pos_x.get() + 2) and (s_desired_pos_y.get() - 2) < s_pitch_pos.get() < (s_desired_pos_y.get() + 2):
                # print('Zero velocity')
                picture_precount += 1
            else:
                picture_precount = 0
            if picture_precount == 10:
                state = S2  # Take picture state
                picture_precount = 0

        if state == S2 and not s_on_target.get():
            [delta_y, delta_x] = mlx_cam.run(camera)  # Take picture
            print('Picture taken')
            print(delta_x, delta_y)
            # stop_time = utime.ticks_ms()
            # diff_time = utime.ticks_diff(stop_time, start_time)
            # print(diff_time)
            if (-10 < delta_x < 10) and (-10 < delta_y < 10):
                s_on_target.put(True)
                s_desired_pos_y.put(s_pitch_pos.get())
                s_desired_pos_x.put(s_yaw_pos.get())
                print('Ready to fire')
                # state = S3
                yield 0
            desired_x = s_yaw_pos.get() - delta_x
            if desired_x < 90:
                desired_x = 90
            elif desired_x > 270:
                desired_x = 270
            desired_y = s_pitch_pos.get() + delta_y
            if desired_y < -5:
                desired_y = -5
            elif desired_y > 15:
                desired_y = 15
            s_desired_pos_x.put(desired_x)
            s_desired_pos_y.put(desired_y)
            state = S1  # Return to idle
        else:
            state = S1
        if state == S3:
            print('State 3')
            if s_fired.get():
                # s_desired_pos_x.put(0)
                # s_desired_pos_y.put(0)
                s_fired.put(False)
            else:
                pass

        yield 0


def task3_pitch(shares):
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target, s_fired = shares

    pitch_motor = motor_run.Motor('C1', 'A0', 'A1', 5, 'B6', 'B7', 4, 0.1, 0)  # Initialize pitch motor

    while True:
        print(s_desired_pos_y.get())
        if not s_on_target.get():
            s_pitch_pos.put(motor_run.move_pitch(pitch_motor, s_desired_pos_y.get()))
            s_yaw_vel.put(pitch_motor.encoder.read()[1])
        else:
            motor_run.move_pitch(pitch_motor, s_pitch_pos.get())

        yield 0


def task4_fire(shares):
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target, s_fired = shares

    S1 = 1  # Idle

    state = S1
    while True:
        print('fire check')
        if s_on_target.get():
            print('Firing')
            servo.run()  # Actuate servo
            s_on_target.put(False)
            s_fired.put(True)
        # if state == S1:
        #     if s_on_target.get():   # if aiming at target:
        #         state = S2  # Fire state
        #
        # elif state == S2:     # Fire state
        #     print('Firing')
        #     servo.run()     # Actuate servo
        #     s_on_target.put(False)
        #     s_fired.put(True)
        #     state = S1      # Return to idle state

        yield 0


if __name__ == '__main__':
    main()
