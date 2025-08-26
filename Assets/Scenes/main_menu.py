import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random

screen = None
master_data = []

# Variables

screen = None
scene = None
camera = None

clock = pygame.time.Clock()

#

profile_options = {}
ui = {}
menu_sfx = {}

fps_cap = 0

buttons = []
selected_index = 0

#

beat_time = 0
next_beat = 0

started_bumping = False

#

pygame.mixer.init()

# Scripts

class user_script_class_template():
    def __init__(self): pass
    def create(self): pass
    def update(self): pass
    def scroll(self, direction): pass
    def selected(self, song_info): pass
    def cancelled(self): pass

user_scripts = []

def add_script(prefix, tag, path):
    global user_scripts

    if tag[:1] == "_": return

    to_exec = f"class user_script_{prefix}{tag}(user_script_class_template):\n"
    for line in open((path), "r").readlines():
        to_exec += f"    {line}"
    exec(f"{to_exec}\nsong_script_{prefix}{tag} = user_script_{prefix}{tag}()\nuser_scripts.append(song_script_{prefix}{tag})")

def invoke_script_function(tag, data = []):
    if len(user_scripts) == 0: return

    for script in user_scripts:
        match tag:
            case "create": script.create()
            case "update": script.update()
            case "select": script.selected(data[0])
            case "return": script.cancelled()
            case "scroll": script.scroll(data[0])

def load_scripts():
    fancy_print(f"Loading Scene Script...", "Main Menu", "i")

    global user_scripts
    user_scripts = []

    if os.path.isfile(skin_grab(f"Scripts/#main_menu.py")):
        add_script("", "song", skin_grab(f"Scripts/#main_menu.py"))
        fancy_print(f"Added Scene Script", "Main Menu", "/")
    else:
        fancy_print(f"No Scene Script Found", "Main Menu", "i")

def set_global(prop, val):
    globals()[prop] = val

# Master Functions

def init(data = []):
    global scene, camera
    global skin_dir, ui, menu_sfx
    global buttons, selected_index
    global beat_time, next_beat
    global fps_cap
    global started_bumping

    scene = RMS.scenes.scene(screen, "Template")
    camera = RMS.cameras.camera("HUD", 1)
    scene.add_camera(camera)

    # Variables

    profile_options = json.load(open(f"Data/{data[0]}/options.json"))
    skin_dir = f"{profile_options["Customisation"]["content_folder"]}/Skins/{profile_options["Customisation"]["skin"]}"

    ui = json.load(open(skin_grab("Menus/MainMenu/ui.json")))
    fps_cap = profile_options["Video"]["fps_cap"]

    ### SFX

    menu_sfx = {}
    sfx = ["scroll", "select", "back"]
    for s in sfx:
        menu_sfx[s] = pygame.mixer.Sound(skin_grab(f"SFX/Menu/{s}.ogg"))
        menu_sfx[s].set_volume(profile_options["Audio"]["vol_sfx"] * profile_options["Audio"]["vol_master"])

    # Logo

    camera.cache_image(skin_grab("Menus/MainMenu/logo.png"))
    logo = RMS.objects.image("logo", skin_grab("Menus/MainMenu/logo.png"))
    logo.set_property("size", camera.get_image_size(skin_grab("Menus/MainMenu/logo.png")))
    logo.set_property("position", [1280/2, ui["logo"]["position"][1]])
    logo.set_property("priority", 5)
    camera.add_item(logo)

    # Elements
    ### BG

    camera.cache_image(skin_grab("Menus/MainMenu/background.png"))
    background = RMS.objects.image("background", skin_grab("Menus/MainMenu/background.png"))
    background.set_property("size", [1280,720])
    background.set_property("position", [1280/2, 720/2])
    camera.add_item(background)

    ### Version String
    version = RMS.objects.text("version", "Version 0.8.5")
    version.set_property("font", skin_grab("Fonts/default.ttf"))
    version.set_property("font_size", 20)
    version.set_property("text_align", "center")
    version.set_property("position", [1280/2, 20])
    camera.add_item(version)

    ### Buttons
    buttons = []
    selected_index = 0

    make_buttons()
    select_button(selected_index, False)

    start_music = True

    if len(data[1]) == 2:
        i = 0
        for button in buttons:
            if button[0].get_property("tag").replace("btn_", "") == data[1][1]:
                selected_index = i
                select_button(i, False)
                break
            i += 1
        del i

        if data[1][1] in ["options", "content"]: start_music = False
        
    # Menu Schmusic
    if start_music:
        pygame.mixer.music.load(skin_grab("Menus/MainMenu/menu_music.wav"))
        pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(profile_options["Audio"]["vol_master"] * profile_options["Audio"]["vol_menu"])

    # BPM
    beat_time = (60/ui["bpm"])
    started_bumping = False

    # Splash

    ### Background
    splash_background = RMS.objects.rectangle("splash_background", "#000000")
    splash_background.set_property("size", [1280,720])
    splash_background.set_property("position", [1280/2,720/2])
    splash_background.set_property("priority", 2)
    splash_background.set_property("opacity", 0)

    camera.add_item(splash_background)

    if data[1][0]:
        splash_background.set_property("opacity", 255)

        # PyGame
        camera.cache_image(skin_grab("Menus/MainMenu/pygame.png"))
        pygame_splash = RMS.objects.image("pygame", skin_grab("Menus/MainMenu/pygame.png"))
        pygame_splash.set_property("size", camera.get_image_size(skin_grab("Menus/MainMenu/pygame.png")))
        pygame_splash.set_property("position", [1280/2, 720/2])
        pygame_splash.set_property("priority", 2)
        camera.add_item(pygame_splash)

        ### Animation
        pygame_splash.set_property("scale", [0.8,0.8])
        pygame_splash.set_property("opacity", 0)

        camera.do_tween("pygame_x_0", pygame_splash, "scale:x", 1, 1/(ui["bpm"]/160), "expo", "out")
        camera.do_tween("pygame_y_0", pygame_splash, "scale:y", 1, 1/(ui["bpm"]/160), "expo", "out")
        camera.do_tween("pygame_a_0", pygame_splash, "opacity", 255, 0.35, delay=0.2)

        camera.do_tween("pygame_x_1", pygame_splash, "scale:x", 0.8, 0.75/(ui["bpm"]/160), "expo", "in", 0.75/(ui["bpm"]/160))
        camera.do_tween("pygame_y_1", pygame_splash, "scale:y", 0.8, 0.75/(ui["bpm"]/160), "expo", "in", 0.75/(ui["bpm"]/160))
        camera.do_tween("pygame_a_1", pygame_splash, "opacity", 0, 0.35/(ui["bpm"]/160), delay=1/(ui["bpm"]/160))

        ### Ignite
        logo.set_property("position", [1280/2, 720/2])
        logo.set_property("scale", [2,2])
        logo.set_property("opacity", 0)

        camera.do_tween("logo_x_0", logo, "scale:x", 1.5, 1.25/(ui["bpm"]/160), "expo", "out", 1.5/(ui["bpm"]/160))
        camera.do_tween("logo_y_0", logo, "scale:y", 1.5, 1.25/(ui["bpm"]/160), "expo", "out", 1.5/(ui["bpm"]/160))
        camera.do_tween("logo_a_0", logo, "opacity", 255, 0.35, delay=1.5/(ui["bpm"]/160))

        camera.do_tween("logo_py_1", logo, "position:y", ui["logo"]["position"][1], 1.2/(ui["bpm"]/160), "expo", "in", 1.8/(ui["bpm"]/160))
        camera.do_tween("logo_x_1", logo, "scale:x", 1, 0.75/(ui["bpm"]/160), "circ", "out", 2.3/(ui["bpm"]/160))
        camera.do_tween("logo_y_1", logo, "scale:y", 1, 0.75/(ui["bpm"]/160), "circ", "out", 2.3/(ui["bpm"]/160))

        # Flash
        flash = RMS.objects.rectangle("flash", "#FFFFFF")
        flash.set_property("size", [1280,720])
        flash.set_property("position", [1280/2,720/2])
        flash.set_property("opacity", 255/2)

        camera.add_item(flash)

        camera.do_tween("flash_go", flash, "opacity", 0, 1, delay=3/(ui["bpm"]/160))
        camera.do_tween("hide_bg", splash_background, "opacity", 0, 0.0001, delay=3/(ui["bpm"]/160))

        # Zoom
        camera.do_tween("cam_x_0", camera, "zoom:x", 1.3, 0.7/(ui["bpm"]/160), "expo", "in", 2.3/(ui["bpm"]/160))
        camera.do_tween("cam_y_0", camera, "zoom:y", 1.3, 0.7/(ui["bpm"]/160), "expo", "in", 2.3/(ui["bpm"]/160))
        camera.do_tween("cam_x_1", camera, "zoom:x", 1, 1/(ui["bpm"]/160), "expo", "out", 3/(ui["bpm"]/160))
        camera.do_tween("cam_y_1", camera, "zoom:y", 1, 1/(ui["bpm"]/160), "expo", "out", 3/(ui["bpm"]/160))
    else: menu_sfx["back"].play()

def update():
    global next_beat, started_bumping
    
    if time.time() >= next_beat and started_bumping:
        camera.cancel_tween("cam_x")
        camera.cancel_tween("cam_y")
        camera.set_property("zoom", [1.02,1.02])
        camera.do_tween("cam_x", camera, "zoom:x", 1, 1, "expo", "out")
        camera.do_tween("cam_y", camera, "zoom:y", 1, 1, "expo", "out")

        camera.cancel_tween("logo_x")
        camera.cancel_tween("logo_y")
        camera.get_item("logo").set_property("scale", [1.05,1.05])
        camera.do_tween("logo_x", camera.get_item("logo"), "scale:x", 1, 1, "expo", "out")
        camera.do_tween("logo_y", camera.get_item("logo"), "scale:y", 1, 1, "expo", "out")

        next_beat += beat_time
    elif not started_bumping and camera.get_item("splash_background").get_property("opacity") == 0:
        started_bumping = True
        next_beat = time.time() + beat_time

    clock.tick(fps_cap)

    scene.render_scene()

def handle_event(event):
    global selected_index, next_beat

    match event.type:
        case pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP:
                    if camera.has_item("splash_background"):
                        if camera.get_item("splash_background").get_property("opacity") == 255: return
                    selected_index -= 1
                    if selected_index < 0: selected_index = len(buttons)-1
                    select_button(selected_index)
                case pygame.K_DOWN:
                    if camera.has_item("splash_background"):
                        if camera.get_item("splash_background").get_property("opacity") == 255: return
                    selected_index += 1
                    if selected_index >= len(buttons): selected_index = 0
                    select_button(selected_index)
                case pygame.K_RETURN:
                    if camera.get_item("splash_background").get_property("opacity") == 255:
                        tweens = [
                            "pygame_x_0", "pygame_y_0", "pygame_a_0",
                            "pygame_x_1", "pygame_y_1", "pygame_a_1",
                            "logo_x_0", "logo_y_0", "logo_a_0",
                            "logo_py_1", "logo_x_1", "logo_y_1",
                            "cam_x_0", "cam_x_1", "cam_y_0", "cam_y_1",
                            "flash_set", "flash_go", "hide_bg"
                        ]
                        for t in tweens: camera.cancel_tween(t)

                        camera.get_item("pygame").set_property("opacity", 0)

                        camera.get_item("logo").set_property("position", [1280/2, ui["logo"]["position"][1]])
                        camera.get_item("logo").set_property("scale", [1,1])
                        camera.get_item("logo").set_property("opacity", 255)

                        camera.get_item("flash").set_property("opacity", 255/2)
                        camera.do_tween("flash_go", camera.get_item("flash"), "opacity", 0, 1)
                        camera.get_item("splash_background").set_property("opacity", 0)

                        camera.set_property("zoom", [1.3,1.3])
                        camera.do_tween("cam_x", camera, "zoom:x", 1, 1, "expo", "out")
                        camera.do_tween("cam_y", camera, "zoom:y", 1, 1, "expo", "out")
                        
                        next_beat -= 4
                    else:
                        press_button(buttons[selected_index][0].get_property("tag").replace("btn_", ""))
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

def make_buttons():
    global buttons

    for button_name in ui["buttons"].keys():
        camera.cache_image(skin_grab(f"Menus/MainMenu/Buttons/active_{button_name}.png"))
        camera.cache_image(skin_grab(f"Menus/MainMenu/Buttons/inactive_{button_name}.png"))

        button = RMS.objects.image(f"btn_{button_name}", skin_grab(f"Menus/MainMenu/Buttons/inactive_{button_name}.png"))
        button.set_property("size", camera.get_image_size(skin_grab(f"Menus/MainMenu/Buttons/inactive_{button_name}.png")))
        button.set_property("position", ui["buttons"][button_name]["position"])
        button.set_property("scale", ui["buttons"][button_name]["inactive"])

        buttons.append([button, ui["buttons"][button_name]["inactive"].copy(), ui["buttons"][button_name]["active"].copy()])
        camera.add_item(button)

def select_button(index, sound = True):
    i = 0
    for tri in buttons:
        tri = tri.copy()
        button = tri[0]
        button_name = button.get_property("tag").replace("btn_", "")

        camera.cancel_tween(f"button_{i}_x")
        camera.cancel_tween(f"button_{i}_y")

        if i == index:
            button.set_property("image_location", skin_grab(f"Menus/MainMenu/Buttons/active_{button_name}.png"))
            button.set_property("size", camera.get_image_size(skin_grab(f"Menus/MainMenu/Buttons/active_{button_name}.png")))
            camera.do_tween(f"button_{i}_x", button, "scale:x", tri[2][0], 0.5, "expo", "out")
            camera.do_tween(f"button_{i}_y", button, "scale:y", tri[2][1], 0.5, "expo", "out")
        else:
            button.set_property("image_location", skin_grab(f"Menus/MainMenu/Buttons/inactive_{button_name}.png"))
            button.set_property("size", camera.get_image_size(skin_grab(f"Menus/MainMenu/Buttons/inactive_{button_name}.png")))
            camera.do_tween(f"button_{i}_x", button, "scale:x", tri[1][0], 0.5, "expo", "out")
            camera.do_tween(f"button_{i}_y", button, "scale:y", tri[1][1], 0.5, "expo", "out")

        i += 1

    if sound:
        menu_sfx["scroll"].stop()
        menu_sfx["scroll"].play()

def press_button(name):
    menu_sfx["select"].play()

    match name:
        case "single": master_data.append(["switch_scene", "song_selection"])
        case "options": master_data.append(["switch_scene", "options"])
        case "content":
            menu_sfx["select"].stop()
            master_data.append(["switch_scene", "download"])
        case "exit": exit()

#

def fancy_print(content, header = "", icon = ""):
    print()
    to_print = ""
    if header != "": to_print = (f"[{header} - {time.strftime("%H:%M:%S", time.gmtime())}]")
    else: to_print = (f"[{time.strftime("%H:%M:%S", time.gmtime())}]")
    if icon != "": to_print = f"[{icon}] {to_print}"

    print(f"{to_print} ---------")
    print(content)