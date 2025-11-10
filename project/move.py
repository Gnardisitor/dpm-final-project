#!/usr/bin/env python3

from math import fabs, pi
from time import sleep

from utils.brick import Motor, wait_ready_sensors

# Initialize motors and sensors
RIGHT_MOTOR = Motor("A")
LEFT_MOTOR = Motor("B")

print("Sensors waiting")
wait_ready_sensors()
print("Sensors ready")

# Measure to find exact values
WHEEL_DIAMETER = 4.3
TURN_DIAMETER = 11.0

# Computed values
WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * pi
TURN_CIRCUMFERENCE = TURN_DIAMETER * pi

# Values for functions
DPS = 540
POLL = 0.01


def move(distance):
    # Check for invalid distance
    if distance == 0:
        return

    # Compute encoder degrees
    encoder_degrees = (distance / WHEEL_CIRCUMFERENCE) * 360
    right_target = RIGHT_MOTOR.get_position() + encoder_degrees
    left_target = LEFT_MOTOR.get_position() + encoder_degrees

    try:
        # Set motors to move
        if distance > 0:
            RIGHT_MOTOR.set_dps(DPS)
            LEFT_MOTOR.set_dps(DPS)
        else:
            RIGHT_MOTOR.set_dps(-DPS)
            LEFT_MOTOR.set_dps(-DPS)

        while True:
            # Check remaining distance
            right_remaining = fabs(right_target - RIGHT_MOTOR.get_position())
            left_remaining = fabs(left_target - LEFT_MOTOR.get_position())

            if right_remaining <= 0 or left_remaining <= 0:
                break

            sleep(POLL)
    finally:
        RIGHT_MOTOR.set_dps(0)
        LEFT_MOTOR.set_dps(0)


def turn(degrees):
    # Check for invalid turn
    if degrees == 0:
        return

    # Compute encoder degrees
    arc_length = degrees / 360 * TURN_CIRCUMFERENCE
    encoder_degrees = (arc_length / WHEEL_CIRCUMFERENCE) * 360
    right_target = RIGHT_MOTOR.get_position() - encoder_degrees
    left_target = LEFT_MOTOR.get_position() + encoder_degrees

    try:
        # Set motors to move
        if degrees > 0:
            RIGHT_MOTOR.set_dps(-DPS)
            LEFT_MOTOR.set_dps(DPS)
        else:
            RIGHT_MOTOR.set_dps(DPS)
            LEFT_MOTOR.set_dps(-DPS)

        while True:
            # Check remaining distance
            right_remaining = fabs(right_target - RIGHT_MOTOR.get_position())
            left_remaining = fabs(left_target - LEFT_MOTOR.get_position())

            if right_remaining <= 0 or left_remaining <= 0:
                break

            sleep(POLL)
    finally:
        RIGHT_MOTOR.set_dps(0)
        LEFT_MOTOR.set_dps(0)


if __name__ == "__main__":
    # Move forward 10 cm then turn 90 degrees to the right
    move(10)
    sleep(1)
    turn(90)
