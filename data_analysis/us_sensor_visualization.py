#!/usr/bin/env python3

"""
This file is used to plot continuous data collected from the ultrasonic sensor.
It should be run on your computer, not on the robot.

Before running this script for the first time, you must install the dependencies
as explained in the README.md file.
"""

from matplotlib import pyplot as plt

# Wanted CSV file containing the data
US_SENSOR_DATA_FILE = "us_sensor.csv"

# Lists to hold distances and notes played
distances = []
notes = []

# Read the ultrasonic sensor data from the CSV file
with open(US_SENSOR_DATA_FILE, "r") as f:
    # Get data from each line of the file
    for line in f:
        data = line.strip().split(", ")

        # Append distance and note to respective lists
        distances.append(float(data[0]))
        notes.append(int(data[1]))

# Plot the data using matplotlib
plt.plot(distances, notes, ".", color="red")

# Define plot labels and title
plt.title("Note Played for Specific Distance from Ultrasonic Sensor")
plt.ylabel("Note played (1-4)")
plt.xlabel("Distance (cm)")

# Define plot ticks
plt.xticks(range(0, 51, 10))
plt.yticks(range(0, 5, 1))

# Show the plot
plt.show()
