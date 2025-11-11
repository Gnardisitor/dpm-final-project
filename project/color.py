#!/usr/bin/env python3

import csv
from math import sqrt
from time import sleep

from utils.brick import EV3ColorSensor, wait_ready_sensors

COLORS = {"unknown": [0.0, 0.0, 0.0]}

# Load colors from CSV file into the dictionary
with open("colors.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        name = row[0]
        r = float(row[1])
        g = float(row[2])
        b = float(row[3])
        COLORS[name] = [r, g, b]

COLOR = EV3ColorSensor(4)

print("Sensors waiting")
wait_ready_sensors()
print("Sensors ready")


def get_color() -> str:
    """
    Get the closest color to the current reading

    Returns
    -------
    str
        Name of the closest color, returns "unknown" if no valid color is detected.
    """

    # Read color and normalize
    color = COLOR.get_rgb()

    # Check for existence of color
    if color[0] is None or color[1] is None or color[2] is None:
        return "unknown"

    dist = sqrt(color[0] * color[0] + color[1] * color[1] + color[2] * color[2])

    # Check for zero distance
    if dist == 0:
        return "unknown"

    color = [color[0] / dist, color[1] / dist, color[2] / dist]

    # Find closest color
    closest_name = ""
    closest_dist = 1
    for name, ref_color in COLORS.items():
        # Get euclidean distance
        dist_list = [
            color[0] - ref_color[0],
            color[1] - ref_color[1],
            color[2] - ref_color[2],
        ]
        dist = sqrt(
            dist_list[0] * dist_list[0]
            + dist_list[1] * dist_list[1]
            + dist_list[2] * dist_list[2]
        )
        if dist < closest_dist:
            closest_dist = dist
            closest_name = name

    return closest_name


# Simple test loop
def test() -> None:
    """
    Simple test loop to print color readings.
    """

    try:
        while True:
            color_name = get_color()
            print(color_name)
            sleep(0.5)
    except BaseException:
        pass


if __name__ == "__main__":
    test()
