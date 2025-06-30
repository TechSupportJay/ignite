import RMS.easing, RMS.scenes, RMS.cameras, RMS.objects
import pygame, math, time, json

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

pygame.display.set_caption("Ignite")

clock = pygame.time.Clock()
fps_cap = 0

# Variables

### System Variables

note_count = 4
grab_dir = f"Assets/Game/Notes_{note_count}K"
songs_dir = "Content/Songs"

pressed = []
for i in range(note_count): pressed.append(False)

### User Variables

note_speed = 0.5
hit_window = 0.1

### Game Variables

binds = [pygame.K_d,pygame.K_f,pygame.K_j,pygame.K_k]

cur_time = 0.0
start_time = time.time_ns()

### Instance Variables

song_name = "radar"
song_difficulty = "hard"

chart_raw = json.load(open(f"{songs_dir}/{song_name}/charts/{song_difficulty}.json"))["notes"]

chart = []
for i in range(note_count): chart.append([])

for combo in chart_raw: chart[combo["p"]-1].append(combo)


chart_pointers = []
for i in range(note_count): chart_pointers.append(0)

pass_pointers = []
for i in range(note_count): pass_pointers.append(0)

# Generate UI

scene = RMS.scenes.scene(screen, "Game")
camera = RMS.cameras.camera("HUD", 1)
scene.add_camera(camera)

### Notes

strum_origin = [100,720-30-84]
strum_seperation = 10
note_size = 84

for i in range(4):
    ### Strum
    new_note = RMS.objects.image(f"strum_{i}", f"{grab_dir}/strum_{i+1}.png")
    new_note.set_property("size", [note_size,note_size])
    new_note.set_property("position", [strum_origin[0] + ((note_size + strum_seperation) * i), strum_origin[1]])
    camera.add_item(new_note)

# Functions

def in_range(compare, base, radius):
    return compare >= base - radius and compare <= base + radius

def strum_handle(index, down):
    to_grab = camera.get_item(f"strum_{index}")

    end_val = 1
    if down: end_val = 0.9

    end_val *= note_size

    camera.cancel_tween(f"strum_input_{index}_x")
    camera.cancel_tween(f"strum_input_{index}_y")

    camera.do_tween(f"strum_input_{index}_x", to_grab, "size:x", end_val, 0.15, "circ", "out")
    camera.do_tween(f"strum_input_{index}_y", to_grab, "size:y", end_val, 0.15, "circ", "out")

def create_note(lane):
    global chart_pointers

    new_note = RMS.objects.image(f"note_{lane}_{chart_pointers[lane]}", f"{grab_dir}/regular_{lane+1}.png")
    new_note.set_property("size", [note_size,note_size])
    new_note.set_property("position", [strum_origin[0] + ((note_size + strum_seperation) * lane), -note_size])
    camera.add_item(new_note)
    chart_pointers[lane] += 1

def process_notes(time_in):
    global pass_pointers

    for l in range(4):
        if chart[l][chart_pointers[l]]["t"] - time_in <= note_speed*2:
            create_note(chart[l][chart_pointers[l]]["p"]-1)
        
        for i in range(pass_pointers[l], chart_pointers[l]):
            if camera.get_item(f"note_{l}_{i}") is None: continue
            camera.get_item(f"note_{l}_{i}").set_property("position:y", strum_origin[1] - ((720-(720-strum_origin[1])) * ((chart[l][i]["t"] - time_in) / note_speed)))

            if time_in > chart[l][i]["t"] and not in_range(chart[l][i]["t"], time_in, hit_window):
                pass_pointers[l] += 1
                camera.remove_item(f"note_{l}_{i}")
                continue

def process_hits(lane, time_in):
    global pass_pointers

    for l in range(4):
        for i in range(pass_pointers[l], chart_pointers[l]):
            if chart[l][i]["p"] == lane:
                if in_range(chart[l][i]["t"], time_in, hit_window):
                    pass_pointers[l] += 1
                    camera.remove_item(f"note_{l}_{i}")
                return

def key_handle(index, down):
    strum_handle(index, down)
    if down: process_hits(index+1, cur_time)

# Music

pygame.mixer.init()
pygame.mixer.music.load(f"{songs_dir}/{song_name}/audio.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play()

# Main Loop

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        else:
            match event.type:
                case pygame.KEYDOWN:              
                    for key in binds:
                        if pygame.key.get_pressed()[key] and not pressed[binds.index(key)]:
                            key_handle(binds.index(key), True)
                            pressed[binds.index(key)] = True
                    if not event.key in binds:
                        match event.key:
                            case _: pass
                case pygame.KEYUP:
                    for key in binds:
                        if not pygame.key.get_pressed()[key] and pressed[binds.index(key)]:
                            key_handle(binds.index(key), False)
                            pressed[binds.index(key)] = False
                    if not event.key in binds:
                        match event.key:
                            case _: pass

    # Time

    cur_time = (time.time_ns() - start_time) / 1000000 / 1000

    process_notes(cur_time)

    # Render
    
    scene.render_scene()