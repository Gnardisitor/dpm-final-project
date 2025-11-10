#!/usr/bin/env python3


from math import fabs, pi
from multiprocessing import Process
from time import sleep

from utils.brick import Motor, TouchSensor, wait_ready_sensors

# Initialize motors and sensors
STOP = TouchSensor(1)
RIGHT_MOTOR = Motor("A")
LEFT_MOTOR = Motor("B")

print("Sensors waiting")
wait_ready_sensors()
print("Sensors ready")

# All current values are temporary and need to be measured.

# Coordinate system values
COORDINATE = (0, 0)
ORIENTATION = 0  # Horizontal facing right in degrees

# Measured values
WHEEL_DIAMETER = 4.3
TURN_DIAMETER = 11.0
TILE_SIZE = 10.0

# Computed values
WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * pi
TURN_CIRCUMFERENCE = TURN_DIAMETER * pi

# Values for functions
DPS = 540
POLL = 0.01


def move(distance: float) -> None:
    """
    Moves the robot forward by a certain distance.

    Parameters
    ----------
    distance : float
        The distance to move in centimeters. Positive values move forward, and negative values move backward.
    """

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


def turn(degrees: int) -> None:
    """
    Turns the robot by a certain number of degrees.

    Parameters
    ----------
    degrees : int
        The number of degrees to turn. Positive values turn right, and negative values turn left.
    """

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


def move_to(x: int, y: int) -> None:
    """
    Moves the robot to the specific tile in the coordinate system using brute force movement.

    Parameters
    ----------
    x : int
        The x-coordinate to move to in centimeters.
    y : int
        The y-coordinate to move to in centimeters.
    """

    global COORDINATE
    global ORIENTATION

    # Check for valid coordinates
    if x < 0 or y < 0:
        print("Cannot have negative coordinates")
        return

    if x > 5 or y > 5:
        print("Coordinates exceed grid size")
        return

    # Compute delta
    delta = (COORDINATE[0] - x, COORDINATE[1] - y)

    # Check for valid orientation
    if ORIENTATION % 90 != 0:
        print("Orientation is not aligned to cardinal directions")
        return

    # If facing right
    if ORIENTATION == 0:
        # Move in x direction
        move(delta[0])

        # Turn to face y direction
        if delta[1] > 0:
            turn(-90)
            ORIENTATION += 90
        elif delta[1] < 0:
            turn(90)
            ORIENTATION -= 90

        # Move in y direction
        move(abs(delta[1]))

    # If facing up
    elif ORIENTATION == 90:
        # Move in y direction
        move(delta[1])

        # Turn to face x direction
        if delta[0] > 0:
            turn(90)
            ORIENTATION -= 90
        elif delta[0] < 0:
            turn(-90)
            ORIENTATION += 90

        # Move in x direction
        move(abs(delta[0]))

    # If facing left
    elif ORIENTATION == 180:
        # Move in x direction
        move(-delta[0])

        # Turn to face y direction
        if delta[1] > 0:
            turn(90)
            ORIENTATION -= 90
        elif delta[1] < 0:
            turn(-90)
            ORIENTATION += 90

        # Move in y direction
        move(abs(delta[1]))

    # If facing down
    elif ORIENTATION == 270:
        # Move in y direction
        move(-delta[1])

        # Turn to face x direction
        if delta[0] > 0:
            turn(-90)
            ORIENTATION += 90
        elif delta[0] < 0:
            turn(90)
            ORIENTATION -= 90

        # Move in x direction
        move(abs(delta[0]))

    # Normalize orientation
    ORIENTATION = ORIENTATION % 360
    COORDINATE = (x, y)


def interrupt() -> bool:
    """
    Checks whether or not the main function is being interrupted by the emergency stop.

    Returns
    -------
    bool
        Whether or not there is an interrupt.
    """

    return STOP.is_pressed()


def main_move():
    """
    This is the main function of the code that is ran by the process. Add movement here.
    """

    # Move forward 10 cm then turn 90 degrees to the right
    move(10)
    sleep(1)
    turn(90)


if __name__ == "__main__":
    # Create process for movement
    move_process = Process(target=main_move)
    move_process.start()
    print("Movement process started")

    # Wait for movement to finish
    while move_process.is_alive() and not interrupt():
        sleep(POLL)

    move_process.terminate()
    move_process.join()
    print("Movement process ended")
