from math import isclose, pi
from multiprocessing import Process
from time import sleep

from color import get_color, is_black
from utils import sound
from utils.brick import EV3UltrasonicSensor, Motor, TouchSensor, wait_ready_sensors

# Initialize motors and sensors
STOP = TouchSensor(3)
RIGHT_MOTOR = Motor("C")
LEFT_MOTOR = Motor("B")
CONVEYER_MOTOR = Motor("A")
ULTRASONIC_SENSOR = EV3UltrasonicSensor(1)

print("Sensors waiting")
wait_ready_sensors()
print("Sensors ready")

# Coordinate system values (tiles go from 1 to 5)
COORDINATE = (1, 1)
ORIENTATION = 0  # Horizontal facing right in degrees
AT_OFFICE = False

DELIVERIES = 0

# Measured values
WHEEL_DIAMETER = 4.2
TURN_DIAMETER = 16.2
TILE_SIZE = 25

# Computed values
DISTANCE_TO_DEGREE = 360 / (pi * WHEEL_DIAMETER)
DEGREE_TO_ROTATION = TURN_DIAMETER / WHEEL_DIAMETER

# Values for functions
MAX_DELTA = 1
DPS = 450
POWER = DPS / 1250 * 100
POLL = 0.01

NOTES = [
    sound.Sound(duration=0.5, pitch="C5", volume=95),
    sound.Sound(duration=0.5, pitch="D5", volume=95),
    sound.Sound(duration=0.5, pitch="E5", volume=95),
    sound.Sound(duration=0.5, pitch="G5", volume=95),
]


def play_sound(note):
    """
    Play the wanted note on the speaker.

    Parameters
    ----------
    note : int
        Wanted index of note to play.
    """

    NOTES[note].play()
    NOTES[note].wait_done()


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


def wait_in_office() -> None:
    """
    Waits until both motors have stopped moving.
    """

    # Wait until the motor start moving
    while isclose(RIGHT_MOTOR.get_speed(), 0):
        sleep(POLL)

    while not isclose(RIGHT_MOTOR.get_speed(), 0):
        sleep(POLL)


def wait_drop() -> None:
    """
    Waits until both motors have stopped moving.
    """

    global AT_OFFICE

    # Wait until the motor start moving
    while isclose(CONVEYER_MOTOR.get_speed(), 0):
        sleep(POLL)

    while not isclose(CONVEYER_MOTOR.get_speed(), 0):
        sleep(POLL)


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


def move_straight_in_office(distance: float) -> None:
    """
    Moves the robot forward by a certain distance.

    Parameters
    ----------
    distance : float
        The distance to move in centimeters. Positive values move forward, and negative values move backward.
    """

    # Check for invalid distance
    if isclose(distance, 0):
        return

    # Compute encoder degrees
    encoder_degrees = int(distance * DISTANCE_TO_DEGREE)

    try:
        # Set motors to move
        if distance > 0:
            forward()
        else:
            # Set limits (makes moving backward properly)
            # RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
            # LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
            backward()

        # Set wanted position
        RIGHT_MOTOR.set_position_relative(encoder_degrees)
        LEFT_MOTOR.set_position_relative(encoder_degrees)
        wait_in_office()
    finally:
        stop()


def move_back_in_office(distance: float) -> None:
    """
    Moves the robot forward by a certain distance.

    Parameters
    ----------
    distance : float
        The distance to move in centimeters. Positive values move forward, and negative values move backward.
    """

    # Check for invalid distance
    if isclose(distance, 0):
        return

    # Compute encoder degrees
    encoder_degrees = int(distance * DISTANCE_TO_DEGREE)

    RIGHT_MOTOR.set_dps(-DPS)
    LEFT_MOTOR.set_dps(-DPS)

    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)

    # Set wanted position
    RIGHT_MOTOR.set_position_relative(encoder_degrees)
    LEFT_MOTOR.set_position_relative(encoder_degrees)
    wait_in_office()
    stop()


def left_motor_only(distance):
    if isclose(distance, 0):
        return

    # Compute encoder degrees
    encoder_degrees = int(distance * DISTANCE_TO_DEGREE)

    LEFT_MOTOR.set_dps(+DPS)

    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)

    # Set wanted position
    LEFT_MOTOR.set_position_relative(encoder_degrees)
    wait_in_office()
    stop()


def right_motor_only(distance):
    if isclose(distance, 0):
        return

    # Compute encoder degrees
    encoder_degrees = int(distance * DISTANCE_TO_DEGREE)

    RIGHT_MOTOR.set_dps(+DPS)

    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)

    # Set wanted position
    RIGHT_MOTOR.set_position_relative(encoder_degrees)
    wait_in_office()
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


def check_red(encoder_degrees):
    red_found = False
    right()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-encoder_degrees)
    LEFT_MOTOR.set_position_relative(encoder_degrees)

    # Wait until the motor start moving
    while isclose(RIGHT_MOTOR.get_speed(), 0):
        sleep(POLL)

    # Wait until the motor stop moving or detect a sticker
    while not isclose(RIGHT_MOTOR.get_speed(), 0):
        color = get_color()
        if color == "red":
            red_found = True
        sleep(POLL)

    stop()
    # Sweep to the left
    left()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(1.5 * encoder_degrees)
    LEFT_MOTOR.set_position_relative(-1.5 * encoder_degrees)

    # Wait until the motor start moving
    while isclose(RIGHT_MOTOR.get_speed(), 0):
        sleep(POLL)

    # Wait until the motor stop moving or detect a sticker
    while not isclose(RIGHT_MOTOR.get_speed(), 0):
        color = get_color()
        if color == "red":
            red_found = True
        sleep(POLL)

    stop()
    right()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-encoder_degrees)
    LEFT_MOTOR.set_position_relative(encoder_degrees)

    # Wait until the motor start moving
    while isclose(RIGHT_MOTOR.get_speed(), 0):
        sleep(POLL)

    # Wait until the motor stop moving or detect a sticker
    while not isclose(RIGHT_MOTOR.get_speed(), 0):
        color = get_color()
        if color == "red":
            red_found = True
        sleep(POLL)
    if red_found:
        print("Found red")
    return red_found


def green_sweep(encoder_degrees: int) -> bool:
    sleep(0.2)
    move_straight_in_office(2)
    sleep(0.3)

    right()
    start_degrees_right = RIGHT_MOTOR.get_position()
    start_degrees_left = LEFT_MOTOR.get_position()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-encoder_degrees)
    LEFT_MOTOR.set_position_relative(encoder_degrees)

    # Wait until the motor start moving
    while (isclose(RIGHT_MOTOR.get_speed(), 0)) or (isclose(LEFT_MOTOR.get_speed(), 0)):
        sleep(POLL)

    # Wait until the motor stop moving or detect a sticker
    while (not isclose(RIGHT_MOTOR.get_speed(), 0)) or not (
        isclose(LEFT_MOTOR.get_speed(), 0)
    ):
        color = get_color()
        if color == "green":
            print("Detected green sticker during sweep.")
            stop()
            end_degrees_right = RIGHT_MOTOR.get_position()
            end_degrees_left = LEFT_MOTOR.get_position()
            move_back_right = start_degrees_right - end_degrees_right
            move_back_left = start_degrees_left - end_degrees_left
            return [True, move_back_right, move_back_left]
        sleep(POLL)

    stop()
    sleep(0.3)

    # Sweep to the left
    left()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(2 * encoder_degrees)
    LEFT_MOTOR.set_position_relative(-2 * encoder_degrees)

    # Wait until the motor start moving
    while (isclose(RIGHT_MOTOR.get_speed(), 0)) or (isclose(LEFT_MOTOR.get_speed(), 0)):
        sleep(POLL)

    # Wait until the motor stop moving or detect a sticker
    while (not isclose(RIGHT_MOTOR.get_speed(), 0)) or not (
        isclose(LEFT_MOTOR.get_speed(), 0)
    ):
        color = get_color()
        if color == "green":
            print("Detected green sticker during sweep.")
            stop()
            end_degrees_right = RIGHT_MOTOR.get_position()
            end_degrees_left = LEFT_MOTOR.get_position()
            move_back_right = start_degrees_right - end_degrees_right
            move_back_left = start_degrees_left - end_degrees_left
            return [True, move_back_right, move_back_left]
        sleep(POLL)

    stop()
    sleep(0.3)

    right()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-encoder_degrees)
    LEFT_MOTOR.set_position_relative(encoder_degrees)

    # Wait until the motor start moving
    while (isclose(RIGHT_MOTOR.get_speed(), 0)) or (isclose(LEFT_MOTOR.get_speed(), 0)):
        sleep(POLL)

    # Wait until the motor stop moving or detect a sticker
    while (not isclose(RIGHT_MOTOR.get_speed(), 0)) or not (
        isclose(LEFT_MOTOR.get_speed(), 0)
    ):
        color = get_color()
        if color == "green":
            print("Detected green sticker during sweep.")
            stop()
            end_degrees_right = RIGHT_MOTOR.get_position()
            end_degrees_left = LEFT_MOTOR.get_position()
            move_back_right = start_degrees_right - end_degrees_right
            move_back_left = start_degrees_left - end_degrees_left
            return [True, move_back_right, move_back_left]
        sleep(POLL)

    stop()
    sleep(0.3)

    return [False, 0, 0]


def check_green(sweep_degrees):
    encoder_degrees = int(sweep_degrees * DEGREE_TO_ROTATION)
    count = 0
    found_green = False
    while count < 10:
        count += 1
        found_green_tuple = green_sweep(encoder_degrees)
        found_green = found_green_tuple[0]
        if found_green:
            break
    print(f"{count}")
    return [found_green, found_green_tuple[1], found_green_tuple[2], count]


def drop_block():
    """
    Drops a single block from the conveyor belt.
    """

    global DELIVERIES

    # Move slightly to the right
    sleep(0.4)
    right()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-90)
    LEFT_MOTOR.set_position_relative(90)
    wait_in_office()
    stop()
    sleep(0.1)

    # Run conveyor belt to drop block
    CONVEYER_MOTOR.set_dps(-0.6 * DPS)
    CONVEYER_MOTOR.set_limits(dps=0.6 * DPS, power=POWER)
    CONVEYER_MOTOR.set_position_relative(150)
    wait_drop()
    CONVEYER_MOTOR.set_dps(0)
    sleep(0.1)

    CONVEYER_MOTOR.set_dps(0.6 * DPS)
    CONVEYER_MOTOR.set_limits(dps=0.6 * DPS, power=POWER)
    CONVEYER_MOTOR.set_position_relative(-90)
    wait_drop()
    CONVEYER_MOTOR.set_dps(0)
    sleep(0.1)

    # Increment deliveries completed
    DELIVERIES += 1


def black_sweep(encoder_degrees: int) -> bool:
    """
    Sweeps equally in both directions and stops once the black line is found.

    Parameters
    ----------
    encoder_degrees : int
        The maximum rotation in encoder degrees to sweep in each direction.

    Returns
    -------
    bool
        Whether or not the black line was found.
    """
    right()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-encoder_degrees)
    LEFT_MOTOR.set_position_relative(encoder_degrees)

    # Wait until the motor start moving
    while (isclose(RIGHT_MOTOR.get_speed(), 0)) or (isclose(LEFT_MOTOR.get_speed(), 0)):
        sleep(POLL)

    # Wait until the motor stop moving or detect a sticker
    while (not isclose(RIGHT_MOTOR.get_speed(), 0)) or not (
        isclose(LEFT_MOTOR.get_speed(), 0)
    ):
        if is_black():
            print("Detected black line during sweep.")
            stop()
            return True
        sleep(POLL)

    stop()

    # Sweep to the left
    left()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(2 * encoder_degrees)
    LEFT_MOTOR.set_position_relative(-2 * encoder_degrees)

    # Wait until the motor start moving
    while (isclose(RIGHT_MOTOR.get_speed(), 0)) or (isclose(LEFT_MOTOR.get_speed(), 0)):
        sleep(POLL)

    # Wait until the motor stop moving or detect a sticker
    while (not isclose(RIGHT_MOTOR.get_speed(), 0)) or not (
        isclose(LEFT_MOTOR.get_speed(), 0)
    ):
        if is_black():
            print("Detected black line during sweep.")
            stop()
            return True
        sleep(POLL)

    stop()

    right()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-encoder_degrees)
    LEFT_MOTOR.set_position_relative(encoder_degrees)

    # Wait until the motor start moving
    while (isclose(RIGHT_MOTOR.get_speed(), 0)) or (isclose(LEFT_MOTOR.get_speed(), 0)):
        sleep(POLL)

    # Wait until the motor stop moving or detect a sticker
    while (not isclose(RIGHT_MOTOR.get_speed(), 0)) or not (
        isclose(LEFT_MOTOR.get_speed(), 0)
    ):
        if is_black():
            print("Detected black line during sweep.")
            stop()
            return True
        sleep(POLL)

    stop()

    return False


def follow_line(distance: float) -> None:
    """
    Follow the black line until it reaches the specified distance from the wall.

    Parameters
    ----------
    distance : float
        The wanted distance from the wall in centimeters.
    """

    global DELIVERIES
    global AT_OFFICE

    forward()
    current_distance = ULTRASONIC_SENSOR.get_value()
    while current_distance > distance:
        print(f"{current_distance} cm")

        if not is_black() and current_distance > 15.0:
            stop()
            sleep(0.1)

            # Check for black line
            black = black_sweep(20)
            if not black:
                black = black_sweep(45)
                if not black:
                    black_sweep(60)

                    # If at mail room
                    if DELIVERIES == 2 and get_color() == "blue":
                        AT_OFFICE = False
                        move(TILE_SIZE - 5)
                        return

            # Continue forward
            sleep(0.1)
            forward()

        current_distance = ULTRASONIC_SENSOR.get_value()
        sleep(POLL)
    stop()


def turn_to_line_right():
    """
    Turns to the right until the black line is reached.
    """

    right()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-65 * DEGREE_TO_ROTATION)
    LEFT_MOTOR.set_position_relative(65 * DEGREE_TO_ROTATION)
    wait_in_office()
    right()
    while not is_black():
        sleep(POLL)
    stop()


def turn_to_line_left():
    """
    Turns to the left until the black line is reached.
    """

    left()
    RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(65 * DEGREE_TO_ROTATION)
    LEFT_MOTOR.set_position_relative(-65 * DEGREE_TO_ROTATION)
    wait_in_office()
    left()
    while not is_black():
        sleep(POLL)
    stop()


def interrupt() -> bool:
    """
    Checks whether or not the main function is being interrupted by the emergency stop.

    Returns
    -------
    bool
        Whether or not there is an interrupt.
    """

    return STOP.is_pressed()


def check_room() -> None:
    """
    Function to scan the entire office for red and green stickers.
    """

    sleep(0.1)
    found_red = check_red(30)
    if found_red:
        return
    else:
        found_green_tuple = check_green(40)
        found_green = found_green_tuple[0]
        move_back_right = found_green_tuple[1]
        move_back_left = found_green_tuple[2]
        count = found_green_tuple[3]

        if found_green:
            drop_block()
            play_sound(0)
            stop()
            sleep(0.2)

            RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
            LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
            RIGHT_MOTOR.set_position_relative(move_back_right + 90)
            LEFT_MOTOR.set_position_relative(move_back_left - 90)
            wait_in_office()
            stop()
            sleep(0.4)

            move_back_in_office(-2 * count - 2)
            stop()
            sleep(0.2)
        else:
            stop()
            sleep(0.2)

            move_back_in_office(-2 * count - 2)
            stop()
            sleep(0.2)


def main_move() -> None:
    """
    This is the main function of the code that is ran by the process. Add movement here.
    """

    global DELIVERIES

    # First office
    print("Going to first office")
    initiate()
    follow_line(3 * TILE_SIZE)
    sleep(0.2)
    turn(-90)

    sleep(0.1)
    print("Checking first office")
    check_room()
    sleep(0.2)
    turn_to_line_right()
    sleep(0.2)

    # Second office
    print("Going to second office")
    follow_line(TILE_SIZE + 2)
    sleep(0.2)
    turn(-90)

    sleep(0.1)
    print("Checking second office")
    check_room()

    # Mail room
    if DELIVERIES == 2:
        sleep(0.2)
        turn_to_line_left()
        sleep(0.2)
        print("Going to mail room")
        follow_line(2 * TILE_SIZE)
        sleep(0.2)
        print("Turning to mail room")
        turn(90)
        sleep(0.2)
        print("Going to mail room")
        follow_line(2.1 * TILE_SIZE)
        sleep(0.2)
        print("At mail room")
        play_sound(1)
        exit()
    else:
        sleep(0.2)
        turn_to_line_right()

    # Big corner
    print("Going to first corner")
    follow_line(7)
    sleep(0.2)
    print("Turning first corner")
    turn(-75)
    sleep(0.2)

    # Third office
    print("Going to third office")
    follow_line(TILE_SIZE + 2)
    sleep(0.2)
    turn(-90)
    sleep(0.2)

    sleep(0.1)
    print("Checking third office")
    check_room()
    sleep(0.2)
    turn_to_line_right()

    # Big corner
    print("Going to second corner")
    follow_line(7)
    sleep(0.2)
    print("Turning second corner")
    turn(-75)

    # Mail room
    if DELIVERIES == 2:
        print("Going to mail room")
        sleep(0.2)
        follow_line(2 * TILE_SIZE)
        sleep(0.2)
        print("Turning to mail room")
        turn(-90)
        sleep(0.2)
        print("Going to mail room")
        follow_line(2.1 * TILE_SIZE)
        sleep(0.2)
        print("At mail room")
        play_sound(1)
        exit()

    # Fourth office
    print("Going to fourth office")
    sleep(0.2)
    follow_line(TILE_SIZE + 2)
    sleep(0.2)
    turn(-90)

    sleep(0.1)
    print("Checking fourth office")
    check_room()
    sleep(0.2)
    turn_to_line_left()

    # Mail room
    print("Going to mail room")
    sleep(0.2)
    follow_line(2 * TILE_SIZE)
    sleep(0.2)
    print("Turning to mail room")
    turn(90)
    sleep(0.2)
    print("Going to mail room")
    follow_line(2.1 * TILE_SIZE)
    sleep(0.2)
    print("At mail room")
    play_sound(1)


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
