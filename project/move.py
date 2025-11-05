#!/usr/bin/env python3

from time import sleep

from utils.brick import (
    Motor,
    wait_ready_sensors,
)

print("Program start.\nWaiting for sensors to turn on...")

# Initialize motors and sensors
RIGHT_MOTOR = Motor("A")
LEFT_MOTOR = Motor("B")

wait_ready_sensors()
print("Done waiting.")


def move_straight_degrees(degrees, dps=720, poll=0.01):
    """
    Drive straight so each wheel turns 'degrees'.
    Positive degrees move forward; negative move backward.
    dps: target speed in degrees per second for each motor.
    """
    # Determine direction from 'degrees'
    direction = 1 if degrees >= 0 else -1
    speed = abs(dps) * direction

    # Read starting encoder positions
    start_r = RIGHT_MOTOR.get_position()
    start_l = LEFT_MOTOR.get_position()

    # Compute absolute targets for each wheel
    target_r = start_r + degrees
    target_l = start_l + degrees

    # Start both motors
    RIGHT_MOTOR.set_dps(speed)
    LEFT_MOTOR.set_dps(speed)

    try:
        while True:
            pos_r = RIGHT_MOTOR.get_position()
            pos_l = LEFT_MOTOR.get_position()

            # Remaining distance along the commanded direction
            rem_r = (target_r - pos_r) * direction
            rem_l = (target_l - pos_l) * direction

            # Stop once either wheel has met or passed its target
            if rem_r <= 0 or rem_l <= 0:
                break

            sleep(poll)
    finally:
        # Hard stop both motors
        RIGHT_MOTOR.set_dps(0)
        LEFT_MOTOR.set_dps(0)


def turn_degrees(degrees, dps=720, poll=0.01):
    """
    Turn in place by 'degrees'.
    Positive degrees turn right (RIGHT motor backward, LEFT motor forward);
    negative degrees turn left (RIGHT motor forward, LEFT motor backward).
    dps: target speed in degrees per second for each motor.
    """
    abs_deg = abs(degrees)
    if degrees >= 0:
        # Turn right: RIGHT backward, LEFT forward
        speed_r = -abs(dps)
        speed_l = abs(dps)
        start_r = RIGHT_MOTOR.get_position()
        start_l = LEFT_MOTOR.get_position()
        target_r = start_r - abs_deg
        target_l = start_l + abs_deg
    else:
        # Turn left: RIGHT forward, LEFT backward
        speed_r = abs(dps)
        speed_l = -abs(dps)
        start_r = RIGHT_MOTOR.get_position()
        start_l = LEFT_MOTOR.get_position()
        target_r = start_r + abs_deg
        target_l = start_l - abs_deg

    # Start both motors
    RIGHT_MOTOR.set_dps(speed_r)
    LEFT_MOTOR.set_dps(speed_l)

    try:
        while True:
            pos_r = RIGHT_MOTOR.get_position()
            pos_l = LEFT_MOTOR.get_position()

            # Remaining distance along the commanded direction
            rem_r = (target_r - pos_r) * (1 if speed_r >= 0 else -1)
            rem_l = (target_l - pos_l) * (1 if speed_l >= 0 else -1)

            # Stop once either wheel has met or passed its target
            if rem_r <= 0 or rem_l <= 0:
                break

            sleep(poll)
    finally:
        # Hard stop both motors
        RIGHT_MOTOR.set_dps(0)
        LEFT_MOTOR.set_dps(0)


if __name__ == "__main__":
    # move_straight_degrees(360)
    turn_degrees(90)
