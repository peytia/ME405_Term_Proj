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
    s_pitch_pos = task_share.Share('f', thread_protect=True, name='pitch_pos')
    s_take_picture = task_share.Share('f', thread_protect=True, name='take_picture')
    s_picture_taken = task_share.Share('f', thread_protect=True, name='picture_taken')
    s_delta_x = task_share.Share('f', thread_protect=True, name='delta_x')
    s_delta_y = task_share.Share('f', thread_protect=True, name='delta_y')
    s_on_target = task_share.Share('f', thread_protect=True, name='on_target')

    shares = s_button_pushed, s_yaw_pos, s_pitch_pos, s_take_picture, s_picture_taken, s_delta_x, s_delta_y, s_on_target

    init_task0 = cotask.Task(task0_init, name='Task_0', priority=100, shares=shares)
    yaw_task1 = cotask.Task(task1_yaw, name='Task_1', priority=11, period=10, shares=shares)
    # camera_task2 = cotask.Task(task2_camera, name='Task_2', priority=5, period=1000, shares=shares)
    pitch_task3 = cotask.Task(task3_pitch, name='Task_3', priority=10, period=10, shares=shares)
    # fire_task4 = cotask.Task(task4_fire, name='Task_4', priority=5, period=1000, shares=shares)
    # button_task5 = cotask.Task(task5_button, name='Task_5', priority=20, shares=shares)

    cotask.task_list.append(init_task0)
    cotask.task_list.append(yaw_task1)
    # cotask.task_list.append(camera_task2)
    cotask.task_list.append(pitch_task3)
    # cotask.task_list.append(fire_task4)
    # cotask.task_list.append(button_task5)

    gc.collect()

    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            break
    print('Done')


def task0_init(shares):     # Initialization of shares on startup
    s_button_pushed, s_yaw_pos, s_pitch_pos, s_take_picture, s_picture_taken, s_delta_x, s_delta_y, s_on_target = shares
    s_button_pushed.put(True)  # Button is not pushed
    s_yaw_pos.put(0)            # Yaw at 0 degrees
    s_pitch_pos.put(0)          # Pitch at 0 degrees
    s_take_picture.put(False)   # Don't take picture
    s_picture_taken.put(False)  # Picture not taken
    s_delta_x.put(0)            # Delta x at 0
    s_delta_y.put(0)            # Delta y at 0
    s_on_target.put(False)      # Not on target


def task1_yaw(shares):
    s_button_pushed, s_yaw_pos, s_pitch_pos, s_take_picture, s_picture_taken, s_delta_x, s_delta_y, s_on_target = shares

    yaw_motor = motor_run.Motor('A10', 'B4', 'B5', 3, 'C6', 'C7', 8, 0.1, 0)    # Initialize yaw motor

    S1 = 1  # Hold position stationary
    S2 = 2  # Initial 180deg spin
    S3 = 3  # Aim

    state = S1
    while True:

        if state == S1:
            motor_run.move_yaw(yaw_motor, s_yaw_pos.get())      # Hold at current position
            if s_button_pushed.get() and not s_picture_taken.get():     # If button pushed and picture not taken
                state = S2              # Spin 180 state
            elif s_button_pushed.get() and s_picture_taken.get():       # If button pushed and picture taken
                state = S3              # Aim state
            else:
                pass                    # Continue holding

        elif state == S2:
            s_yaw_pos.put(motor_run.move_yaw(yaw_motor, 45))     # Spin 180deg
            s_button_pushed.put(False)      # Un-push button
            if s_yaw_pos.get() >= 45:
                state = S1      # Hold
            else:
                pass

        elif state == S3:
            pass                # Calcs needed here to figure out rotation angle based on camera

        yield 0


# def task2_camera(shares):
#     s_button_pushed, s_yaw_pos, s_pitch_pos, s_take_picture, s_picture_taken, s_delta_x, s_delta_y, s_on_target = shares
#
#     S0 = 0  # Camera setup
#     S1 = 1  # Idle
#     S2 = 2  # Take picture
#
#     state = S0
#     while True:
#
#         if state == S0:
#             mlx_cam.run()   # Camera init
#             state = S1
#
#         elif state == S1:
#             if s_take_picture.get():    # If ready to take picture
#                 state = S2  # Take picture state
#             else:
#                 pass    # Continue idle
#
#         elif state == S2:
#             [delta_y, delta_x] = mlx_cam.run()  # Take picture
#             s_delta_x.put(delta_x)
#             s_delta_y.put(delta_y)
#             s_take_picture.put(False)
#             state = S1  # Return to idle


def task3_pitch(shares):
    s_button_pushed, s_yaw_pos, s_pitch_pos, s_take_picture, s_picture_taken, s_delta_x, s_delta_y, s_on_target = shares

    pitch_motor = motor_run.Motor('C1', 'A0', 'A1', 5, 'B6', 'B7', 4, 0.1, 0)  # Initialize pitch motor

    S1 = 1  # Hold position stationary
    S2 = 2  # Aim

    state = S1
    while True:

        if state == S1:
            motor_run.move_pitch(pitch_motor, s_pitch_pos.get())  # Hold at current position
            # if s_picture_taken.get():  # If picture taken
            if s_button_pushed.get():  # If picture taken
                state = S2  # Aim state
            else:
                pass        # Continue holding

        elif state == S2:
            s_pitch_pos.put(motor_run.move_pitch(pitch_motor, 10))  # Spin 180deg
            s_button_pushed.put(False)  # Un-push button
            if s_pitch_pos.get() >= 10:
                state = S1  # Hold
            else:
                pass
            # pass            # Calcs needed here to figure out rotation angle based on camera

        yield 0


# def task4_fire(shares):
#     s_button_pushed, s_yaw_pos, s_pitch_pos, s_take_picture, s_picture_taken, s_delta_x, s_delta_y, s_on_target = shares
#
#     S1 = 1  # Idle
#     S2 = 2  # Fire
#
#     state = S1
#     while True:
#
#         if state == S1:
#             if s_on_target.get():   # if aiming at target:
#                 state = S2  # Fire state
#             else:
#                 pass    # Continue idle
#
#         elif state == S2:     # Fire state
#             servo.run()     # Actuate servo
#             state = S1      # Return to idle state


# def task5_button(shares):
#     S1 = 1  # Idle
#     S2 = 2  # Button pushed
#     pass


if __name__ == '__main__':
    main()
