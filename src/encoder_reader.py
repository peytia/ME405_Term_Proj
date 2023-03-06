import pyb

"""!
    @file                       encoder_reader.py
    @brief                      A driver for reading from Quadrature Encoders
    @details                    This is a driver for interfacing with Quadrature Encoders. This driver
                                needs input parameters of the timer which is the proper timer that
                                corresponds to the pins and the 2 channel pins which the encoder outputs.

    @author                     Peyton Archibald
    @author                     Harrison Hirsch
    @date                       January 31, 2023
"""


class EncoderReader:
    """!
        @brief                  Interface with quadrature encoders
        @details                This is a driver for interfacing with Quadrature Encoders. This driver
                                needs input parameters of the timer which is the proper timer that
                                corresponds to the pins and the 2 channel pins which the encoder outputs.
    """

    def __init__(self, pinA, pinB, timer):
        """!
            @brief              Constructs an encoder object
            @details            Upon instantiation, the encoder object is created with the input parameters
                                of the timer and channel pins which the encoder outputs on. Additionally,
                                the position, count, and delta variables are created and zeroed.
            @param  timer       The timer number which the encoder uses
            @param  pinA        The pin A for the encoder which channel 1 output is on
            @param  pinB        The pin B for the encoder which channel 2 output is on.
        """
        print("Creating an encoder reader")
        self.pinA = pyb.Pin(pinA)
        self.pinB = pyb.Pin(pinB)
        self.encodertimer = pyb.Timer(timer, prescaler=0, period=65535)
        self.ch1 = self.encodertimer.channel(1, pyb.Timer.ENC_AB, pin=self.pinA)
        self.ch2 = self.encodertimer.channel(2, pyb.Timer.ENC_AB, pin=self.pinB)

        self.delta = 0
        self.initialCount = 0
        self.count = 0
        self.position = 0

    def update(self):
        """!
            @brief              Updates encoder position and delta
            @details            update() uses the counter from the encoder to update the known position of the encoder and
                                check if increase in counts is greater than half of the period to ensure that the position
                                of the encoder is acurate and does not experience an overload.
        """

        self.initialCount = self.count
        self.count = self.encodertimer.counter()
        self.delta = self.count - self.initialCount
        self.initialCount = self.count
        if self.delta >= 65535 / 2:
            self.delta -= 65535
        elif self.delta <= -65535 / 2:
            self.delta += 65535
        self.position += self.delta

    def read(self):
        """!
            @brief              Returns encoder position and the delta position
            @details            read() first updates the position of the encoder for an accurate position reading
                                and then returns the current recorded position of the encoder. 
            @return             The position of the encoder shaft and the delta position of the encoder shaft.
        """
        self.update()
        return self.position, self.delta

    def zero(self):
        """!
            @brief              Zeros all of the encoder values, including position
            @details            zero() sets the values of position, count, initialCount, and delta to zero
                                which are all used in calculating zero, such that the position of the encoder
                                is set to a true zero
        """
        self.delta = 0
        self.initialCount = 0
        self.count = 0
        self.position = 0

    def set(self, position):
        """!
            @brief              Sets encoder position
            @details            set() sets the position to a given value. As well as delta to zero to set the
                                the true position of the encoder to a value. This can be used to zero the
                                position of the encoder by passing a 0 value through the input parameter
            @param  position    The new position of the encoder shaft
        """
        self.position = position
        self.delta = 0


if __name__ == '__main__':
    pass
