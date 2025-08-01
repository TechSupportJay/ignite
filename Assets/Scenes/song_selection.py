import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random

screen = None
master_data = []

clock = pygame.time.Clock()
fps_cap = 0

# Variables

screen = None
scene = None
camera = None
difficulty_camera = None

focused_element = "song"

###

profile_options = {}
ui = {}
ui_texts = {}

songs_dir = ""
skin_dir = ""

###

song_tabs = []
selection_id = 0

difficulties = []
diff_selection = 0

###

menu_sfx = {}

# Master Functions

def skin_grab(item):
    if os.path.isfile(f"{skin_dir}/{item}"): return (f"{skin_dir}/{item}")
    else: return (f"Assets/Game/Default/{item}")

are_songs = True
def init(data):
    global scene, camera, difficulty_camera
    global profile_options, ui, ui_texts, fps_cap
    global songs_dir, skin_dir
    global song_tabs, selection_id, are_songs
    global diff_selection, difficulties
    global focused_element
    global menu_sfx

    scene = RMS.scenes.scene(screen, "Song Selection")

    camera = RMS.cameras.camera("Songs", 1)
    difficulty_camera = RMS.cameras.camera("Difficulties", 1)
    
    scene.add_camera(camera)
    scene.add_camera(difficulty_camera)

    focused_element = "song"

    # Load Options

    profile_options = json.load(open(f"Data/{data[0]}/options.json"))
    songs_dir = f"{profile_options["Customisation"]["content_folder"]}/Songs"
    skin_dir = f"{profile_options["Customisation"]["content_folder"]}/Skins/{profile_options["Customisation"]["skin"]}"
    ui = json.load(open(skin_grab("Menus/SongSelect/ui.json")))
    ui_texts = json.load(open(skin_grab("texts.json")))["Song Selection"]

    # Objects

    ### Background
    background = RMS.objects.image("background", skin_grab(f"Menus/SongSelect/background.png"))
    background.set_property("size", [1280,720])
    background.set_property("position", [1280/2,720/2])
    camera.add_item(background)

    ### Album Art
    album = RMS.objects.image("album", skin_grab(f"Menus/SongSelect/cover.png"))
    album.set_property("size", ui["album"]["size"])
    album.set_property("position", ui["album"]["position"])
    camera.add_item(album)
    
    ### Song Info Text
    texts = ["Duration", "BPM", "Chartist"]
    i = 0
    for t in texts:
        text = RMS.objects.text(t.lower(), f"{get_text(t)}")
        text.set_property("font", skin_grab(f"Fonts/{get_ui_property("info_texts", "font", "default")}.ttf"))
        text.set_property("text_align", get_ui_property("info_texts", "text_align", "left"))
        text.set_property("font_size", get_ui_property("info_texts", "font_size", 32))
        text.set_property("color", get_ui_property("info_texts", "color", "#FFFFFF"))
        text.set_property("position", [ui["info_texts"]["position"][0],ui["info_texts"]["position"][1] + (ui["info_texts"]["seperation"]*i)])
        camera.add_item(text)
        i += 1
    del i

    # Set Music
    pygame.mixer.music.set_volume(profile_options["Audio"]["vol_menu"] * profile_options["Audio"]["vol_master"])

    # Load Songs
    are_songs = True
    song_tabs = []

    camera.cache_image(skin_grab(f"Menus/SongSelect/tab.png"))
    load_songs()
    
    selection_id = 0

    difficulties = []
    diff_selection = 0

    # Load SFX
    menu_sfx = {}
    sfx = ["scroll", "select", "play", "back"]
    for s in sfx:
        menu_sfx[s] = pygame.mixer.Sound(skin_grab(f"SFX/Menu/{s}.ogg"))
        menu_sfx[s].set_volume(profile_options["Audio"]["vol_sfx"] * profile_options["Audio"]["vol_master"])

    # Add Overlay
    ### Darkness Overlay
    overlay = RMS.objects.rectangle("overlay", "#000000")
    overlay.set_property("size", [1280,720])
    overlay.set_property("position", [1280/2,720/2])
    camera.add_item(overlay)

    # Transition
    camera.set_property("zoom", [1.2,1.2])

    camera.cancel_tween("diff_transition_x")
    camera.cancel_tween("diff_transition_y")
    camera.cancel_tween("diff_transition_o")

    camera.do_tween("diff_transition_x", camera, "zoom:x", 1, 1, "cubic", "out")
    camera.do_tween("diff_transition_y", camera, "zoom:y", 1, 1, "cubic", "out")
    camera.do_tween("diff_transition_o", camera.get_item("overlay"), "opacity", 0, 1)

    # Select
    select_song(selection_id)

    # FPS Cap
    fps_cap = profile_options["Video"]["fps_cap"]

    # Scripts
    load_scripts()
    invoke_script_function("create")

def update():
    clock.tick(fps_cap)
    
    scene.render_scene()
    invoke_script_function("update")

def handle_event(event):
    global selection_id, diff_selection

    match event.type:
        case pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP:
                    match focused_element:
                        case "song":
                            selection_id -= 1
                            if selection_id < 0: selection_id = len(song_tabs)-1
                            select_song(selection_id)
                        case "diff":
                            diff_selection -= 1
                            if diff_selection < 0: diff_selection = len(difficulties)-1
                            select_difficulty(diff_selection)
                    menu_sfx["scroll"].play()
                    invoke_script_function("scroll", ["up"])
                case pygame.K_DOWN:
                    match focused_element:
                        case "song":
                            selection_id += 1
                            if selection_id > len(song_tabs)-1: selection_id = 0
                            select_song(selection_id)
                        case "diff":
                            diff_selection += 1
                            if diff_selection > len(difficulties)-1: diff_selection = 0
                            select_difficulty(diff_selection)
                    menu_sfx["scroll"].play()
                    invoke_script_function("scroll", ["down"])
                case pygame.K_RETURN:
                    match focused_element:
                        case "song":
                            display_difficulties(song_tabs[selection_id][0])
                        case "diff":
                            start_song(song_tabs[selection_id][0], difficulties[diff_selection])
                    invoke_script_function("selected", [selection_id])
                case pygame.K_ESCAPE:
                    if focused_element == "diff":
                        hide_difficulties()
                        invoke_script_function("return")
                case pygame.K_o:
                    master_data.append(["switch_scene", "options"])
        case pygame.VIDEORESIZE:
            camera.set_property("scale", [event.w/1280, event.h/720])
            camera.set_property("position", [(event.w-1280)/2,(event.h-720)/2])

def destroy():
    global camera, scene
    del camera, scene

    pygame.mixer.music.stop()

# Extra Functions

def load_songs():
    global are_songs

    all_songs = next(os.walk(songs_dir), (None, None, []))[1]
    if len(all_songs) == 0:
        are_songs = False

        cam_items = list(camera.items.keys()).copy()

        for item in cam_items:
            camera.remove_item(item)

        no_songs = RMS.objects.text("no_songs", "no songs... :(")
        no_songs.set_property("font", skin_grab("Fonts/default.ttf"))
        no_songs.set_property("font_size", 32)
        no_songs.set_property("text_align", "center")
        no_songs.set_property("position", [1280/2,720/2])

        camera.add_item(no_songs)

        return

    for song in all_songs:
        song_meta = json.load(open(f"{songs_dir}/{song}/meta.json", "r"))

        # Hardcoded Laoyut (temp?)

        make_song_tab(song, song_meta["name"], song_meta["artist"])

def make_song_tab(id, display_name, artist):
    tab_bg = RMS.objects.image(f"tab_{id}", skin_grab(f"Menus/SongSelect/tab.png"))
    tab_bg.set_property("size", camera.get_image_size(skin_grab(f"Menus/SongSelect/tab.png")))

    tab_bg.set_property("position:x", ui["tab_bg"]["position"][0]+(camera.get_image_size(skin_grab(f"Menus/SongSelect/tab.png"))[0]/2))
    tab_bg.set_property("position:y", ui["tab_bg"]["position"][1]+((camera.get_image_size(skin_grab(f"Menus/SongSelect/tab.png"))[1]+ui["tab_bg"]["seperation"])*len(song_tabs)))
    tab_bg.set_property("priority", 10)

    camera.add_item(tab_bg)

    tab_name = RMS.objects.text(f"name_{id}", display_name)
    tab_name.set_property("font", skin_grab(f"Fonts/{get_ui_property("tab_name", "font", "default")}.ttf"))
    tab_name.set_property("font_size", get_ui_property("tab_name", "font_size", 32))
    tab_name.set_property("color", get_ui_property("tab_name", "color", "#FFFFFF"))
    tab_name.set_property("text_align", get_ui_property("tab_name", "text_align", "left"))
    tab_name.set_property("priority", 10)

    tab_name.set_property("position:x", tab_bg.get_property("position:x")-(tab_bg.get_property("size:x")/2)+ui["tab_name"]["position"][0])
    tab_name.set_property("position:y", tab_bg.get_property("position:y")-(tab_bg.get_property("size:y")/2)+ui["tab_name"]["position"][1])

    camera.add_item(tab_name)

    tab_artist = RMS.objects.text(f"artist_{id}", artist)
    tab_artist.set_property("font", skin_grab(f"Fonts/{get_ui_property("tab_artist", "font", "default")}.ttf"))
    tab_artist.set_property("font_size", get_ui_property("tab_artist", "font_size", 32))
    tab_artist.set_property("color", get_ui_property("tab_artist", "color", "#FFFFFF"))
    tab_artist.set_property("text_align", get_ui_property("tab_artist", "text_align", "left"))
    tab_artist.set_property("priority", 10)

    tab_artist.set_property("position:x", tab_bg.get_property("position:x")-(tab_bg.get_property("size:x")/2)+ui["tab_artist"]["position"][0])
    tab_artist.set_property("position:y", tab_bg.get_property("position:y")-(tab_bg.get_property("size:y")/2)+ui["tab_artist"]["position"][1])

    camera.add_item(tab_artist)

    song_tabs.append([id, tab_bg, tab_name, tab_artist])

def select_song(id):
    if not are_songs: return

    move_vertical = 0

    selection_pos_down = song_tabs[id][1].get_property("position:y") + (song_tabs[id][1].get_property("size:y") / 2)
    selection_pos_up = song_tabs[id][1].get_property("position:y") - (song_tabs[id][1].get_property("size:y") / 2)

    if selection_pos_down > 720: move_vertical = selection_pos_down - 720 + 20
    elif selection_pos_up < 0: move_vertical = (selection_pos_up - (ui["tab_bg"]["position"][1]))

    # Change Tabs
    for i in range(len(song_tabs)):
        positon_relative = 0
        opacity = 255/2

        if i == id:
            positon_relative = ui["tab_bg"]["selection"]
            opacity = 255

        positions = [
            ui["tab_bg"]["position"][0]+(camera.get_image_size(skin_grab(f"Menus/SongSelect/tab.png"))[0]/2)+positon_relative,
            (camera.get_image_size(skin_grab(f"Menus/SongSelect/tab.png"))[0]/2)
        ]

        for x in range(3):
            camera.cancel_tween(f"x_{x}_{i}")
            camera.cancel_tween(f"o_{x}_{i}")

        if not song_tabs[i][1].get_property("position:x") == positions[0]:
            camera.do_tween(f"x_0_{i}", song_tabs[i][1], "position:x", positions[0], 0.5, "cubic", "out")
            camera.do_tween(f"x_1_{i}", song_tabs[i][2], "position:x", positions[0]-positions[1]+ui["tab_name"]["position"][0], 0.5, "cubic", "out")
            camera.do_tween(f"x_2_{i}", song_tabs[i][3], "position:x", positions[0]-positions[1]+ui["tab_artist"]["position"][0], 0.5, "cubic", "out")

        for x in range(3): camera.do_tween(f"o_{x}_{i}", song_tabs[i][x+1], "opacity", opacity, 0.25)
        
        if move_vertical != 0:
            for x in range(1,4): camera.cancel_tween(f"y_{x}_{i}")
            for x in range(1,4): camera.do_tween(f"y_{x}_{i}", song_tabs[i][x], "position:y", song_tabs[i][x].get_property("position:y") - move_vertical, 0.5, "cubic", "out")
    
    # Music
    song_ext = ".ogg"
    exts = [".ogg", ".wav", ".mp3"]

    for ex in exts:
        if os.path.isfile(f"{songs_dir}/{song_tabs[id][0]}/audio{ex}"):
            song_ext = ex
            break
    
    pygame.mixer.music.load(f"{songs_dir}/{song_tabs[id][0]}/audio{song_ext}")
    pygame.mixer.music.play()

    song = pygame.mixer.Sound(f"{songs_dir}/{song_tabs[id][0]}/audio{song_ext}")
    song_len = song.get_length()
    del song

    # Modify Info

    ### Album
    cover = camera.get_item("album")
    if os.path.isfile(f"{songs_dir}/{song_tabs[id][0]}/cover.png"):
        camera.cache_image((f"{songs_dir}/{song_tabs[id][0]}/cover.png"))
        cover.set_property("image_location", (f"{songs_dir}/{song_tabs[id][0]}/cover.png"))
    else: cover.set_property("image_location", (skin_grab(f"Menus/SongSelect/cover.png")))

    ### Texts
    duration = camera.get_item("duration")
    bpm = camera.get_item("bpm")
    chartist = camera.get_item("chartist")

    duration.set_property("text", get_text("duration", time.strftime("%M:%S", time.gmtime(song_len))))
    bpm.set_property("text", get_text("bpm", get_from_meta(song_tabs[id][0], "bpm", "N/A")))
    chartist.set_property("text", get_text("chartist", get_from_meta(song_tabs[id][0], "chartist", "N/A")))

    # Tween Info
    ### Album
    cover.set_property("scale", [1.05,1.05])

    camera.cancel_tween("cover_pulse_x")
    camera.cancel_tween("cover_pulse_y")

    camera.do_tween("cover_pulse_x", cover, "scale:x", 1, 0.5, "back", "out")
    camera.do_tween("cover_pulse_y", cover, "scale:y", 1, 0.5, "back", "out")

    texts = ["duration", "bpm", "chartist"]
    i = 1
    for t in texts:
        camera.cancel_tween(f"{t}_x")
        x = camera.get_item(t)
        x.set_property("position:x", ui["info_texts"]["position"][0] + 10)
        camera.do_tween(f"{t}_x", x, "position:x", ui["info_texts"]["position"][0], 0.5, "cubic", "out", 0.015*(i-1))
        i += i
    del i 

def get_from_meta(song_name, variable, default_val):
    meta_file = json.load(open(f"{songs_dir}/{song_name}/meta.json"))
    if variable in meta_file.keys(): return meta_file[variable]
    else: return default_val

def display_difficulties(song):
    global focused_element, difficulties, diff_selection

    if len(difficulties) > 0:
        for i in range(len(difficulties)):
            difficulty_camera.remove_item(f"difficulty_{i}")

    folder_files = next(os.walk(f"{songs_dir}/{song}/charts"), (None, None, []))[2]
    charts = []
    for c in folder_files:
        if c[-5:] == ".json": charts.append(c.replace(".json", ""))
    
    if len(charts) == 1: start_song(song, charts[0]); return

    menu_sfx["select"].play()

    focused_element = "diff"

    camera.cancel_tween("diff_transition_x")
    camera.cancel_tween("diff_transition_y")
    camera.cancel_tween("diff_transition_o")

    camera.do_tween("diff_transition_x", camera, "zoom:x", 1.1, 0.6, "cubic", "out")
    camera.do_tween("diff_transition_y", camera, "zoom:y", 1.1, 0.6, "cubic", "out")
    camera.do_tween("diff_transition_o", camera.get_item("overlay"), "opacity", 255/1.5, 0.5)

    difficulties = charts
    diff_selection = 0

    i = 0
    for difficulty in charts:
        diff_text = RMS.objects.text(f"difficulty_{i}", difficulty)
        diff_text.set_property("font", skin_grab(f"Fonts/{get_ui_property("difficulty", "font", "default")}.ttf"))
        diff_text.set_property("font_size", get_ui_property("difficulty", "font_size", 48))
        diff_text.set_property("text_align", get_ui_property("difficulty", "text_align", "center"))
        diff_text.set_property("color", get_ui_property("difficulty", "color", "#FFFFFF"))
        diff_text.set_property("position:x", get_ui_property("difficulty", "position", [1280/2+50,720/2])[0])
        diff_text.set_property("position:y", get_ui_property("difficulty", "position", [1280/2+50,720/2])[1] - ((get_ui_property("difficulty", "seperation", 60) * len(charts))/2) + (get_ui_property("difficulty", "seperation", 60)*i))
        diff_text.set_property("scale", [0.9,0.9])
        diff_text.set_property("opacity", 0)

        difficulty_camera.cancel_tween(f"x_difficulty_{i}")
        difficulty_camera.do_tween(f"x_difficulty_{i}", diff_text, "position:x", 1280/2, 0.5, "cubic", "out", 0.015 * i)
        difficulty_camera.add_item(diff_text)
        i += 1
    del i

    select_difficulty(0)

def hide_difficulties():
    global focused_element

    menu_sfx["back"].play()

    camera.cancel_tween("diff_transition_x")
    camera.cancel_tween("diff_transition_y")
    camera.cancel_tween("diff_transition_o")

    camera.do_tween("diff_transition_x", camera, "zoom:x", 1, 0.6, "cubic", "out")
    camera.do_tween("diff_transition_y", camera, "zoom:y", 1, 0.6, "cubic", "out")
    camera.do_tween("diff_transition_o", camera.get_item("overlay"), "opacity", 0, 0.5)

    for i in range(len(difficulties)):
        difficulty_camera.cancel_tween(f"o_difficulty_{i}")
        difficulty_camera.cancel_tween(f"y_difficulty_{i}")

        diff = difficulty_camera.get_item(f"difficulty_{i}")

        difficulty_camera.do_tween(f"o_difficulty_{i}", diff, "opacity", 0, 0.5)
        difficulty_camera.do_tween(f"y_difficulty_{i}", diff, "position:y", diff.get_property("position:y") + 50, 0.5, "cubic", "in")

    focused_element = "song"

def select_difficulty(id):
    for i in range(len(difficulties)):
        diff = difficulty_camera.get_item(f"difficulty_{i}")

        opacity = 255/3
        scale = 0.9

        if i == id:
            opacity = 255
            scale = 1

        if opacity != diff.get_property("opacity"):
            difficulty_camera.cancel_tween(f"o_difficulty_{i}")
            difficulty_camera.do_tween(f"o_difficulty_{i}", diff, "opacity", opacity, 0.15)
        
        if scale != diff.get_property("scale:x"):
            difficulty_camera.cancel_tween(f"sx_difficulty_{i}")
            difficulty_camera.cancel_tween(f"sy_difficulty_{i}")

            difficulty_camera.do_tween(f"sx_difficulty_{i}", diff, "scale:x", scale, 0.35, "back", "out")
            difficulty_camera.do_tween(f"sy_difficulty_{i}", diff, "scale:y", scale, 0.35, "back", "out")

def start_song(song, difficulty):
    menu_sfx["play"].play()
    master_data.append(["load_song", song, difficulty])

def resize(size):
    for cam in scene.cameras.keys():
        scene.cameras[cam].set_property("scale", [size[0]/1280,size[1]/720])
        scene.cameras[cam].set_property("position", [(size[0]-1280)/2,(size[1]-720)/2])

def get_text(key, sub = ""):
    sub = str(sub)
    if not key in ui_texts.keys(): return sub
    else: return ui_texts[key].replace("%s", sub)

def get_ui_property(parent, key, otherwise):
    if not parent in ui.keys(): return otherwise
    if not key in ui[parent].keys(): return otherwise
    else: return ui[parent][key]

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

    print(f"[i] Added Script: {prefix}{tag}")

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
    print("[i] Loading Scene Script...")

    global user_scripts
    user_scripts = []

    if os.path.isfile(skin_grab(f"Scripts/#song_selection.py")): add_script("", "song", skin_grab(f"Scripts/#song_selection.py"))

def set_global(prop, val):
    globals()[prop] = val