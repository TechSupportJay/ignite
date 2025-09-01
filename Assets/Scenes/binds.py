import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random

screen = None
master_data = []

# Variables

screen = None
scene = None
camera = None
binds_camera = None

clock = pygame.time.Clock()

#

fps_cap = 0

profile_options = {}
current_profile = ""
skin_dir = ""
controls = {}

#

menu_sfx = {}

#

current_count = 4
entering_binds = False
current_binds = []

selection_index = 0
current_texts = []

# Master Functions

def init(data = []):
    global scene, camera, binds_camera
    global fps_cap
    global profile_options, skin_dir, controls, current_profile
    global menu_sfx
    global current_count, entering_binds, current_binds
    global selection_index, current_texts

    scene = RMS.scenes.scene(screen, "Template")
    camera = RMS.cameras.camera("Binds", 1)
    binds_camera = RMS.cameras.camera("AddBinds", 2)
    scene.add_camera(camera)
    scene.add_camera(binds_camera)

    #

    profile_options = json.load(open(f"Data/{data[0]}/options.json"))
    current_profile = data[0]
    skin_dir = f"{profile_options["Customisation"]["content_folder"]}/Skins/{profile_options["Customisation"]["skin"]}"
    controls = json.load(open(f"Data/{data[0]}/controls.json"))
    fps_cap = profile_options["Video"]["fps_cap"]

    #

    sfx = ["scroll", "select", "select", "back", "type", "error", "play"]
    for s in sfx:
        menu_sfx[s] = pygame.mixer.Sound(skin_grab(f"SFX/Menu/{s}.ogg"))
        menu_sfx[s].set_volume(profile_options["Audio"]["vol_sfx"] * profile_options["Audio"]["vol_master"])

    #

    current_count = 4
    current_binds = []
    entering_binds = False
    
    selection_index = 0
    current_texts = []

    # Main Camera

    ### Background
    background = RMS.objects.image("background", skin_grab(f"Menus/Options/binds/background.png"))
    background.set_property("size", [1280,720])
    background.set_property("position", [1280/2,720/2])
    camera.add_item(background)

    ### Key Count
    key_count = RMS.objects.text("key_count", "4 KEYS")
    key_count.set_property("font", skin_grab("Fonts/default.ttf"))
    key_count.set_property("font_size", 48)
    key_count.set_property("position", [70,30])
    camera.add_item(key_count)

    ### Directions
    for arrow in ["left", "right"]:
        camera.cache_image(skin_grab(f"Menus/Options/{arrow}.png"))
        arrow_obj = RMS.objects.image(f"arrow_{arrow}", skin_grab(f"Menus/Options/{arrow}.png"))
        arrow_obj.set_property("size", camera.get_image_size(skin_grab(f"Menus/Options/{arrow}.png")))
        arrow_obj.set_property("position:y", 60)

        if arrow == "left": arrow_obj.set_property("position:x", 45)
        else: arrow_obj.set_property("position:x", 70 + camera.get_text_size("key_count")[0] + 30)

        camera.add_item(arrow_obj)
    
    # Add Camera

    ### Overlay
    overlay = RMS.objects.rectangle("overlay", "#000000")
    overlay.set_property("position", [1280/2,720/2])
    overlay.set_property("size", [1280,720])
    overlay.set_property("opacity", 255*0.75)
    binds_camera.add_item(overlay)

    ### Press Text
    press_text = RMS.objects.text("press_text", "Press the key you wish to bind to...")
    press_text.set_property("font", skin_grab("Fonts/sub.ttf"))
    press_text.set_property("font_size", 32)
    press_text.set_property("text_align", "center")
    press_text.set_property("position", [1280/2,50])
    binds_camera.add_item(press_text)

    ### Escape text
    escape_text = RMS.objects.text("escape_text", "or press [ESCAPE] to Cancel")
    escape_text.set_property("font", skin_grab("Fonts/sub.ttf"))
    escape_text.set_property("font_size", 20)
    escape_text.set_property("text_align", "center")
    escape_text.set_property("position", [1280/2,650])
    binds_camera.add_item(escape_text)

    ### Lane Text
    lane_text = RMS.objects.text("lane_text", "Lane 1")
    lane_text.set_property("font", skin_grab("Fonts/default.ttf"))
    lane_text.set_property("font_size", 64)
    lane_text.set_property("text_align", "center")
    lane_text.set_property("position", [1280/2,720/2-32])
    binds_camera.add_item(lane_text)

    ### Hide
    binds_camera.set_property("visible", False)

    # Load Binds

    load_binds(current_count)

def update():
    clock.tick(fps_cap)
    scene.render_scene()

def handle_event(event):
    global current_count, entering_binds, current_binds, selection_index

    match event.type:
        case pygame.KEYDOWN:
            if not entering_binds:
                match event.key:
                    case pygame.K_ESCAPE:
                        save_binds()
                        menu_sfx["back"].play()
                        master_data.append(["switch_scene", "options"])
                    case pygame.K_LEFT:
                        if current_count > 1:
                            current_count -= 1
                            suffix = "KEYS"
                            if current_count == 1: suffix = "KEY"
                            camera.get_item("key_count").set_property("text", f"{current_count} {suffix}")
                        
                            camera.cancel_tween("left")
                            camera.cancel_tween("right")

                            camera.get_item("arrow_right").set_property("position:x", 70 + camera.get_text_size("key_count")[0] + 30)
                            camera.get_item("arrow_left").set_property("position:x", 30)

                            camera.do_tween("left", camera.get_item("arrow_left"), "position:x", 45, 0.5, "expo", "out")
                            
                            menu_sfx["scroll"].stop()
                            menu_sfx["scroll"].play()
                            
                            load_binds(current_count)
                    case pygame.K_RIGHT:
                        current_count += 1
                        camera.get_item("key_count").set_property("text", f"{current_count} KEYS")
                    
                        camera.cancel_tween("left")
                        camera.cancel_tween("right")

                        camera.get_item("arrow_right").set_property("position:x", 70 + camera.get_text_size("key_count")[0] + 30 + 15)
                        camera.get_item("arrow_left").set_property("position:x", 45)

                        camera.do_tween("right", camera.get_item("arrow_right"), "position:x", 70 + camera.get_text_size("key_count")[0] + 30, 0.5, "expo", "out")

                        menu_sfx["scroll"].stop()
                        menu_sfx["scroll"].play()

                        load_binds(current_count)
                    case pygame.K_UP:
                        if selection_index > 0: selection_index -= 1
                        else: selection_index = len(current_texts)-1
                        select_bind(selection_index)
                        menu_sfx["scroll"].stop()
                        menu_sfx["scroll"].play()
                    case pygame.K_DOWN:
                        if selection_index < len(current_texts)-1: selection_index += 1
                        else: selection_index = 0
                        select_bind(selection_index)
                        menu_sfx["scroll"].stop()
                        menu_sfx["scroll"].play()
                    case pygame.K_BACKSPACE:
                        if len(current_texts) > 0:
                            controls[str(current_count)].pop(selection_index)
                            load_binds(current_count)
                            menu_sfx["back"].stop()
                            menu_sfx["back"].play()
                    case pygame.K_RETURN:
                        entering_binds = True
                        current_binds = []

                        if str(current_count) in controls.keys():
                            if len(controls[str(current_count)]) >= 10:
                                menu_sfx["error"].stop()
                                menu_sfx["error"].play()
                                entering_binds = False
                                return

                        menu_sfx["select"].stop()
                        menu_sfx["select"].play()

                        binds_camera.set_property("visible", True)
                        binds_camera.cancel_tween("cam_x")
                        binds_camera.cancel_tween("cam_y")
                        binds_camera.set_property("zoom", [1.1,1.1])

                        binds_camera.do_tween("cam_x", binds_camera, "zoom:x", 1, 0.75, "expo", "out")
                        binds_camera.do_tween("cam_y", binds_camera, "zoom:y", 1, 0.75, "expo", "out")

                        binds_camera.get_item("lane_text").set_property("text", "Lane 1")
            else:
                if event.key == pygame.K_ESCAPE:
                    binds_camera.set_property("visible", False)
                    entering_binds = False

                    menu_sfx["back"].stop()
                    menu_sfx["back"].play()
                elif event.key not in current_binds:
                    current_binds.append(event.key)
                    menu_sfx["type"].stop()
                    menu_sfx["type"].play()
                    
                    binds_camera.get_item("lane_text").set_property("text", f"Lane {len(current_binds)+1}")
                    
                    if len(current_binds) == current_count:
                        binds_camera.set_property("visible", False)
                        entering_binds = False

                        new_binds = []
                        for bind in current_binds:
                            new_binds.append(str(pygame.key.name(bind)))

                        if not str(current_count) in controls.keys(): controls[str(current_count)] = []

                        if new_binds in controls[str(current_count)]:
                            menu_sfx["error"].stop()
                            menu_sfx["error"].play()    
                        else:                 
                            controls[str(current_count)].append(new_binds)
                            load_binds(current_count)

                            menu_sfx["play"].stop()
                            menu_sfx["play"].play()
                else:
                    menu_sfx["error"].stop()
                    menu_sfx["error"].play()
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

def skin_grab(item):
    if os.path.isfile(f"{skin_dir}/{item}"): return (f"{skin_dir}/{item}")
    elif item[-4:] == ".ogg":
        for ext in [".mp3", ".wav"]:
            if os.path.isfile(f"{skin_dir}/{item.replace(".ogg", ext)}"): return f"{skin_dir}/{item.replace(".ogg", ext)}"
        return (f"Assets/Game/Default/{item}")
    else: return (f"Assets/Game/Default/{item}")

#

def load_binds(count):
    global selection_index, current_texts

    i = 0
    selection_index = 0

    if len(current_texts) > 0: camera.remove_item_bulk(current_texts)
    current_texts = []

    if str(count) not in controls: return
    elif len(controls[str(count)]) == 0: return

    for bind_set in controls[str(count)]:
        binds_string = ""
        for bind in bind_set: binds_string += f"{bind.upper()}     "
        binds_string = binds_string[:-5]

        set_text = RMS.objects.text(f"set_text_{i}", binds_string)

        set_text.set_property("font", skin_grab("Fonts/default.ttf"))
        set_text.set_property("font_size", 32)

        set_text.set_property("position:x", 30)
        set_text.set_property("position:y", 120 + (50 * i))

        set_text.set_property("opacity", 255/2)

        camera.add_item(set_text)
        current_texts.append(f"set_text_{i}")
        
        i += 1
    del i

    select_bind(0)

def select_bind(index):
    i = 0
    for text in current_texts:
        if i == index: camera.get_item(text).set_property("opacity", 255)
        else: camera.get_item(text).set_property("opacity", 255/2)
        
        i += 1
    del i

def save_binds():
    file = open(f"Data/{current_profile}/controls.json", "w")
    file.write(json.dumps(controls))
    file.close()