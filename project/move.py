from math import isclose, pi
from multiprocessing import Process
from time import sleep

from color import get_color
from utils.brick import Motor, TouchSensor, wait_ready_sensors

# Initialize motors and sensors
STOP = TouchSensor(3)
RIGHT_MOTOR = Motor("C")
LEFT_MOTOR = Motor("B")

print("Sensors waiting")
wait_ready_sensors()
print("Sensors ready")

# Coordinate system values (tiles go from 1 to 5)
COORDINATE = (1, 1)
ORIENTATION = 0  # Horizontal facing right in degrees
AT_OFFICE = False

# Measured values
WHEEL_DIAMETER = 4.2
TURN_DIAMETER = 17.0
TILE_SIZE = 25

# Computed values
DISTANCE_TO_DEGREE = 360 / (pi * WHEEL_DIAMETER)
DEGREE_TO_ROTATION = TURN_DIAMETER / WHEEL_DIAMETER

# Values for functions
MAX_DELTA = 1
DPS = 540
POWER = DPS / 1250 * 100
POLL = 0.01


def initiate() -> None:
    """
    Initiates the motors.
    """

    try:
        # Reset encoders and set max speed and power
        RIGHT_MOTOR.reset_encoder()
        LEFT_MOTOR.reset_encoder()
        RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
        LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    except BaseException:
        pass


def wait() -> None:
    """
    Waits until both motors have stopped moving.
    """

    global AT_OFFICE

    # Wait until the motor start moving
    while isclose(RIGHT_MOTOR.get_speed(), 0):
        sleep(POLL)

    # Wait until the motor stop moving
    set_flag = False
    while not isclose(RIGHT_MOTOR.get_speed(), 0):
        if get_color() == "orange" and not set_flag:
            AT_OFFICE = not AT_OFFICE
            set_flag = True
        sleep(POLL)

    if AT_OFFICE:
        print("The robot is at the door of an office!")


def forward() -> None:
    """
    Moves the robot forward indefinitely.
    """

    RIGHT_MOTOR.set_dps(DPS)
    LEFT_MOTOR.set_dps(DPS)


def backward() -> None:
    """
    Moves the robot backward indefinitely.
    """

    RIGHT_MOTOR.set_dps(-DPS)
    LEFT_MOTOR.set_dps(-DPS)


def left() -> None:
    """
    Turns the robot left indefinitely.
    """

    RIGHT_MOTOR.set_dps(DPS)
    LEFT_MOTOR.set_dps(-DPS)


def right() -> None:
    """
    Turns the robot right indefinitely.
    """

    RIGHT_MOTOR.set_dps(-DPS)
    LEFT_MOTOR.set_dps(DPS)


def stop() -> None:
    """
    Stops the robot's movement.
    """

    RIGHT_MOTOR.set_dps(0)
    LEFT_MOTOR.set_dps(0)


def move(distance: float) -> None:
    """
    Moves the robot forward by a certain distance.

    Parameters
    ----------
    distance : float
        The distance to move in centimeters. Positive values move forward, and negative values move backward.
    """

    global AT_OFFICE

    # Check for invalid distance
    if isclose(distance, 0) or AT_OFFICE:
        return

    # Compute encoder degrees
    encoder_degrees = int(distance * DISTANCE_TO_DEGREE)

    try:
        # Set motors to move
        if distance > 0:
            forward()
        else:
            # Set limits (makes moving backward properly)
            RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
            LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
            backward()

        # Set wanted position
        RIGHT_MOTOR.set_position_relative(encoder_degrees)
        LEFT_MOTOR.set_position_relative(encoder_degrees)
        wait()
    finally:
        stop()


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
    encoder_degrees = int(degrees * DEGREE_TO_ROTATION)

    try:
        # Set motors to move
        if degrees > 0:
            right()
        else:
            left()

        # Set limits (makes turning work properly)
        RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
        LEFT_MOTOR.set_limits(dps=DPS, power=POWER)

        # Set wanted position
        RIGHT_MOTOR.set_position_relative(-encoder_degrees)
        LEFT_MOTOR.set_position_relative(encoder_degrees)
        wait()
    finally:
        stop()


def goto(x: int, y: int) -> None:
    """
    Moves the robot to the specific tile in the coordinate system using simple brute force movement.

    Parameters
    ----------
    x : int
        The x-coordinate to move to.
    y : int
        The y-coordinate to move to.
    """

    global COORDINATE
    global ORIENTATION

    # Check for valid coordinates
    if x < 1 or y < 1:
        print("Cannot have negative coordinates")
        return

    if x > 5 or y > 5:
        print("Coordinates exceed grid size")
        return

    # Compute delta
    delta = (x - COORDINATE[0], y - COORDINATE[1])

    # Check for valid orientation
    if ORIENTATION % 90 != 0:
        print("Orientation is not aligned to cardinal directions")
        return

    # If facing right
    if ORIENTATION == 0:
        # Move in x direction
        move(delta[0] * TILE_SIZE)

        sleep(1)

        # Turn to face y direction
        if delta[1] > 0:
            turn(-90)
            ORIENTATION += 90
        elif delta[1] < 0:
            turn(90)
            ORIENTATION -= 90

        sleep(1)

        # Move in y direction
        move(abs(delta[1]) * TILE_SIZE)

    # If facing up
    elif ORIENTATION == 90:
        # Move in y direction
        move(delta[1] * TILE_SIZE)

        sleep(1)

        # Turn to face x direction
        if delta[0] > 0:
            turn(90)
            ORIENTATION -= 90
        elif delta[0] < 0:
            turn(-90)
            ORIENTATION += 90

        sleep(1)

        # Move in x direction
        move(abs(delta[0]) * TILE_SIZE)

    # If facing left
    elif ORIENTATION == 180:
        # Move in x direction
        move(-delta[0] * TILE_SIZE)

        sleep(1)

        # Turn to face y direction
        if delta[1] > 0:
            turn(90)
            ORIENTATION -= 90
        elif delta[1] < 0:
            turn(-90)
            ORIENTATION += 90

        sleep(1)

        # Move in y direction
        move(abs(delta[1]) * TILE_SIZE)

    # If facing down
    elif ORIENTATION == 270:
        # Move in y direction
        move(-delta[1] * TILE_SIZE)

        sleep(1)

        # Turn to face x direction
        if delta[0] > 0:
            turn(-90)
            ORIENTATION += 90
        elif delta[0] < 0:
            turn(90)
            ORIENTATION -= 90

        sleep(1)

        # Move in x direction
        move(abs(delta[0]) * TILE_SIZE)

    # Normalize orientation
    ORIENTATION = ORIENTATION % 360
    COORDINATE = (x, y)

    print(f"At {COORDINATE[0]}, {COORDINATE[1]} rotated {ORIENTATION} degrees.")


def interrupt() -> bool:
    """
    Checks whether or not the main function is being interrupted by the emergency stop.

    Returns
    -------
    bool
        Whether or not there is an interrupt.
    """

    return STOP.is_pressed()


def main_move() -> None:
    """
    This is the main function of the code that is ran by the process. Add movement here.
    """

    global ORIENTATION
    global AT_OFFICE

    # Goto first office
    initiate()
    goto(2, 2)

    # Go back to front of office
    goto(2, 1)
    turn(90)
    ORIENTATION = 0

    # Goto second office
    goto(4, 2)


if __name__ == "__main__":
    # Create process for movement
    move_process = Process(target=main_move)
    move_process.start()
    print("Movement process started")

    # Wait for movement to finish
    while move_process.is_alive() and not interrupt():
        sleep(POLL)

    stop()
    print("Movement process stopping")
    move_process.terminate()
    move_process.join()
    print("Movement process ended")
