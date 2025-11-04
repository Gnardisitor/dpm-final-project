from time import sleep
from math import sqrt
from utils.brick import EV3ColorSensor, TouchSensor, wait_ready_sensors
import csv

FILENAME = "colors.csv"
COLORS = {}

print("Sensors waiting")
TOUCH_SENSOR = TouchSensor(1)
COLOR_SENSOR = EV3ColorSensor(2)
wait_ready_sensors()
print("Sensors ready")

def get_color():
    # Get normalized RGB vector from color sensor
    color = COLOR_SENSOR.get_rgb()
    dist = sqrt(color[0] * color[0] + color[1] * color[1] + color[2] * color[2])
    color = [color[0] / dist, color[1] / dist, color[2] / dist]
    print(f"Current RGB vector: {color}.")

    # Get name of color from user
    color_name = input("Enter the name of this color: ")
    color_name = color_name.strip().lower()
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
            (sample_count + 1)
        ]
    else:
        COLORS[color_name] = [color[0], color[1], color[2], 1]



def test():
    try:
        while True:
            # Check if touch sensor is pressed
            if TOUCH_SENSOR.is_pressed():
                # Write 
                get_color()

            sleep(0.5)
    except BaseException:
        for name, color in COLORS.items():
            # Average the colors
            COLORS[name] = [
                color[0] / color[3],
                color[1] / color[3],
                color[2] / color[3]
            ]
            # Check name of averaged color
            print(f"Saving {name}.")
        
        # Save to CSV
        with open("colors.csv", mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["name", "r", "g", "b"])
            writer.writeheader()
            writer.writerows(COLORS)


if __name__ == "__main__":
    test()
