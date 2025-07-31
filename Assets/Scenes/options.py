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

current_options = {}
current_profile = ""
options_ref = {}
skin_dir = ""

#

section_index = 0
option_index = 0
valid_options = []
cur_ref = {}

#

menu_sfx = {}

#

direction_held = ["left", False, 0.0]
last_tick = 0

# Master Functions

def init(data):
    global scene, camera
    global current_options, skin_dir, options_ref, current_profile
    global section_index, option_index, menu_sfx
    global direction_held, last_tick

    scene = RMS.scenes.scene(screen, "Options")
    camera = RMS.cameras.camera("Options", 1)
    scene.add_camera(camera)

    #

    current_profile = data[0]
    current_options = json.load(open(f"Data/{data[0]}/options.json"))
    skin_dir = f"{current_options["Customisation"]["content_folder"]}/Skins/{current_options["Customisation"]["skin"]}"

    ### Background
    background = RMS.objects.image("background", skin_grab(f"Menus/Options/background.png"))
    background.set_property("size", [1280,720])
    background.set_property("position", [1280/2,720/2])
    camera.add_item(background)

    ### Load Overlay
    overlay = RMS.objects.image("overlay", skin_grab(f"Menus/Options/overlay.png"))
    overlay.set_property("size", [1280,720])
    overlay.set_property("position", [1280/2,720/2])
    overlay.set_property("priority", 3)
    camera.add_item(overlay)

    ### Cache Images
    camera.cache_image_bulk([
        skin_grab("Menus/Options/toggle_on.png"),
        skin_grab("Menus/Options/toggle_off.png"),
        skin_grab("Menus/Options/left.png"),
        skin_grab("Menus/Options/right.png")
    ])

    #
    
    options_ref = json.load(open(f"Assets/Game/options.json"))
    load_options()

    #

    section_index = 0
    option_index = 0

    #

    sfx = ["scroll", "select", "select", "back"]
    for s in sfx:
        menu_sfx[s] = pygame.mixer.Sound(skin_grab(f"SFX/Menu/{s}.ogg"))
        menu_sfx[s].set_volume(options_ref["Audio"]["vol_sfx"]["value"] * options_ref["Audio"]["vol_master"]["value"])
    
    #

    direction_held = ["left", False, 0.0]
    last_tick = 0

def update():
    global last_tick, option_index

    scene.render_scene()

    if direction_held[1]:
        times_run = 1
        if pygame.key.get_pressed()[pygame.K_LSHIFT]: times_run = 10
        if time.time() > direction_held[2] and time.time() > last_tick:
            match direction_held[0]:
                case "left":
                    for i in range(times_run): option_input(option_index, "left")
                    play_sfx("scroll")
                    last_tick = time.time() + 0.025
                case "right":
                    for i in range(times_run): option_input(option_index, "right")
                    play_sfx("scroll")
                    last_tick = time.time() + 0.025
                case "up":
                    if option_index > 0: option_index -= 1
                    else: option_index = len(valid_options)-1
                    select_option(option_index)
                    play_sfx("scroll")
                    last_tick = time.time() + 0.075
                case "down":
                    if option_index < len(valid_options)-1: option_index += 1
                    else: option_index = 0
                    select_option(option_index)
                    play_sfx("scroll")
                    last_tick = time.time() + 0.075
            

def handle_event(event):
    global section_index, option_index, direction_held

    match event.type:
        case pygame.KEYDOWN:
            match event.key:
                case pygame.K_q:
                    if section_index != 0: section_index -= 1
                    else: section_index = len(list(options_ref.keys()))-1
                    load_section(section_index)
                    option_index = 0
                    play_sfx("scroll")
                case pygame.K_e:
                    if section_index != len(list(options_ref.keys()))-1: section_index += 1
                    else: section_index = 0
                    load_section(section_index)
                    option_index = 0
                    play_sfx("scroll")
                case pygame.K_UP:
                    if option_index > 0: option_index -= 1
                    else: option_index = len(valid_options)-1
                    select_option(option_index)
                    play_sfx("scroll")
                    direction_held = ["up", True, time.time()+0.5]
                case pygame.K_DOWN:
                    if option_index < len(valid_options)-1: option_index += 1
                    else: option_index = 0
                    select_option(option_index)
                    play_sfx("scroll")
                    direction_held = ["down", True, time.time()+0.5]
                case pygame.K_RETURN:
                    option_input(option_index, "toggle")
                case pygame.K_LEFT:
                    times_run = 1
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]: times_run = 10
                    for i in range(times_run): option_input(option_index, "left")
                    play_sfx("scroll")
                    direction_held = ["left", True, time.time()+0.5]
                case pygame.K_RIGHT:
                    times_run = 1
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]: times_run = 10
                    for i in range(times_run): option_input(option_index, "right")
                    play_sfx("scroll")
                    direction_held = ["right", True, time.time()+0.5]
                case pygame.K_ESCAPE:
                    save_options()
                    master_data.append(["switch_scene", "song_selection"])
                case pygame.K_BACKSPACE:
                    option_input(option_index, "reset")
                    play_sfx("back")
                case _: pass
        case pygame.KEYUP:
            match event.key:
                case pygame.K_LEFT: direction_held = ["left", False, 0]
                case pygame.K_RIGHT: direction_held = ["right", False, 0]
                case pygame.K_UP: direction_held = ["up", False, 0]
                case pygame.K_DOWN: direction_held = ["down", False, 0]
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
    else: return (f"Assets/Game/Default/{item}")

#

def load_options():
    i = 0
    for section in options_ref:
        make_section_header(section, i)
        i += 1
    
    for section in options_ref.keys():
        for option in options_ref[section].keys():
            options_ref[section][option]["value"] = current_options[section][option]

    load_section(0)

def make_section_header(section_name, index):
    header_text = RMS.objects.text(f"header_{index}", section_name)
    header_text.set_property("font", skin_grab("Fonts/default.ttf"))
    header_text.set_property("font_size", 32)
    header_text.set_property("position:y", 30)
    header_text.set_property("opacity", 255/2)
    header_text.set_property("priority", 5)
    if index == 0: header_text.set_property("opacity", 255)

    camera.add_item(header_text)

    if index != 0: header_text.set_property("position:x", camera.get_item(f"header_{index-1}").get_property("position:x") + camera.get_text_size(f"header_{index-1}")[0] + 20)
    else: header_text.set_property("position:x", 30)

def load_section(section_index):
    global cur_ref, valid_options

    valid_options = []
    
    section_name = list(options_ref.keys())[section_index]

    #

    i = 0
    for item in cur_ref:
        if "display" in cur_ref[item].keys():
            camera.remove_item(f"option_{i}")
            type = cur_ref[item]["type"]
            match type:
                case "bool": camera.remove_item(f"toggle_{i}")
                case "float" | "int" | "fps":
                    camera.remove_item(f"left_{i}")
                    camera.remove_item(f"right_{i}")
                    camera.remove_item(f"text_{i}")
            i += 1
    del i

    #

    cur_ref = options_ref[section_name]

    index = 0
    for option in options_ref[section_name]:
        if "display" in options_ref[section_name][option].keys():
            make_option(section_name, option, index)
            valid_options.append([option, options_ref[section_name][option]])
            index += 1
        else:
            make_label(option, index)

    for i in range(len(list(options_ref))):
        if i == section_index: camera.get_item(f"header_{i}").set_property("opacity", 255)
        else: camera.get_item(f"header_{i}").set_property("opacity", 255/2)

def make_option(section, option, index):
    to_tween = []

    ref = options_ref[section][option]

    option_text = RMS.objects.text(f"option_{index}", ref["display"])

    option_text.set_property("font", skin_grab("Fonts/default.ttf"))
    option_text.set_property("font_size", 48)
    option_text.set_property("position:x", 30)
    option_text.set_property("position:y", 100 + (75 * index))

    opacity = 255/2
    if index == 0: opacity = 255

    option_text.set_property("opacity", opacity)

    camera.add_item(option_text)
    to_tween.append(option_text)

    right_side = camera.get_text_size(f"option_{index}")[0]

    match ref["type"]:
        case "bool":
            toggled = skin_grab("Menus/Options/toggle_on.png")
            if "value" in cur_ref[list(cur_ref.keys())[index]].keys():
                if not cur_ref[list(cur_ref.keys())[index]]["value"]: toggled = skin_grab("Menus/Options/toggle_off.png")
            elif not ref["default"]: toggled = skin_grab("Menus/Options/toggle_off.png")
            toggle_icon = RMS.objects.image(f"toggle_{index}", toggled)
            toggle_icon.set_property("position:x", 30 + right_side + 50)
            toggle_icon.set_property("position:y", option_text.get_property("position:y") + (camera.get_text_size(f"option_{index}")[1]/2))
            toggle_icon.set_property("size", [60,60])
            toggle_icon.set_property("opacity", opacity)

            camera.add_item(toggle_icon)
            to_tween.append(toggle_icon)
        case "float" | "int" | "fps":
            for side in ["left", "right"]:
                side_icon = RMS.objects.image(f"{side}_{index}", skin_grab(f"Menus/Options/{side}.png"))
                side_icon.set_property("position:x", 30 + right_side + 50)
                if side == "right": side_icon.set_property("position:x", 30 + right_side + 300)
                side_icon.set_property("position:y", option_text.get_property("position:y") + (camera.get_text_size(f"option_{index}")[1]/2))
                side_icon.set_property("size", [60,60])
                side_icon.set_property("opacity", opacity)

                camera.add_item(side_icon)
                to_tween.append(side_icon)

            t = ref["default"]
            if "value" in cur_ref[list(cur_ref.keys())[index]].keys(): t = cur_ref[list(cur_ref.keys())[index]]["value"]

            suffix = ""
            if "suffix" in cur_ref[list(cur_ref.keys())[index]].keys(): suffix = cur_ref[list(cur_ref.keys())[index]]["suffix"]
            
            if suffix == "%": t = str(int(round(t * 100, 0)))
            elif suffix == "ms": t = str(int(round(t * 1000, 0)))

            if ref["type"] == "fps" and t == 0: t = "Infinite"

            t = str(t)
            t += suffix

            text = RMS.objects.text(f"text_{index}", t)
            text.set_property("font", skin_grab("Fonts/default.ttf"))
            text.set_property("text_align", "center")
            text.set_property("font_size", 48)
            text.set_property("position:y", option_text.get_property("position:y"))
            text.set_property("position:x", camera.get_item(f"left_{index}").get_property("position:x") + 125)
            text.set_property("opacity", opacity)

            camera.add_item(text)
            to_tween.append(text)
    
    i = 0
    for item in to_tween:
        if item.get_property("position:y") - (item.get_property("size:y")/2) > 720: return

        camera.cancel_tween(f"load_{index}_o_{i}")
        camera.cancel_tween(f"load_{index}_x_{i}")

        op = item.get_property("opacity")
        x = item.get_property("position:x")

        item.set_property("opacity", 0)
        item.set_property("position:x", x-20)

        camera.do_tween(f"load_{index}_o_{i}", item, "opacity", op, 0.35, "linear", "out", 0.0125 * index)
        camera.do_tween(f"load_{index}_x_{i}", item, "position:x", x, 0.35, "circ", "out", 0.0125 * index)

        i += 1
    del i
            
def select_option(index):
    y_offset = 0

    if camera.get_item(f"option_{index}").get_property("position:y") + (camera.get_text_size(f"option_{index}")[1]/2) > 720:
        y_offset = -(camera.get_item(f"option_{index}").get_property("position:y") - (720-60-(camera.get_text_size(f"option_{index}")[1]/2)))
    elif camera.get_item(f"option_{index}").get_property("position:y") - (camera.get_text_size(f"option_{index}")[1]/2) < 100:
        y_offset = (100 - (camera.get_item(f"option_{index}").get_property("position:y")))

    for i in range(len(valid_options)):
        opacity = 255/2
        
        type = valid_options[i][1]["type"]

        if i == index: opacity = 255
        
        camera.get_item(f"option_{i}").set_property("opacity", opacity)

        camera.cancel_tween(f"option_{i}_y")
        camera.do_tween(f"option_{i}_y", camera.get_item(f"option_{i}"), "position:y", camera.get_item(f"option_{i}").get_property("position:y") + y_offset, 0.5, "expo", "out")

        match type:
            case "bool":
                camera.get_item(f"toggle_{i}").set_property("opacity", opacity)

                camera.cancel_tween(f"toggle_{i}_y")
                camera.do_tween(f"toggle_{i}_y", camera.get_item(f"toggle_{i}"), "position:y", camera.get_item(f"toggle_{i}").get_property("position:y") + y_offset, 0.5, "expo", "out")
            case "float" | "int" | "fps":
                camera.get_item(f"left_{i}").set_property("opacity", opacity)
                camera.get_item(f"right_{i}").set_property("opacity", opacity)
                camera.get_item(f"text_{i}").set_property("opacity", opacity)               

                camera.cancel_tween(f"left_{i}_y")
                camera.cancel_tween(f"right_{i}_y")
                camera.cancel_tween(f"text_{i}_y")
                camera.do_tween(f"left_{i}_y", camera.get_item(f"left_{i}"), "position:y", camera.get_item(f"left_{i}").get_property("position:y") + y_offset, 0.5, "expo", "out")
                camera.do_tween(f"right_{i}_y", camera.get_item(f"right_{i}"), "position:y", camera.get_item(f"right_{i}").get_property("position:y") + y_offset, 0.5, "expo", "out")
                camera.do_tween(f"text_{i}_y", camera.get_item(f"text_{i}"), "position:y", camera.get_item(f"text_{i}").get_property("position:y") + y_offset, 0.5, "expo", "out")

def option_input(index, input_type):
    option = cur_ref[list(cur_ref.keys())[index]]

    match input_type:
        case "toggle":
            if option["type"] != "bool": return
            else:
                if "value" in option.keys(): cur_ref[list(cur_ref.keys())[index]]["value"] = not option["value"]
                else: cur_ref[list(cur_ref.keys())[index]]["value"] = not option["default"]

                toggled = skin_grab("Menus/Options/toggle_on.png")
                sound = "select"
                if not cur_ref[list(cur_ref.keys())[index]]["value"]:
                    toggled = skin_grab("Menus/Options/toggle_off.png")
                    sound = "back"
                
                play_sfx(sound)

                camera.get_item(f"toggle_{index}").set_property("image_location", toggled)

                # Tween

                camera.cancel_tween(f"scale_toggle_{index}_x")
                camera.cancel_tween(f"scale_toggle_{index}_y")
                
                camera.get_item(f"toggle_{index}").set_property("scale", [0.9,0.9])

                camera.do_tween(f"scale_toggle_{index}_x", camera.get_item(f"toggle_{index}"), "scale:x", 1, 0.3, "expo", "out")
                camera.do_tween(f"scale_toggle_{index}_y", camera.get_item(f"toggle_{index}"), "scale:y", 1, 0.3, "expo", "out")
        case "left" | "right":
            if option["type"] not in ["int", "float", "fps"]: return
            else:
                incr = 0

                if option["type"] in ["int", "fps"] and "increment" not in option.keys(): incr = 1
                else: incr = option["increment"]

                bounds = [None, None]
                if "min" in option.keys(): bounds[0] = option["min"]
                if "max" in option.keys(): bounds[1] = option["max"]

                if input_type == "left": incr *= -1

                current = option["default"]
                if "value" in cur_ref[list(cur_ref.keys())[index]].keys(): current = cur_ref[list(cur_ref.keys())[index]]["value"]

                if input_type == "left":
                    if bounds[0] is not None:
                        if current + incr < bounds[0]: current = bounds[0]
                        else: current += incr
                    else: current += incr
                else:
                    if bounds[1] is not None:
                        if current + incr > bounds[1]: current = bounds[1]
                        else: current += incr
                    else: current += incr

                cur_ref[list(cur_ref.keys())[index]]["value"] = round(current, 5)

                suffix = ""
                if "suffix" in cur_ref[list(cur_ref.keys())[index]].keys(): suffix = cur_ref[list(cur_ref.keys())[index]]["suffix"]

                to_display = str(round(current, 5))
                if suffix == "%": to_display = str(int(round(current * 100)))
                elif suffix == "ms": to_display = str(int(round(current * 1000)))

                if option["type"] == "fps" and current == 0: to_display = "Infinite"

                camera.get_item(f"text_{index}").set_property("text", to_display + suffix)

                # Tween

                move_amt = 5
                if input_type == "left": move_amt *= -1

                orig = camera.get_text_size(f"option_{index}")[0]
                if input_type == "left": orig += 80
                else: orig += 330

                camera.cancel_tween(f"x_{input_type}_{index}")

                camera.get_item(f"{input_type}_{index}").set_property("position:x", orig + move_amt)
                camera.do_tween(f"x_{input_type}_{index}", camera.get_item(f"{input_type}_{index}"), "position:x", orig, 0.5, "back", "out")

                ###

                camera.cancel_tween(f"scale_text_{index}_x")
                camera.cancel_tween(f"scale_text_{index}_y")

                camera.get_item(f"text_{index}").set_property("scale", [1.1,1.1])

                camera.do_tween(f"scale_text_{index}_x", camera.get_item(f"text_{index}"), "scale:x", 1.0, 0.5, "back", "out")
                camera.do_tween(f"scale_text_{index}_y", camera.get_item(f"text_{index}"), "scale:y", 1.0, 0.5, "back", "out")
        case "reset":
            value = option["default"]
            cur_ref[list(cur_ref.keys())[index]]["value"] = value

            match option["type"]:
                case "bool":
                    toggled = skin_grab("Menus/Options/toggle_off.png")
                    if value: toggled = skin_grab("Menus/Options/toggle_on.png")
                    camera.get_item(f"toggle_{index}").set_property("image_location", toggled)
                case "float" | "int" | "fps":
                    suffix = ""
                    if "suffix" in cur_ref[list(cur_ref.keys())[index]].keys(): suffix = cur_ref[list(cur_ref.keys())[index]]["suffix"]

                    to_display = str(round(value, 5))
                    if suffix == "%": to_display = str(int(round(value * 100)))
                    elif suffix == "ms": to_display = str(int(round(value * 1000)))
                    
                    camera.get_item(f"text_{index}").set_property("text", to_display + suffix)

def save_options():
    print(f"[i] Saving options to {current_profile}...")

    file = {}
    for section in options_ref.keys():
        file[section] = {}
        for option in options_ref[section].keys():
            if "value" in options_ref[section][option].keys(): file[section][option] = options_ref[section][option]["value"]
            else: file[section][option] = options_ref[section][option]["default"]
    
    to_save = open(f"Data/{current_profile}/options.json", "w")
    to_save.write(json.dumps(file))

    print(f"[/] Options saved to {current_profile}!")

def make_label(option, index): pass

#

def play_sfx(tag):
    sound = menu_sfx[tag]
    sound.stop()
    sound.set_volume(options_ref["Audio"]["vol_sfx"]["value"] * options_ref["Audio"]["vol_master"]["value"])
    sound.play()