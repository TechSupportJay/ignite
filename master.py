# Imports
import pygame
import Assets.Scenes.game, Assets.Scenes.splash, Assets.Scenes.song_selection

# Pygame

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE | pygame.HWSURFACE)
pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

pygame.display.set_caption("Ignite")

# Variables
current_scene = ""
valid_scenes = {
    "game": Assets.Scenes.game,
    "splash": Assets.Scenes.splash,
    "song_selection": Assets.Scenes.song_selection
}

current_profile = "Profile1"

# Functions
def switch_scene(tag, data = []):
    global current_scene
    if not current_scene == "": valid_scenes[current_scene].destroy()

    if tag in valid_scenes.keys():
        current_scene = tag
        match tag:
            case "game": valid_scenes[current_scene].init([data[0], data[1], data[2], current_profile])
            case "song_selection": valid_scenes[current_scene].init([current_profile])
            case _: valid_scenes[current_scene].init()

# Set Screens
for val in valid_scenes.keys():
    valid_scenes[val].screen = screen

# Start
switch_scene("song_selection")

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
    
    if not valid_scenes[current_scene].master_data == []:
        data = valid_scenes[current_scene].master_data
        valid_scenes[current_scene].master_data = []
        for pair in data:
            match pair[0]:
                case "switch_scene": switch_scene(pair[1])
                case "load_song":
                    switch_scene("game", [pair[1], pair[2], 4])