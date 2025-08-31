import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, shutil, math, time, json, random

screen = None
master_data = []

# Variables

screen = None
scene = None
camera = None

#

options = []
buttons = []
selection_index = 0

#

menu_sfx = {}

# Master Functions

def init(data = []):
    global scene, camera
    global options, buttons
    global menu_sfx
    global selection_index

    scene = RMS.scenes.scene(screen, "Template")
    camera = RMS.cameras.camera("HUD", 1)
    scene.add_camera(camera)

    #

    if not os.path.exists("Data"): os.mkdir("Data")

    options = next(os.walk("Data"), (None, None, []))[1]
    if options is None: options = []
    buttons = []

    load_buttons(options)
    selection_index = 0

    ### SFX

    menu_sfx = {}
    sfx = ["scroll", "select", "back"]
    for s in sfx:
        menu_sfx[s] = pygame.mixer.Sound(f"Assets/Game/Default/SFX/Menu/{s}.ogg")
        menu_sfx[s].set_volume(0.5)

def update():
    scene.render_scene()

def handle_event(event):
    global selection_index

    match event.type:
        case pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP:
                    if selection_index == 0: selection_index = len(buttons)-1
                    else: selection_index -= 1
                    select_item(selection_index)
                    menu_sfx["scroll"].stop()
                    menu_sfx["scroll"].play()
                case pygame.K_DOWN:
                    if selection_index == len(buttons)-1: selection_index = 0
                    else: selection_index += 1
                    select_item(selection_index)
                    menu_sfx["scroll"].stop()
                    menu_sfx["scroll"].play()
                case pygame.K_RETURN:
                    if selection_index != len(buttons)-1:
                        camera.set_property("visible", False)
                        fancy_print(f"Loading Profile: {options[selection_index]}", "Profile Selection", "i")
                        master_data.append(["set_profile", options[selection_index]])
                        master_data.append(["switch_scene", "menu", [True]])
                    else:
                        master_data.append(["switch_scene", "create_profile"])
                    menu_sfx["select"].stop()
                    menu_sfx["select"].play()
                case pygame.K_DELETE:
                    if selection_index != len(buttons)-1:
                        fancy_print(f"Deleting Profile: {options[selection_index]}", "Profile Selection", "i")
                        shutil.rmtree(f"Data/{options[selection_index]}")

                        menu_sfx["back"].stop()
                        menu_sfx["back"].play()

                        destroy()
                        init()
        case pygame.VIDEORESIZE:
            camera.set_property("scale", [event.w/1280, event.h/720])
            camera.set_property("position", [(event.w-1280)/2,(event.h-720)/2])

def destroy():
    global camera, scene
    del camera, scene

def resize(size):
    for cam in scene.cameras.keys():
        scene.cameras[cam].set_property("scale", [size[0]/1280,size[1]/720])
        scene.cameras[cam].set_property("position", [(size[0]-1280)/2,(size[1]-720)/2])


def fancy_print(content, header = "", icon = ""):
    print()
    to_print = ""
    if header != "": to_print = (f"[{header} - {time.strftime("%H:%M:%S", time.gmtime())}]")
    else: to_print = (f"[{time.strftime("%H:%M:%S", time.gmtime())}]")
    if icon != "": to_print = f"[{icon}] {to_print}"

    print(f"{to_print} ---------")
    print(content)

#

def load_buttons(items):
    global buttons

    fancy_print(f"Found the following profiles:\n{items}", "Profile Selection", "i")

    items.append(0)
    i = 0
    for item in items:
        if item == 0:
            button = RMS.objects.text("new_profile", "Create New Profile")
            button.set_property("font", "Assets/Game/Default/Fonts/sub.ttf")
        else:
            button = RMS.objects.text(f"btn_{i}", item)
            button.set_property("font", "Assets/Game/Default/Fonts/default.ttf")
        button.set_property("font_size", 32)
        button.set_property("text_align", "center")
        button.set_property("position:x", 1280/2)
        button.set_property("position:y", 720/2-(40*len(items)/2)+(40*i))
        button.set_property("opacity", 255/2)
        buttons.append(button)
        camera.add_item(button)
        i += 1
    del i

    select_item(0)

def select_item(index):
    i = 0
    for button in buttons:
        if i == index: button.set_property("opacity", 255)
        else: button.set_property("opacity", 255/2)
        i += 1