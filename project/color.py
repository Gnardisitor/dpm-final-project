from time import sleep
from math import sqrt
from utils.brick import EV3ColorSensor, TouchSensor, wait_ready_sensors

COLORS = {
    "red": [1, 0, 0],
    "green": [0, 1, 0],
    "blue": [0, 0, 1],
    "white": [1, 1, 1],
    "black": [0, 0, 0],
}

print("Sensors waiting")
TOUCH = TouchSensor(1)
COLOR = EV3ColorSensor(2)
wait_ready_sensors()
print("Sensors ready")

def color():
    color = COLOR.get_rgb()
    dist = sqrt(color[0] * color[0] + color[1] * color[1] + color[2] * color[2])
    color = [color[0] / dist, color[1] / dist, color[2] / dist]
    print(f"Current color: {color}")

    closest_name = ""
    closest_dist = 10
    for name, ref_color in COLORS.items():
        dist_list = [color[0] - ref_color[0], color[1] - ref_color[1], color[2] - ref_color[2]]
        dist = sqrt(dist_list[0] * dist_list[0] + dist_list[1] * dist_list[1] + dist_list[2] * dist_list[2])
        if dist < closest_dist:
            closest_dist = dist
            closest_name = name
    print(f"Closest color: {closest_name}")


def test():
    try:
        while True:
            if TOUCH.is_pressed():
                color()

            sleep(0.5)
    except BaseException:
        pass


if __name__ == "__main__":
    test()
