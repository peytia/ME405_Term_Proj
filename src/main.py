import mlx_cam
import gc
import motor_run
import servo
import cotask
import task_share


def main():
    # motor_run.move_yaw(30)
    # motor_run.move_pitch(10)
    # mlx_cam.run()
    # servo.run2(9)

    s_button_pushed = task_share.Share('f', thread_protect=True, name='button_pushed')
    s_yaw_pos = task_share.Share('f', thread_protect=True, name='yaw_pos')
    s_yaw_vel = task_share.Share('f', thread_protect=True, name='yaw_vel')
    s_pitch_pos = task_share.Share('f', thread_protect=True, name='pitch_pos')
    s_pitch_vel = task_share.Share('f', thread_protect=True, name='pitch_vel')
    s_desired_pos_x = task_share.Share('f', thread_protect=True, name='desired_pos_x')
    s_desired_pos_y = task_share.Share('f', thread_protect=True, name='desired_pos_y')
    s_on_target = task_share.Share('f', thread_protect=True, name='on_target')

    shares = s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target

    init_task0 = cotask.Task(task0_init, name='Task_0', priority=100, shares=shares)
    yaw_task1 = cotask.Task(task1_yaw, name='Task_1', priority=11, period=10, shares=shares)
    camera_task2 = cotask.Task(task2_camera, name='Task_2', priority=9, period=500, shares=shares)
    pitch_task3 = cotask.Task(task3_pitch, name='Task_3', priority=10, period=10, shares=shares)
    fire_task4 = cotask.Task(task4_fire, name='Task_4', priority=5, period=100, shares=shares)
    # button_task5 = cotask.Task(task5_button, name='Task_5', priority=20, shares=shares)

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
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target = shares
    s_button_pushed.put(True)       # Button is not pushed
    s_yaw_pos.put(0)                # Yaw at 0 degrees
    s_yaw_vel.put(0)                # Yaw velocity 0
    s_pitch_pos.put(0)              # Pitch at 0 degrees
    s_pitch_vel.put(0)              # Pitch velocity 0
    s_desired_pos_x.put(180)        # Desired x at 180
    s_desired_pos_y.put(10)         # Desired y at 10
    s_on_target.put(False)          # Not on target


def task1_yaw(shares):
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target = shares

    yaw_motor = motor_run.Motor('A10', 'B4', 'B5', 3, 'C6', 'C7', 8, 0.1, 0)    # Initialize yaw motor

    while True:

        s_yaw_pos.put(motor_run.move_yaw(yaw_motor, s_desired_pos_x.get()))
        s_yaw_vel.put(yaw_motor.encoder.read()[1])

        yield 0


def task2_camera(shares):
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target = shares

    camera = mlx_cam.camera_setup()

    S1 = 1  # Idle
    S2 = 2  # Take picture

    state = S1
    while True:

        if state == S1:
            if s_yaw_vel.get() == 0 and s_pitch_vel.get() == 0:    # If ready to take picture
                state = S2  # Take picture state

        elif state == S2:
            [delta_y, delta_x] = mlx_cam.run(camera)  # Take picture
            print(delta_x, delta_y)
            if (-5 < delta_x < 5) and (-5 < delta_y < 5):
                s_on_target.put(True)
                print('Ready to fire')
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
            print('Picture taken')
            state = S1  # Return to idle

        yield 0


def task3_pitch(shares):
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target = shares

    pitch_motor = motor_run.Motor('C1', 'A0', 'A1', 5, 'B6', 'B7', 4, 0.1, 0)  # Initialize pitch motor

    while True:

        s_pitch_pos.put(motor_run.move_pitch(pitch_motor, s_desired_pos_y.get()))
        s_yaw_vel.put(pitch_motor.encoder.read()[1])

        yield 0


def task4_fire(shares):
    s_button_pushed, s_yaw_pos, s_yaw_vel, s_pitch_pos, s_pitch_vel, s_desired_pos_x, s_desired_pos_y, s_on_target = shares

    S1 = 1  # Idle
    S2 = 2  # Fire

    state = S1
    while True:

        if state == S1:
            if s_on_target.get():   # if aiming at target:
                state = S2  # Fire state

        elif state == S2:     # Fire state
            print('Firing')
            servo.run()     # Actuate servo
            s_on_target.put(False)
            state = S1      # Return to idle state

        yield 0


# def task5_button(shares):
#     S1 = 1  # Idle
#     S2 = 2  # Button pushed
#     pass


if __name__ == '__main__':
    main()
