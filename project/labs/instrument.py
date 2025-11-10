#!/usr/bin/env python3

from time import sleep

from utils import sound
from utils.brick import (
    EV3UltrasonicSensor,
    Motor,
    TouchSensor,
    wait_ready_sensors,
)

# Array of notes to be played based on distance readings
NOTES = [
    sound.Sound(duration=0.2, pitch="C5", volume=85),
    sound.Sound(duration=0.2, pitch="D5", volume=85),
    sound.Sound(duration=0.2, pitch="E5", volume=85),
    sound.Sound(duration=0.2, pitch="G5", volume=85),
]

print("Program start.\nWaiting for sensors to turn on...")

# Initialize motors and sensors
DRUM = Motor("A")
START_DRUM = TouchSensor(2)
EMERGENCY_STOP = TouchSensor(1)
US_SENSOR = EV3UltrasonicSensor(3)

wait_ready_sensors()
print("Done waiting.")


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


def main_loop():
    """
    Main while loop for the instrument, which checks for button presses and
    plays notes based on distance readings from the ultrasonic sensor.
    """

    try:
        # Main while loop
        while True:
            # Break from loop if emergency stop is pressed
            if EMERGENCY_STOP.is_pressed():
                break

            # Start the drum at 720 dps (120 bpm) if the start drum button is pressed
            if START_DRUM.is_pressed():
                DRUM.set_dps(720)

            # Get distance from ultrasonic sensor
            distance = US_SENSOR.get_value()

            # Play different notes based on distance ranges
            if distance is not None:
                print(distance)
                if distance < 10:
                    play_sound(0)
                elif distance < 20:
                    play_sound(1)
                elif distance < 30:
                    play_sound(2)
                elif distance < 40:
                    play_sound(3)
                else:
                    # No note played for distances 40 cm and above
                    sleep(0.2)

            # Short delay to avoid rapid triggering
            sleep(0.3)
    except BaseException:
        # Avoid errors crashing the program to stop the motor properly
        pass
    finally:
        # Stop the drum motor and exit code
        DRUM.set_dps(0)
        print("Emergency stop")


if __name__ == "__main__":
    main_loop()
