# Imports
import pygame
import game

# Pygame

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE | pygame.HWSURFACE)
pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

pygame.display.set_caption("Ignite")

# Variables
current_scene = ""
valid_scenes = {"game": game}

# Functions
def switch_scene(tag):
    global current_scene
    if not current_scene == "": valid_scenes[current_scene].destroy()

    if tag in valid_scenes.keys():
        current_scene = tag
        match tag:
            case "game": valid_scenes[current_scene].init(["beancore", "hard", 4])
            case _: valid_scenes[current_scene].init()

# Set Screens
for val in valid_scenes.keys():
    valid_scenes[val].screen = screen

# Start
switch_scene("game")

# Update Loop
while True:
    valid_scenes[current_scene].update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        else:
            valid_scenes[current_scene].handle_event(event)
            match current_scene:
                case "game":
                    match event.type:
                        case pygame.KEYDOWN:
                            match event.key:
                                case pygame.K_F7:
                                    switch_scene("game")