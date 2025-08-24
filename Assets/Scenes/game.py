import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random
import Assets.Scenes.online.client

clock = pygame.time.Clock()
screen = None
master_data = []

# Variables

### System Variables

online_play = False

note_count = 4

pressed = []
is_sus = []

def pygame_get_key(key):
    try:
        return getattr(pygame.locals, "K_" + key)
    except:
        return getattr(pygame.locals, "K_" + key.upper())

### User Variables

current_profile = ""
profile_options = {}
controls = {}

fps_cap = 0

songs_dir = ""
skin_dir = ""

note_speed = 1
hit_window = 0.5

downscroll = True
### Game Variables

binds = []

player_stats = {
    "score": 0,
    "combo": 0,
    "misses": 0,
    "accuracy": 0.0,
    "rank": "s+",
    "ratings": {
        "perf": 0,
        "okay": 0,
        "bad": 0
    }
}

perf_score = 0

### Instance Variables

song_name = ""
song_difficulty = ""

chart_raw = []
chart_notes = []

chart_len = 0
processed_notes = 0

chart = []

song_ended = False

##### Sort

chart_unsorted = True

chart_pointers = []

pass_pointers = []

class user_script_class_template():
    def __init__(self): pass
    def create(self): pass
    def destroy(self): pass
    def update(self, dt): pass
    def step_hit(self): pass
    def beat_hit(self): pass
    def note_hit(self, lane, time_diff): pass
    def note_miss(self, lane): pass
    def song_start(self): pass
    def key_down(self, index): pass
    def key_up(self, index): pass

user_scripts = []

def add_script(prefix, tag, path):
    global user_scripts

    if tag[:1] in ["_", "#"]: return

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
            case "destroy": script.destroy()
            case "update": script.update(data[0])
            case "step": script.step_hit()
            case "beat": script.beat_hit()
            case "note_hit": script.note_hit(data[0], data[1])
            case "note_miss": script.note_miss(data[0])
            case "song_start": script.song_start()
            case "key_down": script.key_down(data[0])
            case "key_up": script.key_up(data[0]) 

def load_scripts(mid_song = True):
    print("[i] Loading Scripts...")

    if mid_song: invoke_script_function("destroy")

    global user_scripts
    user_scripts = []

    if os.path.isfile(f"{songs_dir}/{song_name}/script.py"): add_script("", "song", f"{songs_dir}/{song_name}/script.py")
    if len(os.listdir(f"{profile_options["Customisation"]["content_folder"]}/Scripts")) > 0:
        for script in os.listdir(f"{profile_options["Customisation"]["content_folder"]}/Scripts"): add_script("scr_", script.replace(".py", ""), f"{profile_options["Customisation"]["content_folder"]}/Scripts/{script}")
    if os.path.isdir((f"{skin_dir}/Scripts")):
        if len(os.listdir(f"{skin_dir}/Scripts")) > 0:
            for script in os.listdir(f"{skin_dir}/Scripts"): add_script("skn_", script.replace(".py", ""), f"{skin_dir}/Scripts/{script}")
    
    if profile_options["Customisation"]["skin"] == "default":
        if os.path.isdir((f"Assets/Game/Default/Scripts")):
            if len(os.listdir(f"Assets/Game/Default/Scripts")) > 0:
                for script in os.listdir(f"Assets/Game/Default/Scripts"): add_script("skn_", script.replace(".py", ""), f"Assets/Game/Default/Scripts/{script}")
    
    if mid_song: invoke_script_function("create")

def set_global(prop, val):
    globals()[prop] = val

# Conductor

bpm = 130

step_time = 0

cur_step = 0
cur_beat = 0

cur_time = 0.0
start_time = 99999
next_step = 0.0

# Generate UI

scene = None
camera = None

# Background

background = None

#

skin_hud = {}
skin_notes = {}
skin_texts = {}

### Notes

strum_origin = [0,0]
strum_seperation = 10

note_size = 32
sus_size = 20
tip_size = [20,10]

# Note Background

note_bg = None

### Other

rating = None

# Functions

def in_range(compare, base, radius):
    return compare >= base - radius and compare <= base + radius

def show_rating(texture):
    for t in ["rating_size", "rating_size_y", "rating_opacity"]: camera.cancel_tween(t)

    rating.set_property("image_location", skin_grab(f"Ratings/{texture}.png"))
    img_size = camera.get_image_size(skin_grab(f"Ratings/{texture}.png"))
    rating.set_property("size", img_size)
    rating.set_property("scale", [1.1,1.1])
    rating.set_property("opacity", 255)

    camera.do_tween("rating_size_x", rating, "scale:x", 1, 0.5, "back", "out")
    camera.do_tween("rating_size_y", rating, "scale:y", 1, 0.5, "back", "out")
    camera.do_tween("rating_opacity", rating, "opacity", 0, 0.5, "cubic", "in")

def strum_handle(index, down):
    to_grab = camera.get_item(f"strum_{index}")

    end_val = 1
    if down: end_val = 0.9

    camera.cancel_tween(f"strum_input_{index}_x")
    camera.cancel_tween(f"strum_input_{index}_y")

    camera.do_tween(f"strum_input_{index}_x", to_grab, "scale:x", end_val, 0.15, "back", "out")
    camera.do_tween(f"strum_input_{index}_y", to_grab, "scale:y", end_val, 0.15, "back", "out")

    if not down: to_grab.set_property("image_location", skin_grab(f"Notes/{skin_notes["notes"][str(note_count)][index]}_strum.png"))

def create_note(lane):
    global chart_pointers, processed_notes

    new_note = RMS.objects.image(f"note_{lane}_{chart_pointers[lane]}", skin_grab(f"Notes/{skin_notes["notes"][str(note_count)][lane]}_static.png"))
    new_note.set_property("size", [note_size,note_size])
    new_note.set_property("position", [camera.get_item(f"strum_{lane}").get_property("position:x"), -note_size])
    camera.add_item(new_note)
    chart_pointers[lane] += 1
    
    processed_notes += 1

def create_sustain(lane, length):
    sus_tip = RMS.objects.image(f"tip_{lane}_{chart_pointers[lane]}", skin_grab(f"Notes/{skin_notes["sustain"][str(note_count)][lane]}_tip.png"))
    sus_tip.set_property("size", tip_size)
    sus_tip.set_property("position", [camera.get_item(f"strum_{lane}").get_property("position:x"), -note_size])
    if not downscroll: sus_tip.set_property("rotation", 180)
    camera.add_item(sus_tip)

    sus_length = RMS.objects.image(f"sus_{lane}_{chart_pointers[lane]}", skin_grab(f"Notes/{skin_notes["sustain"][str(note_count)][lane]}_tail.png"))
    sus_length.set_property("size:x", sus_size)
    if downscroll: sus_length.set_property("size:y", ((((720-(720-strum_origin[1]))) * (length / note_speed))))
    else: sus_length.set_property("size:y", ((((720-strum_origin[1]))) * (length / note_speed)))
    sus_length.set_property("position:x", camera.get_item(f"strum_{lane}").get_property("position:x"))
    sus_length.set_property("position:y", -sus_length.get_property("size:y"))
    camera.add_item(sus_length)

def process_notes(time_in):
    global pass_pointers, player_stats, perf_score, continue_notes

    for l in range(note_count):
        if processed_notes >= chart_len: continue_notes = False

        processing = True
        while processing:  
            if chart_pointers[l] >= len(chart[l]):
                continue_notes = False
                break
            
            if (chart[l][chart_pointers[l]]["t"] - time_in <= note_speed*2):
                if chart[l][chart_pointers[l]]["l"] > 0: create_sustain(chart[l][chart_pointers[l]]["p"]-1, chart[l][chart_pointers[l]]["l"])
                create_note(chart[l][chart_pointers[l]]["p"]-1)
        
            if chart_pointers[l] >= len(chart[l]):
                continue_notes = False
                break

            processing = (chart[l][chart_pointers[l]]["t"] - time_in <= note_speed*2 and processed_notes < chart_len and continue_notes)
         
        for i in range(pass_pointers[l], chart_pointers[l]):
            if chart[l][i]["l"] > 0:
                if time_in > chart[l][i]["t"]:
                    if downscroll: camera.get_item(f"sus_{l}_{i}").set_property("size:y", (((((720-(720-strum_origin[1]))) * ((chart[l][i]["l"] - (time_in - chart[l][i]["t"])) / note_speed))) - tip_size[1]))
                    else: camera.get_item(f"sus_{l}_{i}").set_property("size:y", ((((((720-strum_origin[1]))) * ((chart[l][i]["l"] - (time_in - chart[l][i]["t"])) / note_speed))) - tip_size[1]))
                    
                    if camera.get_item(f"sus_{l}_{i}").get_property("size:y") < 0: camera.get_item(f"sus_{l}_{i}").set_property("size:y", 0)

                    if downscroll: camera.get_item(f"sus_{l}_{i}").set_property("position:y", camera.get_item(f"strum_{l}").get_property("position:y") - (camera.get_item(f"sus_{l}_{i}").get_property("size:y") / 2))
                    else: camera.get_item(f"sus_{l}_{i}").set_property("position:y", camera.get_item(f"strum_{l}").get_property("position:y") + (camera.get_item(f"sus_{l}_{i}").get_property("size:y") / 2))
                else:
                    if downscroll: camera.get_item(f"sus_{l}_{i}").set_property("position:y", camera.get_item(f"strum_{l}").get_property("position:y") - (((720-(720-strum_origin[1])) * ((chart[l][i]["t"] - time_in)) / note_speed)) - (camera.get_item(f"sus_{l}_{i}").get_property("size:y")/2))
                    else: camera.get_item(f"sus_{l}_{i}").set_property("position:y", camera.get_item(f"strum_{l}").get_property("position:y") + ((((720-strum_origin[1])) * ((chart[l][i]["t"] - time_in)) / note_speed)) + (camera.get_item(f"sus_{l}_{i}").get_property("size:y")/2))

                if downscroll: camera.get_item(f"tip_{l}_{i}").set_property("position:y", camera.get_item(f"sus_{l}_{i}").get_property("position:y") - (camera.get_item(f"sus_{l}_{i}").get_property("size:y")/2) - (camera.get_item(f"tip_{l}_{i}").get_property("size:y")/2) + 2)
                else: camera.get_item(f"tip_{l}_{i}").set_property("position:y", camera.get_item(f"sus_{l}_{i}").get_property("position:y") + (camera.get_item(f"sus_{l}_{i}").get_property("size:y")/2) + (camera.get_item(f"tip_{l}_{i}").get_property("size:y")/2) - 2)

                if downscroll and camera.get_item(f"tip_{l}_{i}").get_property("position:y") >= strum_origin[1]: camera.get_item(f"tip_{l}_{i}").set_property("opacity", 0)
                elif not downscroll and camera.get_item(f"tip_{l}_{i}").get_property("position:y") <= strum_origin[1]: camera.get_item(f"tip_{l}_{i}").set_property("opacity", 0)
        
                camera.get_item(f"tip_{l}_{i}").set_property("position:x", camera.get_item(f"strum_{l}").get_property("position:x"))
                camera.get_item(f"sus_{l}_{i}").set_property("position:x", camera.get_item(f"strum_{l}").get_property("position:x"))

            if camera.get_item(f"note_{l}_{i}") is None: continue

            camera.get_item(f"note_{l}_{i}").set_property("position:x", camera.get_item(f"strum_{l}").get_property("position:x"))

            if downscroll: camera.get_item(f"note_{l}_{i}").set_property("position:y", camera.get_item(f"strum_{l}").get_property("position:y") - ((720-(720-strum_origin[1])) * ((chart[l][i]["t"] - time_in) / note_speed)))
            else: camera.get_item(f"note_{l}_{i}").set_property("position:y", camera.get_item(f"strum_{l}").get_property("position:y") + (((720-strum_origin[1])) * ((chart[l][i]["t"] - time_in) / note_speed)))

            if profile_options["Gameplay"]["botplay"]:
                if time_in >= chart[l][i]["t"] and not pressed[l]:
                    pressed[l] = True
                    key_handle(l, True)
                      
            if time_in > chart[l][i]["t"] and not in_range(chart[l][i]["t"], time_in, hit_window):
                if chart[l][i]["l"] > 0:
                    camera.remove_item(f"sus_{l}_{i}")
                    camera.remove_item(f"tip_{l}_{i}")
                camera.remove_item(f"note_{l}_{i}")

                perf_score += int(10000*(time_in-(chart[l][i]["t"] + chart[l][i]["l"])))

                player_stats["misses"] += 1
                player_stats["combo"] = 0
                player_stats["score"] -= 100
                perf_score += 500

                if profile_options["Audio"]["vol_miss"] > 0: misssound.play()

                pass_pointers[l] += 1
                
                show_rating("miss")
                invoke_script_function("note_miss", [l])
                continue

def process_hits(lane, time_in):
    global pass_pointers, pressed

    for l in range(note_count):
        for i in range(pass_pointers[l], chart_pointers[l]):
            if chart[l][i]["p"] == lane:
                if in_range(chart[l][i]["t"], time_in, hit_window):
                    process_time(abs(time_in - chart[l][i]["t"]))
                    
                    if chart[l][i]["l"] == 0: pass_pointers[l] += 1
                    else: is_sus[l] = [True, chart[l][i]["t"] + chart[l][i]["l"]]

                    camera.remove_item(f"note_{l}_{i}")
                    camera.get_item(f"strum_{l}").set_property("image_location", skin_grab(f"Notes/{skin_notes["notes"][str(note_count)][l]}_confirm.png"))

                    if profile_options["Audio"]["vol_hitsound"] > 0: hitsound.play()

                    invoke_script_function("note_hit", [l, abs(time_in - chart[l][i]["t"])])

                    if profile_options["Gameplay"]["botplay"] and chart[l][i]["l"] == 0:
                        key_handle(lane-1, False)
                        pressed[lane-1] = False
                elif not profile_options["Gameplay"]["ghost_tapping"]:
                    player_stats["misses"] += 1
                    player_stats["combo"] = 0
                    player_stats["score"] -= 100
                    if profile_options["Audio"]["vol_miss"] > 0: misssound.play()
                    show_rating("miss")
                    invoke_script_function("note_miss", [l])
                return

def process_time(difference):
    global player_stats, perf_score

    if difference <= profile_options["Gameplay"]["timing_perfect"]:
        show_rating("perf")
        player_stats["score"] += 500
        player_stats["ratings"]["perf"] += 1
    elif difference <= profile_options["Gameplay"]["timing_okay"]:
        show_rating("okay")
        player_stats["score"] += 250
        player_stats["ratings"]["okay"] += 1
    else:
        show_rating("bad")
        player_stats["score"] += 100
        player_stats["ratings"]["bad"] += 1

    player_stats["combo"] += 1
    if player_stats["combo"] > player_stats["highest"]: player_stats["highest"] = player_stats["combo"]
    perf_score += 500

def key_handle(index, down):
    strum_handle(index, down)
    if down:
        invoke_script_function("key_down", [index])
        process_hits(index+1, cur_time)
    else:
        invoke_script_function("key_up", [index])

def process_sustains(time_in, dt):
    global pass_pointers, player_stats, is_sus, perf_score

    for i in range(note_count):
        if is_sus[i][0]:
            if is_sus[i][1] <= time_in:
                is_sus[i] = [False,0]
                camera.remove_item(f"sus_{i}_{pass_pointers[i]}")
                camera.remove_item(f"tip_{i}_{pass_pointers[i]}")
                
                if profile_options["Gameplay"]["botplay"]:
                    key_handle(i, False)
                    pressed[i] = False

                pass_pointers[i] += 1
            else:
                if pressed[i]:
                    player_stats["score"] += int(1000*dt)
                    perf_score += int(1000*dt)
                else:
                    if in_range(time_in, chart[i][pass_pointers[i]]["t"] + chart[i][pass_pointers[i]]["l"], hit_window):
                        is_sus[i] = [False,0]
                        camera.remove_item(f"sus_{i}_{pass_pointers[i]}")
                        camera.remove_item(f"tip_{i}_{pass_pointers[i]}")
                        
                        pass_pointers[i] += 1
                    else:
                        is_sus[i] = [False,0]
                        
                        camera.remove_item(f"sus_{i}_{pass_pointers[i]}")
                        camera.remove_item(f"tip_{i}_{pass_pointers[i]}")

                        player_stats["score"] -= 100
                        perf_score += int(1000*(time_in/(chart[i][pass_pointers[i]]["t"] + chart[i][pass_pointers[i]]["l"])))

                        pass_pointers[i] += 1
                        show_rating("miss")

                        invoke_script_function("note_miss", [i])
                    continue

# UI

def update_hud_texts():
    pairs = [["score", player_stats["score"]],
            ["misses", player_stats["misses"]],
            ["combo", player_stats["combo"]],
            ["accuracy", round(player_stats["accuracy"] * 100, 2)],
            ["rank", skin_texts["Gameplay"]["ranks"][player_stats["rank"]]]
    ]

    for pair in pairs:
        if not camera.item_exists(pair[0]): continue
        camera.get_item(pair[0]).set_property("text", skin_hud["text"][pair[0]]["text"].replace("%s", str(pair[1])))

def skin_grab(item):
    if os.path.isfile(f"{skin_dir}/{item}"): return (f"{skin_dir}/{item}")
    elif item[-4:] == ".ogg":
        for ext in exts:
            if os.path.isfile(f"{skin_dir}/{item.replace(".ogg", ext)}"): return f"{skin_dir}/{item.replace(".ogg", ext)}"
        return (f"Assets/Game/Default/{item}")
    else: return (f"Assets/Game/Default/{item}")

### Time Functions

dt = cur_time

def conduct(time_in):
    global next_step, cur_step, music_playing, dt, last_time
    global song_ended

    dt = time_in - last_time
    last_time = time_in

    if not music_playing and time_in >= 0.0:
        pygame.mixer.music.play()
        music_playing = True
        invoke_script_function("song_start")
    elif music_playing and not pygame.mixer.music.get_busy() and not song_ended:
        song_ended = True
        camera.do_tween("fadeout", camera.get_item("overlay"), "opacity", 255, 0.5)
    else:
        if time_in >= next_step:
            next_step += step_time
            cur_step += 1
            step_hit()

def step_hit():
    global cur_beat

    if cur_step % 4 == 0 or cur_step == 0:
        cur_beat += 1
        beat_hit()
    
    invoke_script_function("step")

cam_bump_mod = 4

def beat_hit():
    if cur_beat % cam_bump_mod == 0 or cur_beat == 0:
        camera.cancel_tween("cam_bump_x")
        camera.cancel_tween("cam_bump_y")

        camera.set_property("zoom", [1.025, 1.025])

        camera.do_tween("cam_bump_x", camera, "zoom:x", 1.0, 0.85, "quad", "out")
        camera.do_tween("cam_bump_y", camera, "zoom:y", 1.0, 0.85, "quad", "out")
    
    invoke_script_function("beat")

# Score

def update_accuracy():
    global player_stats

    if not perf_score == 0:
        player_stats["accuracy"] = player_stats["score"] / perf_score
        if player_stats["accuracy"] < 0: player_stats["accuracy"] = 0

    if profile_options["Gameplay"]["botplay"]: player_stats["rank"] = "bot"
    else:
        for rank in ["s+", "s", "a", "b", "c", "d", "f"]:
            r = profile_options["Gameplay"][f"rank_{rank}"]
            if player_stats["accuracy"] >= r:
                player_stats["rank"] = rank
                break
            player_stats["rank"] = "f"


# Music

pygame.mixer.init()

exts = [".wav", ".ogg", ".mp3"]
song_ext = ""

music_playing = False

# SFX

hitsound = None
misssound = None

# Pre-Loop

last_score = 0
last_time = time.time_ns() / 1000 / 1000000

has_created = False
continue_notes = True

# Initialise
def init(data):
    global song_name, song_difficulty, song_ext
    global note_count, note_speed, hit_window, pressed, is_sus, downscroll
    global note_size, strum_seperation, strum_origin, sus_size, tip_size, skin_texts, skin_hud, skin_notes
    global chart, chart_len, chart_notes, chart_pointers, pass_pointers, chart_raw, chart_unsorted, processed_notes
    global fps_cap, songs_dir, skin_dir
    global player_stats, last_score, perf_score
    global cur_time, cur_step, cur_beat, last_time, music_playing, bpm, step_time, start_time, next_step, cam_bump_mod
    global hitsound, misssound
    global camera, scene
    global background, rating, note_bg
    global user_scripts, profile_options, controls, binds, pressed
    global has_created, master_data, online_play
    global song_ended

    # Initalise Scene

    scene = RMS.scenes.scene(screen, "Game")
    camera = RMS.cameras.camera("HUD", 1)
    scene.add_camera(camera)

    camera.set_property("zoom", [1.1, 1.1])
    cam_bump_mod = 4

    camera.do_tween("cam_bump_x", camera, "zoom:x", 1.0, 1, "quad", "out")
    camera.do_tween("cam_bump_y", camera, "zoom:y", 1.0, 1, "quad", "out")

    # Variables
    ### User Variables

    user_scripts = []   

    current_profile = data[2]
    profile_options = json.load(open(f"Data/{current_profile}/options.json"))
    controls = json.load(open(f"Data/{current_profile}/controls.json"))

    fps_cap = int(profile_options["Video"]["fps_cap"])
    songs_dir = f"{profile_options["Customisation"]["content_folder"]}/Songs"

    chart_raw = json.load(open(f"{songs_dir}/{data[0]}/charts/{data[1]}.json"))
    if "lanes" in chart_raw ["meta"].keys(): note_count = chart_raw["meta"]["lanes"]
    else: note_count = 4

    skin_dir = f"{profile_options["Customisation"]["content_folder"]}/Skins/{profile_options["Customisation"]["skin"]}"

    note_speed = profile_options["Gameplay"]["scroll_time"]
    hit_window = profile_options["Gameplay"]["timing_hit_window"]

    ### System Variables

    pressed = []
    is_sus = []

    for i in range(note_count):
        pressed.append(False)
        is_sus.append([False,0])

    ### Game Variables

    downscroll = profile_options["Gameplay"]["downscroll"]

    binds = []
    for bind_set in controls[str(note_count)]:
        s = []
        for bind in bind_set: s.append(pygame_get_key(bind))
        binds.append(s)

    player_stats = {
        "score": 0,
        "combo": 0,
        "highest": 0,
        "misses": 0,
        "accuracy": 0.0,
        "rank": "s+",
        "ratings": {
            "perf": 0,
            "okay": 0,
            "bad": 0
        }
    }

    perf_score = 0
    update_accuracy()

    ### Instance Variables

    song_name = data[0]
    song_difficulty = data[1]

    chart_notes = chart_raw["notes"]

    chart_len = 0
    processed_notes = 0

    chart = []
    for i in range(note_count): chart.append([])

    for sec in chart_notes:
        if not "l" in sec.keys(): sec["l"] = 0.0
        chart[sec["p"]-1].append(sec)
        chart_len += 1

    # Sort Chart

    chart_unsorted = True
    while chart_unsorted:
        chart_unsorted = False
        for lane in chart:
            for i in range(len(lane)-1):
                if lane[i]["t"] > lane[i+1]["t"]:
                    temp = lane[i+1]
                    lane[i+1] = lane[i]
                    lane[i] = temp
                    chart_unsorted = True

    chart_pointers = []
    for i in range(note_count): chart_pointers.append(0)

    pass_pointers = []
    for i in range(note_count): pass_pointers.append(0)

    # Objects
        
    for rat in ["perf", "okay", "bad", "miss"]: camera.cache_image(skin_grab(f"Ratings/{rat}.png"))

    ### Background

    background = RMS.objects.image("background", skin_grab(f"background.png"))
    background.set_property("size", [1280,720])
    background.set_property("position", [1280/2,720/2])
    if os.path.isfile(f"{songs_dir}/{song_name}/background.png"): background.set_property("image_location", (f"{songs_dir}/{song_name}/background.png"))
    camera.add_item(background)
    background.set_property("opacity", 0)
    camera.do_tween("background_fade", background, "opacity", 255, 1, "cubic", "out")

    ### Notes
    skin_hud = json.load(open(skin_grab(f"hud.json")))
    skin_notes = json.load(open(skin_grab(f"notes.json")))

    ### Cache Images

    for note in skin_notes["notes"][str(note_count)]:
        camera.cache_image(skin_grab(f"Notes/{note}_static.png"))
        camera.cache_image(skin_grab(f"Notes/{note}_strum.png"))
        camera.cache_image(skin_grab(f"Notes/{note}_confirm.png"))

    for note in skin_notes["sustain"][str(note_count)]:
        camera.cache_image(skin_grab(f"Notes/{note}_tail.png"))
        camera.cache_image(skin_grab(f"Notes/{note}_tip.png"))

    new_orig = []

    strum_seperation = skin_hud["strumline"]["spacing"]

    note_size = skin_hud["strumline"]["size"]
    sus_size = skin_hud["sustain"]["width"]
    tip_size = skin_hud["sustain"]["tip"]

    if str(note_count) in skin_hud["strumline"]["x_origin"].keys(): new_orig.append(skin_hud["strumline"]["x_origin"][str(note_count)])
    else: new_orig.append((1280 / 2) - (((note_size * note_count) + (strum_seperation * (note_count - 1))) / 2) + (note_size/2))

    if downscroll: new_orig.append(skin_hud["strumline"]["y_origin"]["down"])
    else: new_orig.append(skin_hud["strumline"]["y_origin"]["up"])

    strum_origin = new_orig

    ### Note Background

    note_bg = RMS.objects.rectangle("note_bg", "#000000")
    note_bg.set_property("opacity", int(profile_options["Gameplay"]["back_trans"] * 255))
    note_bg.set_property("size", [(note_size * (note_count) + (strum_seperation * (note_count-1))) + 25, 720])
    note_bg.set_property("position", [1280/2,720/2])
    camera.add_item(note_bg)

    ### Strums

    for i in range(note_count):
        new_note = RMS.objects.image(f"strum_{i}", skin_grab(f"Notes/{skin_notes["notes"][str(note_count)][i]}_strum.png"))
        new_note.set_property("size", [note_size,note_size])
        new_note.set_property("position", [strum_origin[0] + ((note_size + strum_seperation) * i), strum_origin[1]])
        camera.add_item(new_note)

        # Tweens

        new_note.set_property("position:y", strum_origin[1] + 20)
        new_note.set_property("opacity", 0)
        
        camera.do_tween(f"start_tween_y_{i}", new_note, "position:y", strum_origin[1], 0.5, "circ", "out", (0.05*i))
        camera.do_tween(f"start_tween_alpha_{i}", new_note, "opacity", 255, 0.5, "circ", "out", (0.05*i))

    ### Rating
    
    rating = RMS.objects.image("rating", skin_grab(f"Ratings/perf.png"))
    rating.set_property("position", (1280/2, 720/2))
    rating.set_property("opacity", 0)
    camera.add_item(rating)

    # Skin Management
    skin_texts = json.load(open(skin_grab(f"texts.json")))

    i = 0
    for key in skin_hud["text"].keys():
        text_obj = skin_hud["text"][key]

        new_text = RMS.objects.text(key, text_obj["text"])
        new_text.set_property("font", skin_grab(f"Fonts/{text_obj["font"]}"))
        new_text.set_property("font_size", text_obj["size"])
        new_text.set_property("position", text_obj["position"])

        if "text_align" in text_obj.keys(): new_text.set_property("text_align", text_obj["text_align"])
        
        camera.add_item(new_text)

        ### Tweens

        new_text.set_property("position:y", text_obj["position"][1] + 20)
        new_text.set_property("opacity", 0)

        camera.do_tween(f"start_tween_y_{key}", new_text, "position:y", text_obj["position"][1] - 20, 0.5, "circ", "out", (0.05*note_count)+(0.05*i))
        camera.do_tween(f"start_tween_alpha_{key}", new_text, "opacity", 255, 0.5, "circ", "out", (0.05*note_count)+(0.05*i))

        i += 1
    del i

    # Time

    bpm = chart_raw["meta"]["BPM"]
    step_time = ((60.0 / bpm) / 4.0)
    start_time = time.time_ns() + ((step_time*16) * 1000 * 1000000)
    cur_step = 0
    cur_beat = 0
    cur_time = 0.0
    next_step = 0.0

    # Music
    
    music_playing = False

    for ex in exts:
        if os.path.isfile(f"{songs_dir}/{song_name}/audio{ex}"):
            song_ext = ex
            break
    
    pygame.mixer.music.load(f"{songs_dir}/{song_name}/audio{song_ext}")
    pygame.mixer.music.set_volume(profile_options["Audio"]["vol_music"] * profile_options["Audio"]["vol_master"])

    # Hitsounds

    hitsound = pygame.mixer.Sound(skin_grab(f"SFX/hitsound.ogg"))
    hitsound.set_volume(profile_options["Audio"]["vol_hitsound"] * profile_options["Audio"]["vol_master"])

    misssound = pygame.mixer.Sound(skin_grab(f"SFX/miss.ogg"))
    misssound.set_volume(profile_options["Audio"]["vol_miss"] * profile_options["Audio"]["vol_master"])

    # Online

    if data[3] == False: online_play = False
    else:
        Assets.Scenes.online.client.reset()
        online_play = True
        Assets.Scenes.online.client.host_ip = data[3][1]
        Assets.Scenes.online.client.host_port = data[3][2]

    # Exit Fade
    overlay = RMS.objects.rectangle("overlay", "#000000")
    overlay.set_property("size", [1280,720])
    overlay.set_property("position", [1280/2,720/2])
    overlay.set_property("priority", 100)
    overlay.set_property("opacity", 0)
    camera.add_item(overlay)

    song_ended = False

    # Finish

    load_scripts(False)
    has_created = False
    master_data = []

# Loop

def update():
    global has_created, cur_time, last_score, pressed

    # Process Binds
    cur_pressed = pressed.copy()
    for i in range(note_count):
        key_pressed = False
        for x in range(len(binds)):
            if pygame.key.get_pressed()[binds[x][i]]:
                key_pressed = True
                break
        if key_pressed and not pressed[i] and not profile_options["Gameplay"]["botplay"]:
            key_handle(i, True)
            pressed[i] = True
            cur_pressed[i] = True
        if not key_pressed and pressed[i] and cur_pressed[i] and not profile_options["Gameplay"]["botplay"]:
            key_handle(i, False)
            pressed[i] = False
            cur_pressed[i] = False

    if not has_created: has_created = True; invoke_script_function("create")

    # Time
    clock.tick(fps_cap)

    cur_time = ((time.time_ns() - start_time) / 1000000.0 / 1000.0)

    process_notes(cur_time - (profile_options["Audio"]["offset"] / 1000))
    conduct(cur_time)

    if perf_score != last_score:
        last_score = perf_score
        update_accuracy()
    
    process_sustains(cur_time - (profile_options["Audio"]["offset"] / 1000), dt)

    # UI
    update_hud_texts()

    # Script
    invoke_script_function("update", [dt])

    # End Fade
    if song_ended:
        if camera.get_item("overlay").get_property("opacity") == 255:
            master_data.append(["switch_scene", "results", {
                "meta": json.load(open(f"{profile_options["Customisation"]["content_folder"]}/Songs/{song_name}/meta.json")),
                "score": player_stats["score"],
                "accuracy": player_stats["accuracy"],
                "highest": player_stats["highest"],
                "ratings": player_stats["ratings"],
                "misses": player_stats["misses"],
                "rank": player_stats["rank"],
                "folder": song_name,
                "difficulty": song_difficulty
            }])

    # Render
    scene.render_scene()

def handle_event(event):
    match event.type:
        case pygame.KEYDOWN:  
            if not event.key in binds:
                match event.key:
                    case pygame.K_F5: load_scripts()
                    case pygame.K_ESCAPE:
                        master_data.append(["switch_scene", "results", {
                            "meta": json.load(open(f"{profile_options["Customisation"]["content_folder"]}/Songs/{song_name}/meta.json")),
                            "score": player_stats["score"],
                            "accuracy": player_stats["accuracy"],
                            "highest": player_stats["highest"],
                            "ratings": player_stats["ratings"],
                            "misses": player_stats["misses"],
                            "rank": player_stats["rank"],
                            "folder": song_name,
                            "difficulty": song_difficulty
                        }])
                    case _: pass
        case pygame.KEYUP:
            if not event.key in binds:
                match event.key:
                    case _: pass
def destroy():
    global camera, scene, user_scripts

    for script in user_scripts: script.destroy()
    user_scripts = []
    del camera, scene

    pygame.mixer_music.stop()

def resize(size):
    for cam in scene.cameras.keys():
        scene.cameras[cam].set_property("scale", [size[0]/1280,size[1]/720])
        scene.cameras[cam].set_property("position", [(size[0]-1280)/2,(size[1]-720)/2])