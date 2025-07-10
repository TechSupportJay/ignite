# Imports
import game

# Variables
current_scene = "game"
valid_scenes = {"game": game}

# Functions
def switch_scene(tag):
    global current_scene

    if tag in valid_scenes.keys():
        current_scene = tag
        valid_scenes[current_scene].init(["censored", "exhaust", 4])


# Start
switch_scene("game")

# Update Loop
while True:
    valid_scenes[current_scene].update()