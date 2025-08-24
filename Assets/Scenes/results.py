import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random

screen = None
master_data = []

# Variables

screen = None
scene = None
camera = None

sound = None

#

skin_dir = ""
ui = {}
ui_texts = {}

# Master Functions

def init(data = []):
    global scene, camera, sound
    global skin_dir, ui_texts, ui

    scene = RMS.scenes.scene(screen, "Template")
    camera = RMS.cameras.camera("HUD", 1)
    scene.add_camera(camera)

    #

    current_profile = data[0]
    profile_options = json.load(open(f"Data/{current_profile}/options.json"))
    skin_dir = f"{profile_options["Customisation"]["content_folder"]}/Skins/{profile_options["Customisation"]["skin"]}"

    ui = json.load(open(skin_grab("Results/ui.json")))
    ui_texts = json.load(open(skin_grab("texts.json")))

    game_data = data[1]
    
    # Images
    ### Background

    background = RMS.objects.image("background", skin_grab("Results/background.png"))
    background.set_property("size", [1280,720])
    background.set_property("position", [1280/2,720/2])
    camera.add_item(background)

    # Texts
    song_stuff = ["name", "artist", "chartist", "difficulty", "bpm"]
    for s in song_stuff:
        content = ""
        if s in ["chartist", "bpm", "artist"]: content = get_text("Song Selection", s,  data[1]["meta"][s])
        elif s == "difficulty": content = data[1][s]
        else: content = data[1]["meta"][s]

        text = RMS.objects.text(s, content)
        text.set_property("position", get_ui_property(s, "position", [0,0]))
        text.set_property("font", skin_grab(f"Fonts/{get_ui_property(s, "font", "default.ttf")}"))
        text.set_property("font_size", get_ui_property(s, "font_size", 32))
        text.set_property("text_align", get_ui_property(s, "text_align", "left"))
        text.set_property("color", get_ui_property(s, "color", "#FFFFFF"))

        camera.add_item(text)
    
    other_stuff = ["perf", "okay", "bad", "score", "accuracy", "highest", "misses"]
    for s in other_stuff:
        if s in ["perf", "okay", "bad"]: content = data[1]["ratings"][s]
        elif s == "accuracy": content = str(round(data[1][s]*100, 2))
        else: content = data[1][s]
        content = get_text("Results", s, str(content))

        text = RMS.objects.text(s, str(content))
        text.set_property("position", get_ui_property(s, "position", [0,0]))
        text.set_property("font", skin_grab(f"Fonts/{get_ui_property(s, "font", "default.ttf")}"))
        text.set_property("font_size", get_ui_property(s, "font_size", 32))
        text.set_property("text_align", get_ui_property(s, "text_align", "left"))
        text.set_property("color", get_ui_property(s, "color", "#FFFFFF"))

        camera.add_item(text)
    
    # Album

    album_path = f"{profile_options["Customisation"]["content_folder"]}/Songs/{data[1]["folder"]}/album.png"
    if not os.path.isfile(f"{profile_options["Customisation"]["content_folder"]}/Songs/{data[1]["folder"]}/album.png"):
        album_path = skin_grab("Menus/SongSelect/cover.png")
    album = RMS.objects.image("album", album_path)
    album.set_property("position", get_ui_property("album", "position", [0,0]))
    album.set_property("size", get_ui_property("album", "size", [50,50]))

    camera.add_item(album)

    ### Flash

    flash = RMS.objects.rectangle("flash", "#FFFFFF")
    flash.set_property("size", [1280,720])
    flash.set_property("position", [1280/2,720/2])
    flash.set_property("opacity", 255/2)
    camera.add_item(flash)

    ### Overlay

    overlay = RMS.objects.rectangle("overlay", "#000000")
    overlay.set_property("size", [1280,720])
    overlay.set_property("position", [1280/2,720/2])
    camera.add_item(overlay)

    ### Rank

    camera.cache_image(skin_grab(f"Results/{game_data["rank"]}.png"))
    rank = RMS.objects.image("rank", skin_grab(f"Results/{game_data["rank"]}.png"))
    rank.set_property("size", camera.get_image_size(skin_grab(f"Results/{game_data["rank"]}.png")))
    rank.set_property("position", ui["rank"]["position"])
    camera.add_item(rank)

    # Animation

    rank.set_property("opacity", 0)
    rank.set_property("scale", [0,0])

    go_to = rank.get_property("position")
    rank.set_property("position", [1280/2,720/2])

    camera.do_tween("rank_x", rank, "scale:x", 0.8, 1, "expo", "out")
    camera.do_tween("rank_y", rank, "scale:y", 0.8, 1, "expo", "out")

    camera.do_tween("rank_px", rank, "position:x", go_to[0], 0.6, "circ", "in", 0.6)
    camera.do_tween("rank_py", rank, "position:y", go_to[1], 0.6, "circ", "in", 0.6)

    camera.do_tween("rank_o", rank, "opacity", 255, 0.6)

    camera.do_tween("overlay", overlay, "opacity", 0, 0.0001, delay=1.2)
    camera.do_tween("flash", flash, "opacity", 0, 1, delay=1.2)

    camera.do_tween("rank_x_2", rank, "scale:x", 1, 0.25, "back", "out", delay=1.2)
    camera.do_tween("rank_y_2", rank, "scale:y", 1, 0.25, "back", "out", delay=1.2)

    to_move = ["album", "name", "artist", "difficulty", "chartist", "bpm", "score", "accuracy", "highest", "perf", "okay", "bad", "misses"]
    i = 0
    for obj in to_move:
        obj = camera.get_item(obj)
        obj.set_property("position:x", obj.get_property("position:x")-20)
        obj.set_property("opacity", 0)
        camera.do_tween(f"{obj}_x", obj, "position:x", obj.get_property("position:x")+20, 0.5, "expo", "out", 1+i*0.05)
        camera.do_tween(f"{obj}_o", obj, "opacity", 255, 0.5, delay=1+i*0.05)
        i += 1
    del i

    # Sound

    sound = pygame.mixer.Sound(skin_grab(f"Results/SFX/{game_data["rank"]}.ogg"))
    sound.set_volume(profile_options["Audio"]["vol_sfx"] * profile_options["Audio"]["vol_master"])

    sound.play()

def update():
    scene.render_scene()

def handle_event(event):
    match event.type:
        case pygame.KEYDOWN:
            match event.key:
                case pygame.K_RETURN: master_data.append(["switch_scene", "song_selection"])
        case pygame.VIDEORESIZE:
            camera.set_property("scale", [event.w/1280, event.h/720])
            camera.set_property("position", [(event.w-1280)/2,(event.h-720)/2])

def destroy():
    sound.stop()
    global camera, scene
    del camera, scene

def resize(size):
    for cam in scene.cameras.keys():
        scene.cameras[cam].set_property("scale", [size[0]/1280,size[1]/720])
        scene.cameras[cam].set_property("position", [(size[0]-1280)/2,(size[1]-720)/2])

def skin_grab(item):
    if os.path.isfile(f"{skin_dir}/{item}"): return (f"{skin_dir}/{item}")
    else: return (f"Assets/Game/Default/{item}")

def get_text(parent, key, sub = ""):
    sub = str(sub)
    if not key in ui_texts[parent].keys(): return sub
    else: return ui_texts[parent][key].replace("%s", sub)

def get_ui_property(parent, key, otherwise):
    if not parent in ui.keys(): return otherwise
    if not key in ui[parent].keys(): return otherwise
    else: return ui[parent][key]