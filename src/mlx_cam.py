"""!
@file mlx_cam.py

RAW VERSION
This version uses a stripped down MLX90640 driver which produces only raw data,
not calibrated data, in order to save memory.

This file contains a wrapper that facilitates the use of a Melexis MLX90640
thermal infrared camera for general use. The wrapper contains a class MLX_Cam
whose use is greatly simplified in comparison to that of the base class,
@c class @c MLX90640, by mwerezak, who has a cool fox avatar, at
@c https://github.com/mwerezak/micropython-mlx90640

To use this code, upload the directory @c mlx90640 from mwerezak with all its
contents to the root directory of your MicroPython device, then copy this file
to the root directory of the MicroPython device.

There's some test code at the bottom of this file which serves as a beginning
example.

@author mwerezak Original files, Summer 2022
@author JR Ridgely Added simplified wrapper class @c MLX_Cam, January 2023
@author Peyton Archibald, Harrison Hirsch Added functionality for interfacing with the dart gun
@copyright (c) 2022 by the authors and released under the GNU Public License,
    version 3.
"""

import utime as time
from machine import Pin, I2C
from mlx90640 import MLX90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, IMAGE_SIZE, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern
from array import array as ar


class MLX_Cam:
    """!
    @brief   Class which wraps an MLX90640 thermal infrared camera driver to
             make it easier to grab and use an image.
    """

    def __init__(self, i2c, address=0x33, pattern=ChessPattern,
                 width=NUM_COLS, height=NUM_ROWS):
        """!
        @brief   Set up an MLX90640 camera.
        @param   i2c An I2C bus which has been set up to talk to the camera;
                 this must be a bus object which has already been set up
        @param   address The address of the camera on the I2C bus (default 0x33)
        @param   pattern The way frames are interleaved, as we read only half
                 the pixels at a time (default ChessPattern)
        @param   width The width of the image in pixels; leave it at default
        @param   height The height of the image in pixels; leave it at default
        """
        ## The I2C bus to which the camera is attached
        self._i2c = i2c
        ## The address of the camera on the I2C bus
        self._addr = address
        ## The pattern for reading the camera, usually ChessPattern
        self._pattern = pattern
        ## The width of the image in pixels, which should be 32
        self._width = width
        ## The height of the image in pixels, which should be 24
        self._height = height

        # The MLX90640 object that does the work
        self._camera = MLX90640(i2c, address)
        self._camera.set_pattern(pattern)
        self._camera.setup()

        ## A local reference to the image object within the camera driver
        self._image = self._camera.raw

    def get_image(self):
        """!
        @brief   Get one image from a MLX90640 camera.
        @details Grab one image from the given camera and return it. Both
                 subframes (the odd checkerboard portions of the image) are
                 grabbed and combined (maybe; this is the raw version, so the
                 combination is sketchy and not fully tested). It is assumed
                 that the camera is in the ChessPattern (default) mode as it
                 probably should be.
        @returns A reference to the image object we've just filled with data
        """
        for subpage in (0, 1):
            while not self._camera.has_data:
                time.sleep_ms(10)
                # print('.', end='')
            image = self._camera.read_image(subpage)

        return image

    def find_max(self, array):
        """!
            @brief                  Finds the hottest pixel in an image taken
            @details                Given an image taken, this method finds the index of the hottest pixel and converts
                                    it to pitch and yaw degrees from the center of the image
            @param  array           The image object to be analyzed
            @return                 The delta x and delta y, in degrees, to the hottest pixel from the center of the
                                    image
        """
        hottest = max(array)
        for p_idx in range(self._width * self._height - 1):
            if array[p_idx] == hottest:
                return [(self._height / 2 - (p_idx // self._width)) * 1.2566,
                        -1.2566 * (self._width / 2 - (self._width - (p_idx % self._width) - 1))]

    # def gaussian_filt(self, array):
    #     matrix = []
    #     temp_row = ar('f', [])
    #     mask = ar('f', [1 / 16, 1 / 8, 1 / 16,
    #                     1 / 8, 1 / 4, 1 / 8,
    #                     1 / 16, 1 / 8, 1 / 16])
    #     filtered_array = ar('f', [])
    #     for p_idx in range(self._width * self._height):
    #         if (p_idx + 1) % 32 == 0:
    #             temp_row.append(array[p_idx])
    #             matrix.append(temp_row)
    #             temp_row = ar('f', [])
    #         else:
    #             temp_row.append(array[p_idx])
    #     for i in range(len(matrix) - 2):
    #         for j in range(len(matrix[i]) - 2):
    #             mask_values = [a * b for a, b in zip(mask[0:3], matrix[i][j:j + 3])] + \
    #                           [a * b for a, b in zip(mask[3:6], matrix[i + 1][j:j + 3])] + \
    #                           [a * b for a, b in zip(mask[6:9], matrix[i + 2][j:j + 3])]
    #             filtered_array.append(sum(mask_values))
    #
    #     return filtered_array
    #
    # def find_person(self, array):
    #     filtered_array = self.gaussian_filt(array)
    #     hottest = max(filtered_array)
    #     for p_idx in range(len(filtered_array)):
    #         if filtered_array[p_idx] == hottest:
    #             return [((self._height - 2) / 2 - (p_idx // (self._width - 2))) * 1.2566,
    #                     -1.2566 * ((self._width - 2) / 2 - ((self._width - 2) - (p_idx % (self._width - 2)) - 1))]


def camera_setup():
    """!
        @brief                  Sets up the camera object
        @details                Sets up I2C and initializes the camera object
        @return                 The camera object
    """
    # The following import is only used to check if we have an STM32 board such
    # as a Pyboard or Nucleo; if not, use a different library
    try:
        from pyb import info

    # Oops, it's not an STM32; assume generic machine.I2C for ESP32 and others
    except ImportError:
        # For ESP32 38-pin cheapo board from NodeMCU, KeeYees, etc.
        i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))

    # OK, we do have an STM32, so just use the default pin assignments for I2C1
    else:
        i2c_bus = I2C(1)

    # print("MXL90640 Easy(ish) Driver Test")

    # Select MLX90640 camera I2C address, normally 0x33, and check the bus
    i2c_address = 0x33
    # scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
    # print(f"I2C Scan: {scanhex}")

    # Create the camera object and set it up in default mode
    cam = MLX_Cam(i2c_bus)
    return cam


def run(cam):
    """!
        @brief                  Takes a picture and finds the hottest pixel, to be sent to the motor controller
        @details                Given a camera object, this method takes a picture and finds the hottest pixel for the
                                purpose of aiming the gun
        @param  cam             The previously initialized camera object
        @return                 The delta x and delta y to the hottest pixel
    """
    # Get an image
    image = cam.get_image()
    deltas = cam.find_max(image)

    return deltas


# The test code sets up the sensor, then grabs and shows an image in a terminal
# every ten and a half seconds or so.
## @cond NO_DOXY don't document the test code in the driver documentation
if __name__ == "__main__":
    camera = camera_setup()
    run(camera)

## @endcond End the block which Doxygen should ignore
