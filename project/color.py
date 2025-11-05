from math import sqrt
from time import sleep
import csv

from utils.brick import EV3ColorSensor, TouchSensor, wait_ready_sensors

COLORS = {}

with open("colors.csv", "r") as file:
    reader = csv.reader(file)
    for row in reader:
        name = row[0]
        r = float(row[1])
        g = float(row[2])
        b = float(row[3])
        COLORS[name] = [r, g, b]

print("Sensors waiting")
TOUCH = TouchSensor(1)
COLOR = EV3ColorSensor(2)
wait_ready_sensors()
print("Sensors ready")


def get_color():
    # Read color and normalize
    color = COLOR.get_rgb()
    dist = sqrt(color[0] * color[0] + color[1] * color[1] + color[2] * color[2])
    color = [color[0] / dist, color[1] / dist, color[2] / dist]

    # Find closest color
    closest_name = ""
    closest_dist = 1
    for name, ref_color in COLORS.items():
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

    # Return closest color
    return closest_name


def test():
    try:
        while True:
            if TOUCH.is_pressed():
                color_name = get_color()
                print(color_name)

            sleep(0.5)
    except BaseException:
        pass


if __name__ == "__main__":
    test()
