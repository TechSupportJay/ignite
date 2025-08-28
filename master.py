# Imports
import pygame, time
import Assets.Scenes.game, Assets.Scenes.results
import Assets.Scenes.main_menu, Assets.Scenes.song_selection, Assets.Scenes.options
import Assets.Scenes.profile, Assets.Scenes.profile_creation
import Assets.Scenes.download

# PyGame

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE | pygame.HWSURFACE)
pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

pygame.display.set_caption("Ignite")
pygame.display.set_icon(pygame.image.load("Assets/icon.png").convert_alpha())

screen_size = [1280,720]
fullscreen = False

# Variables
current_scene = "" 
valid_scenes = {
    "game": Assets.Scenes.game,
    "menu": Assets.Scenes.main_menu,
    "song_selection": Assets.Scenes.song_selection,
    "options": Assets.Scenes.options,
    "results": Assets.Scenes.results,
    "download": Assets.Scenes.download,
    "profile": Assets.Scenes.profile,
    "create_profile": Assets.Scenes.profile_creation
}


current_profile = ""

# Functions
def switch_scene(tag, data = []):
    global current_scene
    if not current_scene == "": valid_scenes[current_scene].destroy()

    if tag in valid_scenes.keys():
        current_scene = tag
        
        if data != []: fancy_print(f"Scene Switch: {tag}\nData: {data}", "Master", "i")
        else: fancy_print(f"Scene Switch: \"{tag}\"", "Master", "i")

        match tag:
            case "game": valid_scenes[current_scene].init([data[0], data[1], current_profile, data[2]])
            case "profile" | "create_profile": valid_scenes[current_scene].init()
            case _: valid_scenes[current_scene].init([current_profile, data])
        valid_scenes[current_scene].resize(screen_size)
        if current_scene not in ["game"]:
            valid_scenes[current_scene].camera.set_property("zoom", [1.1,1.1])
            valid_scenes[current_scene].camera.do_tween("cam_x", valid_scenes[current_scene].camera, "zoom:x", 1, 0.75, "expo", "out")
            valid_scenes[current_scene].camera.do_tween("cam_y", valid_scenes[current_scene].camera, "zoom:y", 1, 0.75, "expo", "out")

#

def fancy_print(content, header = "", icon = ""):
    print()
    to_print = ""
    if header != "": to_print = (f"[{header} - {time.strftime("%H:%M:%S", time.gmtime())}]")
    else: to_print = (f"[{time.strftime("%H:%M:%S", time.gmtime())}]")
    if icon != "": to_print = f"[{icon}] {to_print}"

    print(f"{to_print} ---------")
    print(content)

# Set Screens
for val in valid_scenes.keys():
    valid_scenes[val].screen = screen

# Start
switch_scene("profile")

# Update Loop
while True:
    valid_scenes[current_scene].update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.VIDEORESIZE:
            screen_size = [event.w, event.h]
            valid_scenes[current_scene].resize(screen_size)
        else:
            valid_scenes[current_scene].handle_event(event)
            match current_scene:
                case "game":
                    match event.type:
                        case pygame.KEYDOWN:
                            match event.key:
                                case pygame.K_F7:
                                    switch_scene("game") 
            match event.type:
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_F11:
                            fullscreen = not fullscreen
                            if fullscreen:
                                pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                                screen_size = pygame.display.get_desktop_sizes()[0]
                                valid_scenes[current_scene].resize(screen_size)
                            else:
                                pygame.display.set_mode((1280,720), pygame.RESIZABLE | pygame.HWSURFACE)
                                screen_size = [1280,720]
                                valid_scenes[current_scene].resize(screen_size)
    

    if not valid_scenes[current_scene].master_data == []:
        data = valid_scenes[current_scene].master_data
        valid_scenes[current_scene].master_data = []
        for pair in data:
            match pair[0]:
                case "switch_scene":
                    if len(pair) == 3: switch_scene(pair[1], pair[2])
                    else: switch_scene(pair[1])
                case "load_song": switch_scene("game", [pair[1], pair[2], pair[3]])
                case "set_profile": current_profile = pair[1]