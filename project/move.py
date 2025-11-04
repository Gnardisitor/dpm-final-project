#!/usr/bin/env python3

from time import sleep

from utils.brick import (
    Motor,
    TouchSensor,
    wait_ready_sensors,
)

print("Program start.\nWaiting for sensors to turn on...")

# 4 sensors 1234
# 4 motors ABCD

# Initialize motors and sensors
RIGHT_MOTOR = Motor("C")
LEFT_MOTOR = Motor("B")
START_DRUM = TouchSensor(1)
EMERGENCY_STOP = TouchSensor(4)

wait_ready_sensors()
print("Done waiting.")


def straight():
    RIGHT_MOTOR.set_dps(720)
    LEFT_MOTOR.set_dps(720)


# def turnRight():
#     while color:
#         RIGHT_MOTOR.set_dps(720)
#         LEFT_MOTOR.set_dps(720)


def stop():
    """
    Main while loop to test the drum motor functionality,
    data is collected seperately using Audacity.
    """

    try:
        while True:
            # Break from loop if emergency stop is pressed
            if EMERGENCY_STOP.is_pressed():
                break

            # Start the drum at 720 dps (120 bpm) if the start drum button is pressed
            # if START_DRUM.is_pressed():
            #    straight()

            # Short delay
            sleep(0.1)
    except BaseException:
        # Avoid errors crashing the program to stop the motor properly
        pass
    finally:
        # Stop the drum motor and exit code
        RIGHT_MOTOR.set_dps(0)
        LEFT_MOTOR.set_dps(0)
        print("Emergency stop")


if __name__ == "__main__":
    straight()
    stop()
