'''!
    @file       mainpage.py
    @brief      Functions as a mainpage file to run with doxygen
    @details    This file will be processed by doxygen to create a main page for navigation and explanitory
                purposes for the term project.

    @author     Peyton Archibald
    @author     Harrison Hirsch
    @date       March 20, 2023

    @mainpage
    @section    SoftwareDesign Software Design
    This page shows the overall current design of the software for the nerf turret. The image below shows a
    task diagram for the turret. This is where we document the share going between the tasks, the frequency
    of the tasks, and the priority of each task over one another. An important note: we are not using any
    queues (at the moment), so any of the solid arrows in the task diagram below indicate a share. A share is
    traditionally indicated by a dashed line.
    @image html task_diagram.png

    In each of the subsections below, a finite state machine is drawn for each corresponding task. While all
    tasks have FSM's, many are very simple and could be excluded. Others, like the controller, is quite a bit
    more complex.

    @subsection  YawTask Yaw Motor Task
    @image html yaw_task.png

    @subsection  PitchTask Pitch Motor Task
    @image html pitch_task.png

    @subsection  FireTask Fire Control Task
    @image html fire_task.png

    @subsection  UserTask User Input Task
    @image html user_task.png

    @subsection  CameraTask Camera Task
    @image html camera_task.png

    @subsection  ControllerTask Controller Task
    @image html controller_task.png
'''