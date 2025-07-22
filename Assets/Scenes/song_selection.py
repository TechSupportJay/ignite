import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random

screen = None
master_data = []

# Variables

screen = None
scene = None
camera = None

###

profile_options = {}

songs_dir = ""
skin_dir = ""

###

song_tabs = []
selection_id = 0

# Master Functions

def skin_grab(item):
    if os.path.isfile(f"{skin_dir}/{item}"): return (f"{skin_dir}/{item}")
    else: return (f"Assets/Game/Default/{item}")

def init(data):
    global scene, camera
    global profile_options, songs_dir, skin_dir
    global song_tabs, selection_id

    scene = RMS.scenes.scene(screen, "Song Selection")
    camera = RMS.cameras.camera("HUD", 1)
    scene.add_camera(camera)

    # Load Options

    profile_options = json.load(open(f"Data/{data[0]}/options.json"))
    songs_dir = f"{profile_options["Customisation"]["content_folder"]}/Songs"
    skin_dir = f"{profile_options["Customisation"]["content_folder"]}/Skins/{profile_options["Customisation"]["skin"]}"

    # Objects

    ### Background
    background = RMS.objects.image("background", skin_grab(f"SongSelect/background.png"))
    background.set_property("size", [1280,720])
    background.set_property("position", [1280/2,720/2])
    camera.add_item(background)

    ### Album Art
    album = RMS.objects.image("album", skin_grab(f"SongSelect/cover.png"))
    album.set_property("size", [350,350])
    album.set_property("position", [25+(350/2),25+(350/2)])
    camera.add_item(album)
    
    ### Song Info Text
    texts = ["Duration", "BPM", "Chartist"]
    i = 0
    for t in texts:
        text = RMS.objects.text(t.lower(), f"{t}: X")
        text.set_property("font", skin_grab(f"Fonts/default.ttf"))
        text.set_property("font_size", 26)
        text.set_property("position", [25,380 + (30*i)])
        camera.add_item(text)
        i += 1
    del i

    # Set Music
    pygame.mixer.music.set_volume(profile_options["Audio"]["volume"]["menu"] * profile_options["Audio"]["volume"]["master"])

    # Load Songs
    song_tabs = []

    camera.cache_image(skin_grab(f"SongSelect/tab.png"))
    load_songs()
    
    selection_id = 0

    select_song(selection_id)

def update():
    scene.render_scene()

def handle_event(event):
    global selection_id

    match event.type:
        case pygame.KEYDOWN:
            match event.key:
                case pygame.K_UP:
                    selection_id -= 1
                    if selection_id < 0: selection_id = len(song_tabs)-1
                    select_song(selection_id)
                case pygame.K_DOWN:
                    selection_id += 1
                    if selection_id > len(song_tabs)-1: selection_id = 0
                    select_song(selection_id)
                case pygame.K_RETURN:
                    master_data.append(["load_song", song_tabs[selection_id][0], _get_first_diff(song_tabs[selection_id][0])])
        case pygame.VIDEORESIZE:
            camera.set_property("scale", [event.w/1280, event.h/720])
            camera.set_property("position", [(event.w-1280)/2,(event.h-720)/2])

def destroy():
    global camera, scene
    del camera, scene

# Extra Functions

def load_songs():
    all_songs = next(os.walk(songs_dir), (None, None, []))[1]
    for song in all_songs:
        song_meta = json.load(open(f"{songs_dir}/{song}/meta.json", "r"))

        # Hardcoded Laoyut (temp?)

        make_song_tab(song, song_meta["name"], song_meta["artist"])

def make_song_tab(id, display_name, artist):
    tab_bg = RMS.objects.image(f"tab_{id}", skin_grab(f"SongSelect/tab.png"))
    tab_bg.set_property("size", camera.get_image_size(skin_grab(f"SongSelect/tab.png")))

    tab_bg.set_property("position:x", 1280-(camera.get_image_size(skin_grab(f"SongSelect/tab.png"))[0]/2))
    tab_bg.set_property("position:y", 60+((camera.get_image_size(skin_grab(f"SongSelect/tab.png"))[1]+10)*len(song_tabs)))

    camera.add_item(tab_bg)

    tab_name = RMS.objects.text(f"name_{id}", display_name)
    tab_name.set_property("font", skin_grab(f"Fonts/default.ttf"))
    tab_name.set_property("font_size", 32)

    tab_name.set_property("position:x", tab_bg.get_property("position:x")-(tab_bg.get_property("size:x")/2)+30)
    tab_name.set_property("position:y", tab_bg.get_property("position:y")-(tab_bg.get_property("size:y")/2)+11)

    camera.add_item(tab_name)

    tab_artist = RMS.objects.text(f"artist_{id}", artist)
    tab_artist.set_property("font", skin_grab(f"Fonts/default.ttf"))
    tab_artist.set_property("font_size", 20)

    tab_artist.set_property("position:x", tab_bg.get_property("position:x")-(tab_bg.get_property("size:x")/2)+30)
    tab_artist.set_property("position:y", tab_bg.get_property("position:y")-(tab_bg.get_property("size:y")/2)+47)

    camera.add_item(tab_artist)

    song_tabs.append([id, tab_bg, tab_name, tab_artist])

def select_song(id):
    # Change Tabs
    for i in range(len(song_tabs)):
        positon_relative = 100
        opacity = 255/2

        if i == id:
            positon_relative = 0
            opacity = 255

        positions = [
            1280-(camera.get_image_size(skin_grab(f"SongSelect/tab.png"))[0]/2)+positon_relative,
            (1280-(camera.get_image_size(skin_grab(f"SongSelect/tab.png"))[0]/2)+positon_relative)-(song_tabs[id][1].get_property("size:x")/2)+30
        ]

        for x in range(3):
            camera.cancel_tween(f"x_{x}_{i}")
            camera.cancel_tween(f"o_{x}_{i}")

        if not song_tabs[i][1].get_property("position:x") == positions[0]:
            camera.do_tween(f"x_0_{i}", song_tabs[i][1], "position:x", positions[0], 0.5, "cubic", "out")
            camera.do_tween(f"x_1_{i}", song_tabs[i][2], "position:x", positions[1], 0.5, "cubic", "out")
            camera.do_tween(f"x_2_{i}", song_tabs[i][3], "position:x", positions[1], 0.5, "cubic", "out")

            for x in range(3): camera.do_tween(f"o_{x}_{i}", song_tabs[i][x+1], "opacity", opacity, 0.25)
    
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
    else: cover.set_property("image_location", (skin_grab(f"SongSelect/cover.png")))

    ### Texts
    duration = camera.get_item("duration")
    bpm = camera.get_item("bpm")
    chartist = camera.get_item("chartist")

    duration.set_property("text", f"Duration: {time.strftime("%M:%S", time.gmtime(song_len))}")
    bpm.set_property("text", f"BPM: {get_from_meta(song_tabs[id][0], "bpm", "N/A")}")
    chartist.set_property("text", f"Chartist: {get_from_meta(song_tabs[id][0], "chartist", "N/A")}")

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
        x.set_property("position:x", 25 + 10)
        camera.do_tween(f"{t}_x", x, "position:x", 25, 0.5, "cubic", "out", 0.015*(i-1))
        i += i
    del i 

def get_from_meta(song_name, variable, default_val):
    meta_file = json.load(open(f"{songs_dir}/{song_name}/meta.json"))
    if variable in meta_file.keys(): return meta_file[variable]
    else: return default_val

# TEMPORARY!!

def _get_first_diff(song_id):
    charts = next(os.walk(f"{songs_dir}/{song_id}/charts"), (None, None, []))[2]
    return charts[0].replace(".json", "")