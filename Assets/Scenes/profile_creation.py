import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random

screen = None
master_data = []

# Variables

screen = None
scene = None
camera = None

#

stage = 0
stage_objects = []
can_proceed = False

#

menu_sfx = {}

#

profile_name = ""

# Master Functions

def init(data = []):
    global scene, camera
    global stage, stage_objects, can_proceed
    global profile_name
    global menu_sfx

    scene = RMS.scenes.scene(screen, "Template")
    camera = RMS.cameras.camera("HUD", 1)
    scene.add_camera(camera)

    ### SFX

    menu_sfx = {}
    sfx = ["scroll", "select", "back", "type"]
    for s in sfx:
        menu_sfx[s] = pygame.mixer.Sound(f"Assets/Game/Default/SFX/Menu/{s}.ogg")
        menu_sfx[s].set_volume(0.5)

    # Background

    background = RMS.objects.image("background", "Assets/Game/Default/Menus/Profile/background.png")
    background.set_property("size", [1280,720])
    background.set_property("position", [1280/2,720/2])
    camera.add_item(background)

    #

    stage = 0
    stage_objects = []
    load_stage(stage)

    #

    can_proceed = False
    profile_name = ""


def update():
    scene.render_scene()

def handle_event(event):
    global stage, can_proceed, profile_name

    match event.type:
        case pygame.KEYDOWN:
            match stage:
                case 0:
                    match event.key:
                        case pygame.K_BACKSPACE:
                            if len(camera.get_item("text_input").get_property("text")) > 0: camera.get_item("text_input").set_property("text", (camera.get_item("text_input").get_property("text")[:-2]) + "|")
                            else: can_proceed = False
                            menu_sfx["type"].stop()
                            menu_sfx["type"].play()
                        case _:
                            key_dict = {
                                pygame.K_a: "a", pygame.K_b: "b", pygame.K_c: "c", pygame.K_d: "d", pygame.K_e: "e", pygame.K_f: "f", pygame.K_g: "g", pygame.K_h: "h", pygame.K_i: "i", pygame.K_j: "j", pygame.K_k: "k", pygame.K_l: "l", pygame.K_m: "m", pygame.K_n: "n", pygame.K_o: "o", pygame.K_p: "p", pygame.K_q: "q", pygame.K_r: "r", pygame.K_s: "s", pygame.K_t: "t", pygame.K_u: "u", pygame.K_v: "v", pygame.K_w: "w", pygame.K_x: "x", pygame.K_y: "y", pygame.K_z: "z",
                                pygame.K_0: "0", pygame.K_1: "1", pygame.K_2: "2", pygame.K_3: "3", pygame.K_4: "4", pygame.K_5: "5", pygame.K_6: "6", pygame.K_7: "7", pygame.K_8: "8", pygame.K_9: "9",
                                pygame.K_KP0: "0", pygame.K_KP1: "1", pygame.K_KP2: "2", pygame.K_KP3: "3", pygame.K_KP4: "4", pygame.K_KP5: "5", pygame.K_KP6: "6", pygame.K_KP7: "7", pygame.K_KP8: "8", pygame.K_KP9: "9",
                                pygame.K_SPACE: " "
                            }

                            if event.key in key_dict:
                                to_add = key_dict[event.key]
                                if pygame.key.get_pressed()[pygame.K_LSHIFT]: to_add = to_add.upper()
                                if camera.get_item("text_input").get_property("opacity") != 255:
                                    camera.get_item("text_input").set_property("opacity", 255)
                                    camera.get_item("text_input").set_property("text", to_add + "|")
                                else:
                                    camera.get_item("text_input").set_property("text", camera.get_item("text_input").get_property("text")[:-1] + to_add + "|")
                            
                                can_proceed = True

                                menu_sfx["type"].stop()
                                menu_sfx["type"].play()
            match event.key:
                case pygame.K_ESCAPE:
                    menu_sfx["back"].stop()
                    menu_sfx["back"].play()
                    if stage == 0: master_data.append(["switch_scene", "profile"])
                    else:
                        stage -= 1
                        load_stage(stage)
                case pygame.K_RETURN:
                    if can_proceed:
                        match stage:
                            case 0:
                                profile_name = camera.get_item("text_input").get_property("text")[:-1]
                                if os.path.exists(f"data/{profile_name}"):
                                    menu_sfx["back"].stop()
                                    menu_sfx["back"].play()
                                    can_proceed = False

                        if can_proceed:
                            stage += 1
                            load_stage(stage)
                            menu_sfx["select"].stop()
                            menu_sfx["select"].play()

                            if stage == 1: make_profile(profile_name)

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

#

def load_stage(stage):
    global stage_objects, can_proceed

    if len(stage_objects) > 0:
        for item in stage_objects: camera.remove_item(item.get_property("tag"))
    stage_objects = []
    can_proceed = False

    label_1 = RMS.objects.text("label_1", "")
    label_1.set_property("font", "Assets/Game/Default/Fonts/default.ttf")
    label_1.set_property("font_size", 32)
    label_1.set_property("position", [1280/2,50])
    label_1.set_property("text_align", "center")
    camera.add_item(label_1)
    stage_objects.append(label_1)

    match stage:
        case 0:
            label_1.set_property("text", "Type a name for this profile")

            label_2 = RMS.objects.text("label_2", "Press [ENTER] to continue")

            label_2.set_property("font", "Assets/Game/Default/Fonts/sub.ttf")
            label_2.set_property("font_size", 20)
            label_2.set_property("position", [1280/2,720-80])
            label_2.set_property("text_align", "center")

            camera.add_item(label_2)

            stage_objects.append(label_2)

            #

            text_object = RMS.objects.text("text_input", "Start Typing...")
            text_object.set_property("font", "Assets/Game/Default/Fonts/default.ttf")
            text_object.set_property("font_size", 64)
            text_object.set_property("position", [1280/2,720/2-32])
            text_object.set_property("text_align", "center")
            text_object.set_property("opacity", 255/2)
            camera.add_item(text_object)

            stage_objects.append(text_object)

def make_profile(name):
    # Make Files
    os.mkdir(f"Data/{name}")

    # Options
    options_base = json.load(open("Assets/Game/options.json"))
    options_file = {}

    for section in options_base.keys():
        options_file[section] = {}
        for option in options_base[section].keys():
            if option == "content_folder": options_file[section][option] = "Content"
            else: options_file[section][option] = options_base[section][option]["default"]
    
    f = open(f"Data/{name}/options.json", "w")
    f.write(json.dumps(options_file))
    f.close()

    # Controls - Temporary

    f = open(f"Data/{name}/controls.json", "w")
    f.write("{}")
    f.close()

    # Network - Temporary

    network = {
        "ip": "127.0.0.1",
        "port": 5050
    }

    f = open(f"Data/{name}/network.json", "w")
    f.write(json.dumps(network))
    f.close()

    # Make Content Folder
    if not os.path.exists("Content"): os.mkdir("Content")
    if not os.path.exists("Content/Songs"): os.mkdir("Content/Songs")
    if not os.path.exists("Content/Skins"): os.mkdir("Content/Skins")
    if not os.path.exists("Content/Scripts"): os.mkdir("Content/Scripts")
    master_data.append(["switch_scene", "profile"])