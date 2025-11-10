#!/usr/bin/env python3

from time import sleep

from utils import sound
from utils.brick import (
    EV3UltrasonicSensor,
    wait_ready_sensors,
)

# File to write ultrasonic sensor data for analysis
US_SENSOR_DATA_FILE = "../data_analysis/us_sensor.csv"

# Array of notes to be played based on distance readings
NOTES = [
    sound.Sound(duration=0.2, pitch="C5", volume=75),
    sound.Sound(duration=0.2, pitch="D5", volume=75),
    sound.Sound(duration=0.2, pitch="E5", volume=75),
    sound.Sound(duration=0.2, pitch="G5", volume=75),
]

print("Program start.\nWaiting for sensors to turn on...")

# Initialize ultrasonic sensor
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


def test():
    """
    Main while loop to test the ultrasonic sensor and speaker
    functionality and writing the data to a CSV file.
    """

    try:
        # Open file to write ultrasonic sensor data
        output_file = open(US_SENSOR_DATA_FILE, "w")

        while True:
            # Get distance from ultrasonic sensor
            note = 0  # Default note (no sound)
            distance = US_SENSOR.get_value()

            # Play different notes based on distance ranges
            if distance is not None:
                if distance < 10:
                    note = 1
                    print(f"Playing note {note} at {distance} cm.")
                    play_sound(0)
                elif distance < 20:
                    note = 2
                    print(f"Playing note {note} at {distance} cm.")
                    play_sound(1)
                elif distance < 30:
                    note = 3
                    print(f"Playing note {note} at {distance} cm.")
                    play_sound(2)
                elif distance < 40:
                    note = 4
                    print(f"Playing note {note} at {distance} cm.")
                    play_sound(3)
                else:
                    sleep(0.2)

            # Write distance and note played to the output file
            output_file.write(f"{distance}, {note}\n")
            sleep(0.3)
    except BaseException:
        # Avoid errors crashing the program to close the file properly
        pass
    finally:
        # Close the output file
        output_file.close()
        print("Stop")


if __name__ == "__main__":
    test()
