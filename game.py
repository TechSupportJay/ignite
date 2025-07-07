import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE | pygame.HWSURFACE)
pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

pygame.display.set_caption("Ignite")

clock = pygame.time.Clock()
fps_cap = 0

# Variables

### System Variables

note_count = 4

pressed = []
is_sus = []

for i in range(note_count):
    pressed.append(False)
    is_sus.append([False,0])

def pygame_get_key(key):
    try:
        return getattr(pygame.locals, "K_" + key)
    except:
        return getattr(pygame.locals, "K_" + key.upper())

### User Variables

current_profile = "Profile1"
profile_options = json.load(open(f"Data/{current_profile}/options.json"))

songs_dir = f"{profile_options["Customisation"]["content_folder"]}/Songs"
skin_dir = f"{profile_options["Customisation"]["content_folder"]}/Skins/{profile_options["Customisation"]["skin"]}"
grab_dir = f"{skin_dir}/Notes_{note_count}K"

note_speed = profile_options["Gameplay"]["scroll_time"]
hit_window = profile_options["Gameplay"]["timings"]["hit_window"]

### Game Variables

binds = []
for bind in profile_options["Binds"][str(note_count)]:
    binds.append(pygame_get_key(bind))

player_stats = {
    "score": 0,
    "combo": 0,
    "misses": 0,
    "accuracy": 0.0,
    "rank": "s+"
}

perf_score = 0

### Instance Variables

song_name = "beancore"
song_difficulty = "hard"

chart_raw = json.load(open(f"{songs_dir}/{song_name}/charts/{song_difficulty}.json"))
chart_notes = chart_raw["notes"]

chart_len = 0
processed_notes = 0

chart = []
for i in range(note_count): chart.append([])

for sec in chart_notes:
    if not "l" in sec.keys(): sec["l"] = 0.0
    chart[sec["p"]-1].append(sec)
    chart_len += 1

for i in range(note_count): chart.append([])

##### Sort

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

def add_script(tag, path):
    global user_scripts

    to_exec = f"class user_script_{tag}(user_script_class_template):\n"
    for line in open((path), "r").readlines():
        to_exec += f"    {line}"
    exec(f"{to_exec}\nsong_script_{tag} = user_script_{tag}()\nuser_scripts.append(song_script_{tag})")

    print(f"[i] Added Script: {tag}")

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

    if os.path.isfile(f"{songs_dir}/{song_name}/script.py"): add_script("song", f"{songs_dir}/{song_name}/script.py")
    if len(os.listdir(f"{profile_options["Customisation"]["content_folder"]}/Scripts")) > 0:
        for script in os.listdir(f"{profile_options["Customisation"]["content_folder"]}/Scripts"): add_script(f"scr_{script.replace(".py", "")}", f"{profile_options["Customisation"]["content_folder"]}/Scripts/{script}")
    if os.path.isdir((f"{skin_dir}/Scripts")):
        if len(os.listdir(f"{skin_dir}/Scripts")) > 0:
            for script in os.listdir(f"{skin_dir}/Scripts"): add_script(f"skn_{script.replace(".py", "")}", f"{skin_dir}/Scripts/{script}")
    
    if mid_song: invoke_script_function("create")

load_scripts(False)

def set_global(prop, val):
    globals()[prop] = val

# Conductor

bpm = chart_raw["meta"]["BPM"]

step_time = ((60.0 / bpm) / 4.0)

cur_step = 0
cur_beat = 0

cur_time = 0.0
start_time = time.time_ns() + ((step_time*16) * 1000 * 1000000)
next_step = 0.0

# Generate UI

scene = RMS.scenes.scene(screen, "Game")
camera = RMS.cameras.camera("HUD", 1)
scene.add_camera(camera)

camera.set_property("zoom", [1.1, 1.1])

camera.do_tween("cam_bump_x", camera, "zoom:x", 1.0, 1, "quad", "out")
camera.do_tween("cam_bump_y", camera, "zoom:y", 1.0, 1, "quad", "out")

# Background

background = RMS.objects.image("background", f"{skin_dir}/background.png")
background.set_property("size", [1280,720])
background.set_property("position", [1280/2,720/2])
if os.path.isfile(f"songs_dir/{song_name}/background.png"): background.set_property("image_location", (f"songs_dir/{song_name}/background.png"))
camera.add_item(background)

background.set_property("opacity", 0)
camera.do_tween("background_fade", background, "opacity", 255, 1, "cubic", "out")

### Cache

for i in range(4): camera.cache_image_bulk([
    f"{grab_dir}/strum_{i+1}.png",
    f"{grab_dir}/regular_{i+1}.png",
    f"{grab_dir}/confirm_{i+1}.png"
])
    
for rat in ["perf", "okay", "bad", "miss"]: camera.cache_image(f"{skin_dir}/Ratings/{rat}.png") 

#

skin_hud = json.load(open(f"{skin_dir}/hud.json"))
skin_texts = json.load(open(f"{skin_dir}/texts.json"))

### Notes

strum_origin = skin_hud["strumline"]["origin"]
strum_seperation = skin_hud["strumline"]["spacing"]

note_size = skin_hud["strumline"]["size"]
sus_size = skin_hud["sustain"]["width"]
tip_size = skin_hud["sustain"]["tip"]

# Note Background

note_bg = RMS.objects.rectangle("note_bg", "#000000")
note_bg.set_property("opacity", int(profile_options["Gameplay"]["back_trans"] * 255))
note_bg.set_property("size", [(note_size * (note_count) + (strum_seperation * (note_count-1))), 720])
note_bg.set_property("position", [1280/2,720/2])
camera.add_item(note_bg)

# Strums

for i in range(note_count):
    new_note = RMS.objects.image(f"strum_{i}", f"{grab_dir}/strum_{i+1}.png")
    new_note.set_property("size", [note_size,note_size])
    new_note.set_property("position", [strum_origin[0] + ((note_size + strum_seperation) * i), strum_origin[1]])
    camera.add_item(new_note)

    # Tweens

    new_note.set_property("position:y", strum_origin[1] + 20)
    new_note.set_property("opacity", 0)
    
    camera.do_tween(f"start_tween_y_{i}", new_note, "position:y", strum_origin[1], 0.5, "circ", "out", (0.05*i))
    camera.do_tween(f"start_tween_alpha_{i}", new_note, "opacity", 255, 0.5, "circ", "out", (0.05*i))

### User Text

i = 0
for key in skin_hud["text"].keys():
    text_obj = skin_hud["text"][key]

    new_text = RMS.objects.text(key, text_obj["text"])
    new_text.set_property("font", f"{skin_dir}/Fonts/{text_obj["font"]}")
    new_text.set_property("font_size", text_obj["size"])
    new_text.set_property("position", text_obj["position"])

    if "text_align" in text_obj.keys(): new_text.set_property("text_align", text_obj["text_align"])
    
    camera.add_item(new_text)

    # Tweens

    new_text.set_property("position:y", text_obj["position"][1] + 20)
    new_text.set_property("opacity", 0)

    camera.do_tween(f"start_tween_y_{key}", new_text, "position:y", text_obj["position"][1] - 20, 0.5, "circ", "out", (0.05*note_count)+(0.05*i))
    camera.do_tween(f"start_tween_alpha_{key}", new_text, "opacity", 255, 0.5, "circ", "out", (0.05*note_count)+(0.05*i))

    i += 1
del i

### Other

rating = RMS.objects.image("rating", f"{skin_dir}/Ratings/perf.png")
rating.set_property("position", (1280/2, 720/2))
rating.set_property("opacity", 0)
camera.add_item(rating)

# Functions

def in_range(compare, base, radius):
    return compare >= base - radius and compare <= base + radius

def show_rating(texture):
    for t in ["rating_size", "rating_size_y", "rating_opacity"]: camera.cancel_tween(t)

    rating.set_property("image_location", f"{skin_dir}/Ratings/{texture}.png")
    img_size = camera.get_image_size(f"{skin_dir}/Ratings/{texture}.png")
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

    if not down: to_grab.set_property("image_location", f"{grab_dir}/strum_{index+1}.png")

def create_note(lane):
    global chart_pointers, processed_notes

    new_note = RMS.objects.image(f"note_{lane}_{chart_pointers[lane]}", f"{grab_dir}/regular_{lane+1}.png")
    new_note.set_property("size", [note_size,note_size])
    new_note.set_property("position", [camera.get_item(f"strum_{lane}").get_property("position:x"), -note_size])
    camera.add_item(new_note)
    chart_pointers[lane] += 1
    
    processed_notes += 1

def create_sustain(lane, length):
    sus_tip = RMS.objects.image(f"tip_{lane}_{chart_pointers[lane]}", f"{grab_dir}/tip_{lane+1}.png")
    sus_tip.set_property("size", tip_size)
    sus_tip.set_property("position", [camera.get_item(f"strum_{lane}").get_property("position:x"), -note_size])
    camera.add_item(sus_tip)

    sus_length = RMS.objects.image(f"sus_{lane}_{chart_pointers[lane]}", f"{grab_dir}/sus_{lane+1}.png")
    sus_length.set_property("size:x", sus_size)
    sus_length.set_property("size:y", ((((720-(720-strum_origin[1]))) * (length / note_speed))))
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
                    camera.get_item(f"sus_{l}_{i}").set_property("size:y", (((((720-(720-strum_origin[1]))) * ((chart[l][i]["l"] - (time_in - chart[l][i]["t"])) / note_speed))) - tip_size[1]))
                    if camera.get_item(f"sus_{l}_{i}").get_property("size:y") < 0: camera.get_item(f"sus_{l}_{i}").set_property("size:y", 0)
                    camera.get_item(f"sus_{l}_{i}").set_property("position:y", camera.get_item(f"strum_{l}").get_property("position:y") - (camera.get_item(f"sus_{l}_{i}").get_property("size:y") / 2))
                else:
                    camera.get_item(f"sus_{l}_{i}").set_property("position:y", camera.get_item(f"strum_{l}").get_property("position:y") - (((720-(720-strum_origin[1])) * ((chart[l][i]["t"] - time_in)) / note_speed)) - (camera.get_item(f"sus_{l}_{i}").get_property("size:y")/2))
                camera.get_item(f"tip_{l}_{i}").set_property("position:y", camera.get_item(f"sus_{l}_{i}").get_property("position:y") - (camera.get_item(f"sus_{l}_{i}").get_property("size:y")/2) - (camera.get_item(f"tip_{l}_{i}").get_property("size:y")/2) + 2)
                if camera.get_item(f"tip_{l}_{i}").get_property("position:y") >= strum_origin[1]: camera.get_item(f"tip_{l}_{i}").set_property("opacity", 0)
            if camera.get_item(f"note_{l}_{i}") is None: continue
            camera.get_item(f"note_{l}_{i}").set_property("position:y", camera.get_item(f"strum_{l}").get_property("position:y") - ((720-(720-strum_origin[1])) * ((chart[l][i]["t"] - time_in) / note_speed)))

            if profile_options["Gameplay"]["botplay"]:
                if time_in >= chart[l][i]["t"] and not pressed[l]:
                    pressed[l] = True
                    key_handle(l, True)
                      
            if time_in > chart[l][i]["t"] and not in_range(chart[l][i]["t"], time_in, hit_window):
                if chart[l][i]["l"] > 0:
                    camera.remove_item(f"sus_{l}_{i}")
                    camera.remove_item(f"tip_{l}_{i}")
                camera.remove_item(f"note_{l}_{i}")

                perf_score += int(10000*(cur_time-(chart[l][i]["t"] + chart[l][i]["l"])))

                player_stats["misses"] += 1
                player_stats["combo"] = 0
                player_stats["score"] -= 100
                perf_score += 500

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
                    camera.get_item(f"strum_{l}").set_property("image_location", f"{grab_dir}/confirm_{lane}.png")

                    if profile_options["Audio"]["volume"]["hitsound"] > 0:
                        hitsound.play()

                    invoke_script_function("note_hit", [l, abs(time_in - chart[l][i]["t"])])

                    if profile_options["Gameplay"]["botplay"] and chart[l][i]["l"] == 0:
                        key_handle(lane-1, False)
                        pressed[lane-1] = False
                return

def process_time(difference):
    global player_stats, perf_score

    if difference <= profile_options["Gameplay"]["timings"]["perfect"]:
        show_rating("perf")
        player_stats["score"] += 500
    elif difference <= profile_options["Gameplay"]["timings"]["okay"]:
        show_rating("okay")
        player_stats["score"] += 250
    else:
        show_rating("bad")
        player_stats["score"] += 500

    player_stats["combo"] += 1
    perf_score += 500

def key_handle(index, down):
    strum_handle(index, down)
    if down:
        invoke_script_function("key_down", [index])
        process_hits(index+1, cur_time)
    else:
        invoke_script_function("key_up", [index])

def handle_current_sus(time_in, dt):
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
                    player_stats["score"] += int(10000*dt)
                    perf_score += int(10000*dt)
                else:
                    if in_range(cur_time, chart[i][pass_pointers[i]]["t"] + chart[i][pass_pointers[i]]["l"], hit_window):
                        is_sus[i] = [False,0]
                        camera.remove_item(f"sus_{i}_{pass_pointers[i]}")
                        camera.remove_item(f"tip_{i}_{pass_pointers[i]}")
                        
                        pass_pointers[i] += 1
                    else:
                        is_sus[i] = [False,0]
                        
                        camera.remove_item(f"sus_{i}_{pass_pointers[i]}")
                        camera.remove_item(f"tip_{i}_{pass_pointers[i]}")

                        player_stats["score"] -= 100
                        perf_score += int(10000*(cur_time/(chart[i][pass_pointers[i]]["t"] + chart[i][pass_pointers[i]]["l"])))

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

### Time Functions

dt = cur_time

def conduct(time_in):
    global next_step, cur_step, music_playing, dt, last_time

    dt = time_in - last_time
    last_time = time_in

    if not music_playing and time_in >= 0.0:
        pygame.mixer.music.play()
        music_playing = True
        invoke_script_function("song_start")
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

    player_stats["accuracy"] = player_stats["score"] / perf_score
    if player_stats["accuracy"] < 0: player_stats["accuracy"] = 0

    for rank in profile_options["Gameplay"]["ranks"].keys():
        r = profile_options["Gameplay"]["ranks"][rank]
        if player_stats["accuracy"] >= r:
            player_stats["rank"] = rank
            break


# Music

pygame.mixer.init()

exts = [".wav", ".ogg", ".mp3"]
song_ext = ""

for ex in exts:
    if os.path.isfile(f"{songs_dir}/{song_name}/audio{ex}"):
        song_ext = ex
        break

music_playing = False

pygame.mixer.music.load(f"{songs_dir}/{song_name}/audio{song_ext}")
pygame.mixer.music.set_volume(profile_options["Audio"]["volume"]["music"] * profile_options["Audio"]["volume"]["master"])

# SFX

hitsound = pygame.mixer.Sound(f"{skin_dir}/SFX/hitsound.ogg")
hitsound.set_volume(profile_options["Audio"]["volume"]["hitsound"] * profile_options["Audio"]["volume"]["master"])

# Main Loop

last_score = 0
last_time = time.time_ns() / 1000 / 1000000

has_created = False
continue_notes = True

while True:
    if not has_created: has_created = True; invoke_script_function("create")

    clock.tick(fps_cap)

    # Time

    cur_time = (time.time_ns() - start_time) / 1000000.0 / 1000.0 - (profile_options["Audio"]["offset"] / 1000)

    process_notes(cur_time)
    conduct(cur_time)

    if perf_score != last_score:
        last_score = perf_score
        update_accuracy()
    
    handle_current_sus(cur_time, dt)

    # UI

    update_hud_texts()

    # Script

    invoke_script_function("update", [dt])

    # Render
    
    scene.render_scene()

    # Events

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        else:
            match event.type:
                case pygame.KEYDOWN:              
                    for key in binds:
                        if pygame.key.get_pressed()[key] and not pressed[binds.index(key)] and not profile_options["Gameplay"]["botplay"]:
                            key_handle(binds.index(key), True)
                            pressed[binds.index(key)] = True
                    if not event.key in binds:
                        match event.key:
                            case pygame.K_F5: load_scripts()
                            case _: pass
                case pygame.KEYUP:
                    for key in binds:
                        if not pygame.key.get_pressed()[key] and pressed[binds.index(key)] and not profile_options["Gameplay"]["botplay"]:
                            key_handle(binds.index(key), False)
                            pressed[binds.index(key)] = False
                    if not event.key in binds:
                        match event.key:
                            case _: pass
                case pygame.VIDEORESIZE:
                    camera.set_property("scale", [event.w/1280, event.h/720])
                    camera.set_property("position", [(event.w-1280)/2,(event.h-720)/2])