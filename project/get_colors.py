from math import sqrt
from time import sleep

from utils.brick import EV3ColorSensor, TouchSensor, wait_ready_sensors

COLORS_FILENAME = "colors.csv"
COLORS = {}

AMBIENTS_FILENAME = "ambients.csv"
AMBIENTS = {}

TOUCH_SENSOR = TouchSensor(3)
COLOR_SENSOR = EV3ColorSensor(4)

CURRENT_NAME = "unknown"
CURRENT_MODE = "color"
POLL = 0.01

print("Sensors waiting")
wait_ready_sensors()
print("Sensors ready")


def get_color(color_name: str) -> None:
    """
    Adds to the dictionary the currently detected color, can sum multiple samples per color.

    Parameters
    ----------
    color_name : str
        The name of the color to save.
    """

    # Get normalized RGB vector from color sensor
    color = COLOR_SENSOR.get_rgb()

    # Check for existence of color
    if color[0] is None or color[1] is None or color[2] is None:
        print("No color detected.")
        return

    dist = sqrt(color[0] * color[0] + color[1] * color[1] + color[2] * color[2])

    # Check for zero distance
    if dist == 0:
        print("No color detected.")
        return

    color = [color[0] / dist, color[1] / dist, color[2] / dist]
    print(f"Current RGB vector: {color}.")
    print(f"Saving {color_name} with RGB vector: {color}.")

    # Check if color exists, if so average it
    if color_name in COLORS:
        print(f"Color '{color_name}' already exists. Doing average.")
        existing_color = COLORS[color_name]
        sample_count = existing_color[3]
        COLORS[color_name] = [
            (existing_color[0] + color[0]),
            (existing_color[1] + color[1]),
            (existing_color[2] + color[2]),
            (sample_count + 1),
        ]
    else:
        COLORS[color_name] = [color[0], color[1], color[2], 1]


def get_ambient(ambient_name: str) -> None:
    """
    Adds to the dictionary the currently detected ambient value, can sum multiple samples per ambient.

    Parameters
    ----------
    ambient_name : str
        The name of the ambient to save.
    """

    # Get ambient value from color sensor
    ambient = COLOR_SENSOR.get_ambient()
    print(f"Current ambient value: {ambient}.")
    print(f"Saving {ambient_name} with ambient value: {ambient}.")

    # Check if ambient exists, if so average it
    if ambient_name in AMBIENTS:
        print(f"Ambient '{ambient_name}' already exists. Doing average.")
        existing_ambient = AMBIENTS[ambient_name]
        sample_count = existing_ambient[1]
        AMBIENTS[ambient_name] = [
            (existing_ambient[0] + ambient),
            (sample_count + 1),
        ]
    else:
        AMBIENTS[ambient_name] = [ambient, 1]


def test() -> None:
    """
    Simple loop to gather multiple samples and then save the results into a CSV file.
    """

    global CURRENT_NAME
    global CURRENT_MODE

    try:
        while True:
            # Check if touch sensor is pressed
            if TOUCH_SENSOR.is_pressed():
                if CURRENT_MODE == "color":
                    get_color(CURRENT_NAME)
                else:
                    get_ambient(CURRENT_NAME)

            sleep(POLL)
    except KeyboardInterrupt:
        try:
            command = input("Command: ")
            command = command.strip().lower()
        except KeyboardInterrupt:
            print("Command error. Restarting test loop.")
            test()

        if command == "exit":
            save()
            return
        elif command == "color":
            CURRENT_MODE = "color"
            print("Switched to color mode.")
        elif command == "ambient":
            CURRENT_MODE = "ambient"
            print("Switched to ambient mode.")
        elif command != "":
            CURRENT_NAME = command

        test()


def save() -> None:
    """
    Save the gathered colors and ambients into CSV files.
    """

    # Average RGB values
    avg_colors = {}
    for name, color in COLORS.items():
        avg_r = color[0] / color[3]
        avg_g = color[1] / color[3]
        avg_b = color[2] / color[3]

        # Save averages
        avg_colors[name] = [avg_r, avg_g, avg_b]

    # Save to CSV
    with open(COLORS_FILENAME, mode="w", newline="") as file:
        for name, color in avg_colors.items():
            file.write(f"{name},{color[0]},{color[1]},{color[2]}\n")
        file.close()

    # Average ambient values
    avg_ambients = {}
    for name, ambient in AMBIENTS.items():
        avg_amb = ambient[0] / ambient[1]

        # Save averages
        avg_ambients[name] = avg_amb

    # Save to CSV
    with open(AMBIENTS_FILENAME, mode="w", newline="") as file:
        for name, ambient in avg_ambients.items():
            file.write(f"{name},{ambient}\n")
        file.close()


if __name__ == "__main__":
    test()
