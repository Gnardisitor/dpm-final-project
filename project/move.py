from math import isclose, pi
from multiprocessing import Process
from time import sleep

from color import get_color, is_black
from simpleaudio import WaveObject
from utils.brick import EV3UltrasonicSensor, Motor, TouchSensor, wait_ready_sensors

# Initialize motors and sensors
STOP = TouchSensor(3)
RIGHT_MOTOR = Motor("C")
LEFT_MOTOR = Motor("B")
CONVEYOR_MOTOR = Motor("D")
ULTRASONIC_SENSOR = EV3UltrasonicSensor(1)

# Sounds
DROP_SOUND = WaveObject.from_wave_file("sounds/drop.wav")
VICTORY_SOUND = WaveObject.from_wave_file("sounds/victory.wav")

# print("Sensors waiting")
wait_ready_sensors()
# print("Sensors ready")

# Measured values
WHEEL_DIAMETER = 4.2
TURN_DIAMETER = 16.2
TILE_SIZE = 25
DROP_TURN = 40

# Computed values
DISTANCE_TO_DEGREE = 360 / (pi * WHEEL_DIAMETER)
DEGREE_TO_ROTATION = TURN_DIAMETER / WHEEL_DIAMETER

# Values for functions
DELIVERIES = 0
DPS = 540
POWER = DPS / 1250 * 100
POLL = 0.01
SLEEP = 0.3


def play_drop_sound() -> None:
    """
    Plays the drop sound.
    """

    DROP_SOUND.play()


def play_victory_sound() -> None:
    """
    Plays the victory sound.
    """

    VICTORY_SOUND.play()
    sleep(5)


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

    # Wait until the motor start moving
    while isclose(RIGHT_MOTOR.get_speed(), 0):
        sleep(POLL)

    # Wait until the motor stop moving
    while not isclose(RIGHT_MOTOR.get_speed(), 0):
        sleep(POLL)


def wait_drop() -> None:
    """
    Waits until both motors have stopped moving.
    """

    # Wait until the motor start moving
    while isclose(CONVEYOR_MOTOR.get_speed(), 0):
        sleep(POLL)

    while not isclose(CONVEYOR_MOTOR.get_speed(), 0):
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

    RIGHT_MOTOR.set_dps(-0.6 * DPS)
    LEFT_MOTOR.set_dps(-0.6 * DPS)


def left() -> None:
    """
    Turns the robot left indefinitely.
    """

    RIGHT_MOTOR.set_dps(DPS)
    LEFT_MOTOR.set_dps(-DPS - 5)


def right() -> None:
    """
    Turns the robot right indefinitely.
    """

    RIGHT_MOTOR.set_dps(-DPS)
    LEFT_MOTOR.set_dps(DPS + 5)


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

    # Compute encoder degrees
    encoder_degrees = int(distance * DISTANCE_TO_DEGREE)

    try:
        # Set motors to move
        if distance > 0:
            forward()
        else:
            RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
            LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
            backward()

        # Set wanted position
        RIGHT_MOTOR.set_position_relative(encoder_degrees)
        LEFT_MOTOR.set_position_relative(encoder_degrees)
        RIGHT_MOTOR.wait_is_moving()
        RIGHT_MOTOR.wait_is_stopped()
    finally:
        stop()


def back_to_door() -> None:
    """
    Moves the robot backward until it reaches the door.
    """

    try:
        # Set motors to move
        backward()

        # Poll until it reaches the door
        while get_color() != "orange":
            sleep(POLL)
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

    # Compute encoder degrees
    encoder_degrees = int(degrees * DEGREE_TO_ROTATION)

    try:
        # Set motors to move
        if degrees > 0:
            right()
        else:
            left()

        # Set limits (makes turning work properly)
        RIGHT_MOTOR.set_limits(dps=0.75 * DPS, power=POWER)
        LEFT_MOTOR.set_limits(dps=0.75 * DPS, power=POWER)

        # Set wanted position
        RIGHT_MOTOR.set_position_relative(-encoder_degrees)
        LEFT_MOTOR.set_position_relative(encoder_degrees)
        RIGHT_MOTOR.wait_is_moving()
        RIGHT_MOTOR.wait_is_stopped()
    finally:
        stop()


def check_red(encoder_degrees):
    red_found = False
    sleep(SLEEP)

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
    sleep(SLEEP)

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
    sleep(SLEEP)

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

    # if red_found:
    # print("Found red")
    return red_found


def green_sweep(encoder_degrees: int) -> bool:
    sleep(SLEEP)
    move(2)
    sleep(SLEEP)

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
            # print("Detected green sticker during sweep.")
            stop()
            end_degrees_right = RIGHT_MOTOR.get_position()
            end_degrees_left = LEFT_MOTOR.get_position()
            move_back_right = start_degrees_right - end_degrees_right
            move_back_left = start_degrees_left - end_degrees_left
            return [True, move_back_right, move_back_left]
        sleep(POLL)

    stop()
    sleep(SLEEP)

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
            # print("Detected green sticker during sweep.")
            stop()
            end_degrees_right = RIGHT_MOTOR.get_position()
            end_degrees_left = LEFT_MOTOR.get_position()
            move_back_right = start_degrees_right - end_degrees_right
            move_back_left = start_degrees_left - end_degrees_left
            return [True, move_back_right, move_back_left]
        sleep(POLL)

    stop()
    sleep(SLEEP)

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
            # print("Detected green sticker during sweep.")
            stop()
            end_degrees_right = RIGHT_MOTOR.get_position()
            end_degrees_left = LEFT_MOTOR.get_position()
            move_back_right = start_degrees_right - end_degrees_right
            move_back_left = start_degrees_left - end_degrees_left
            return [True, move_back_right, move_back_left]
        sleep(POLL)

    stop()
    sleep(SLEEP)

    return [False, 0, 0]


def check_green(sweep_degrees):
    encoder_degrees = int(sweep_degrees * DEGREE_TO_ROTATION)
    count = 0
    found_green = False

    while True:
        count += 1
        found_green_tuple = green_sweep(encoder_degrees)
        found_green = found_green_tuple[0]

        # Check if count is done
        if count > 8:
            break

        # Check for value found
        if found_green:
            break

    # print(f"{count}")
    return [found_green, found_green_tuple[1], found_green_tuple[2], count]


def drop_block():
    """
    Drops a single block from the conveyor belt.
    """

    global DELIVERIES

    # Move slightly to the right
    sleep(0.7)
    right()
    RIGHT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-DROP_TURN)
    LEFT_MOTOR.set_position_relative(DROP_TURN)
    wait()
    stop()
    sleep(SLEEP)

    # Run conveyor belt to drop block
    CONVEYOR_MOTOR.set_dps(DPS)
    CONVEYOR_MOTOR.set_limits(dps=DPS, power=POWER)
    CONVEYOR_MOTOR.set_position_relative(135)
    wait_drop()
    CONVEYOR_MOTOR.set_dps(0)
    sleep(SLEEP)

    CONVEYOR_MOTOR.set_dps(-DPS)
    CONVEYOR_MOTOR.set_limits(dps=DPS, power=POWER)
    CONVEYOR_MOTOR.set_position_relative(-90)
    wait_drop()
    CONVEYOR_MOTOR.set_dps(0)
    sleep(SLEEP)

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
            # print("Detected black line during sweep.")
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
            # print("Detected black line during sweep.")
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
            # print("Detected black line during sweep.")
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

    forward()
    current_distance = 200.0
    while current_distance > distance:
        # print(f"{current_distance} cm")

        if not is_black() and current_distance > 15.0:
            stop()
            sleep(0.5 * SLEEP)

            # Check for black line
            black = black_sweep(20)
            if not black:
                black = black_sweep(45)
                if not black:
                    black = black_sweep(60)
                    if not black:
                        black = black_sweep(90)

            # Continue forward
            sleep(SLEEP)
            forward()

        current_distance = ULTRASONIC_SENSOR.get_value()
        sleep(POLL)
    stop()


def turn_to_line_right():
    """
    Turns to the right until the black line is reached.
    """

    right()
    RIGHT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(-65 * DEGREE_TO_ROTATION)
    LEFT_MOTOR.set_position_relative(65 * DEGREE_TO_ROTATION)
    wait()

    RIGHT_MOTOR.set_dps(-0.5 * DPS)
    LEFT_MOTOR.set_dps(0.5 * DPS)
    RIGHT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
    while not is_black():
        sleep(POLL)
    stop()


def turn_to_line_left():
    """
    Turns to the left until the black line is reached.
    """

    left()
    RIGHT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
    RIGHT_MOTOR.set_position_relative(65 * DEGREE_TO_ROTATION)
    LEFT_MOTOR.set_position_relative(-65 * DEGREE_TO_ROTATION)
    wait()

    RIGHT_MOTOR.set_dps(0.5 * DPS)
    LEFT_MOTOR.set_dps(-0.5 * DPS)
    RIGHT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
    LEFT_MOTOR.set_limits(dps=0.5 * DPS, power=POWER)
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

    sleep(SLEEP)
    found_red = check_red(50)
    if found_red:
        return
    else:
        found_green_tuple = check_green(40)
        found_green = found_green_tuple[0]
        move_back_right = found_green_tuple[1]
        move_back_left = found_green_tuple[2]

        if found_green:
            drop_block()
            play_drop_sound()
            stop()
            sleep(SLEEP)

            RIGHT_MOTOR.set_limits(dps=DPS, power=POWER)
            LEFT_MOTOR.set_limits(dps=DPS, power=POWER)
            RIGHT_MOTOR.set_position_relative(move_back_right + DROP_TURN)
            LEFT_MOTOR.set_position_relative(move_back_left - DROP_TURN)
            wait()
            stop()
            sleep(SLEEP)

            back_to_door()
            sleep(SLEEP / 2)
            move(1.5)
            stop()
            sleep(SLEEP)
        else:
            stop()
            sleep(SLEEP)

            back_to_door()
            sleep(SLEEP / 2)
            move(1.5)
            stop()
            sleep(SLEEP)


def main_move() -> None:
    """
    This is the main function of the code that is ran by the process. Add movement here.
    """

    global DELIVERIES

    sleep(SLEEP)

    # First office
    # print("Going to first office")
    initiate()
    sleep(0.1)
    follow_line(3 * TILE_SIZE + 0.5)
    sleep(0.6)
    turn(-90)

    sleep(SLEEP)
    # print("Checking first office")
    check_room()
    sleep(0.6)
    turn_to_line_right()
    sleep(0.1)

    # Second office
    # print("Going to second office")
    follow_line(TILE_SIZE + 2)
    sleep(0.6)
    turn(-90)

    sleep(SLEEP)
    # print("Checking second office")
    check_room()

    # Mail room
    if DELIVERIES == 2:
        sleep(0.6)
        turn_to_line_left()
        sleep(0.1)
        # print("Going to mail room")
        follow_line(2 * TILE_SIZE)
        sleep(0.6)
        # print("Turning to mail room")
        turn(90)
        sleep(0.1)
        # print("Going to mail room")
        follow_line(3.1 * TILE_SIZE)
        move(20)
        sleep(SLEEP)
        # print("At mail room")
        play_victory_sound()
        exit()
    else:
        sleep(0.6)
        turn_to_line_right()

    # Big corner
    # print("Going to first corner")
    follow_line(6)
    sleep(0.6)
    # print("Turning first corner")
    turn(-77.5)
    sleep(0.1)

    # Third office
    # print("Going to third office")
    follow_line(TILE_SIZE + 2)
    sleep(0.6)
    turn(-90)
    sleep(SLEEP)

    sleep(SLEEP)
    # print("Checking third office")
    check_room()
    sleep(0.6)
    turn_to_line_right()

    # Big corner
    # print("Going to second corner")
    follow_line(6)
    sleep(0.6)
    # print("Turning second corner")
    turn(-77.5)

    # Mail room
    if DELIVERIES == 2:
        # print("Going to mail room")
        sleep(0.1)
        follow_line(2 * TILE_SIZE)
        sleep(0.6)
        # print("Turning to mail room")
        turn(-90)
        sleep(0.1)
        # print("Going to mail room")
        follow_line(3.1 * TILE_SIZE)
        move(20)
        sleep(SLEEP)
        # print("At mail room")
        play_victory_sound()
        exit()

    # Fourth office
    # print("Going to fourth office")
    sleep(0.1)
    follow_line(TILE_SIZE + 2)
    sleep(0.6)
    turn(-90)

    sleep(SLEEP)
    # print("Checking fourth office")
    check_room()
    sleep(0.6)
    turn_to_line_left()

    # Mail room
    # print("Going to mail room")
    sleep(0.1)
    follow_line(2 * TILE_SIZE)
    sleep(0.6)
    # print("Turning to mail room")
    turn(90)
    sleep(0.1)
    # print("Going to mail room")
    follow_line(3.1 * TILE_SIZE)
    move(20)
    sleep(SLEEP)
    # print("At mail room")
    play_victory_sound()


if __name__ == "__main__":
    # Create process for movement
    move_process = Process(target=main_move)
    move_process.start()
    # print("Movement process started")

    # Wait for movement to finish
    while move_process.is_alive() and not interrupt():
        sleep(POLL)

    stop()
    # print("Movement process stopping")
    move_process.terminate()
    move_process.join()
    # print("Movement process ended")
