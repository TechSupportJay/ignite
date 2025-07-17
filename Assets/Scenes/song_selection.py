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

    background = RMS.objects.image("background", f"{skin_dir}/menu_background.png")
    background.set_property("size", [1280,720])
    background.set_property("position", [1280/2,720/2])
    camera.add_item(background)

    # Load Songs
    song_tabs = []

    camera.cache_image(f"{skin_dir}/SongSelect/tab.png")
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
                    master_data.append(["load_song", song_tabs[selection_id][0]])
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
    tab_bg = RMS.objects.image(f"tab_{id}", f"{skin_dir}/SongSelect/tab.png")
    tab_bg.set_property("size", camera.get_image_size(f"{skin_dir}/SongSelect/tab.png"))

    tab_bg.set_property("position:x", 1280-(camera.get_image_size(f"{skin_dir}/SongSelect/tab.png")[0]/2))
    tab_bg.set_property("position:y", 100+((camera.get_image_size(f"{skin_dir}/SongSelect/tab.png")[1]+10)*len(song_tabs)))

    camera.add_item(tab_bg)

    tab_name = RMS.objects.text(f"name_{id}", display_name)
    tab_name.set_property("font", f"{skin_dir}/Fonts/default.ttf")
    tab_name.set_property("font_size", 32)

    tab_name.set_property("position:x", tab_bg.get_property("position:x")-(tab_bg.get_property("size:x")/2)+30)
    tab_name.set_property("position:y", tab_bg.get_property("position:y")-(tab_bg.get_property("size:y")/2)+11)

    camera.add_item(tab_name)

    tab_artist = RMS.objects.text(f"artist_{id}", artist)
    tab_artist.set_property("font", f"{skin_dir}/Fonts/default.ttf")
    tab_artist.set_property("font_size", 20)

    tab_artist.set_property("position:x", tab_bg.get_property("position:x")-(tab_bg.get_property("size:x")/2)+30)
    tab_artist.set_property("position:y", tab_bg.get_property("position:y")-(tab_bg.get_property("size:y")/2)+47)

    camera.add_item(tab_artist)

    song_tabs.append([id, tab_bg, tab_name, tab_artist])

def select_song(id):
    for i in range(len(song_tabs)):
        positon_relative = 100
        opacity = 255/2

        if i == id:
            positon_relative = 0
            opacity = 255

        positions = [
            1280-(camera.get_image_size(f"{skin_dir}/SongSelect/tab.png")[0]/2)+positon_relative,
            (1280-(camera.get_image_size(f"{skin_dir}/SongSelect/tab.png")[0]/2)+positon_relative)-(song_tabs[id][1].get_property("size:x")/2)+30
        ]

        for x in range(3):
            camera.cancel_tween(f"x_{x}_{i}")
            camera.cancel_tween(f"o_{x}_{i}")

        if not song_tabs[i][1].get_property("position:x") == positions[0]:
            camera.do_tween(f"x_0_{i}", song_tabs[i][1], "position:x", positions[0], 0.5, "cubic", "out")
            camera.do_tween(f"x_1_{i}", song_tabs[i][2], "position:x", positions[1], 0.5, "cubic", "out")
            camera.do_tween(f"x_2_{i}", song_tabs[i][3], "position:x", positions[1], 0.5, "cubic", "out")

            for x in range(3): camera.do_tween(f"o_{x}_{i}", song_tabs[i][x+1], "opacity", opacity, 0.25)