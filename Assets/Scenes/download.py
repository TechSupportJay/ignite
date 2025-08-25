import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random
import socket, threading

screen = None
master_data = []

# Variables

screen = None
scene = None
camera = None

current_profile = {}
skin_dir = ""

#

profile_options = {}
ui = {}
ui_texts = {}
menu_sfx = {}

#

header = 0
ip = None
port = 0
server = None
client = None

thread = None

#

connected = False
currently_downloading = ""
download = {}
charts = []
ext = ""
requested = ""
request_fulfilled = False
last_ping = 0

#

songs = []
selection_id = 0

# Master Functions

def init(data = []):
    global scene, camera
    global current_profile, profile_options, skin_dir
    global header, ip, port, server, identifiers, thread, connected, client
    global currently_downloading, download, requested, charts, ext, request_fulfilled, last_ping
    global ui, ui_texts
    global songs
    global menu_sfx

    scene = RMS.scenes.scene(screen, "Template")
    camera = RMS.cameras.camera("HUD", 1)
    scene.add_camera(camera)

    #

    current_profile = data[0]
    profile_options = json.load(open(f"Data/{data[0]}/options.json"))
    skin_dir = f"{profile_options["Customisation"]["content_folder"]}/Skins/{profile_options["Customisation"]["skin"]}"
    ui = json.load(open(skin_grab("Menus/Download/ui.json")))
    ui_texts = grab_json("texts.json", "Song Selection")

    # Online

    network_options = json.load(open(f"Data/{data[0]}/network.json"))

    header = 64
    ip = network_options["ip"]
    port = network_options["port"]
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

    thread = None
    connected = False

    ### Connection

    connected = False

    try:
        connect(ip, port)
        connected = True
    except:
        connected = False
    
    menu_sfx = {}
    sfx = ["scroll", "select", "play", "back"]
    for s in sfx:
        menu_sfx[s] = pygame.mixer.Sound(skin_grab(f"SFX/Menu/{s}.ogg"))
        menu_sfx[s].set_volume(profile_options["Audio"]["vol_sfx"] * profile_options["Audio"]["vol_master"])
    
    if connected:
        # Load UI
        background = RMS.objects.image("background", skin_grab(f"Menus/Download/background.png"))
        background.set_property("size", [1280,720])
        background.set_property("position", [1280/2,720/2])
        camera.add_item(background)

        camera.cache_image(skin_grab(f"Menus/Download/download_background.png"))
        download_background = RMS.objects.image("download_background", skin_grab(f"Menus/Download/download_background.png"))
        download_background.set_property("size", [1280,720])
        download_background.set_property("position", [1280/2,720/2])
        download_background.set_property("visible", False)
        download_background.set_property("priority", 99)
        camera.add_item(download_background)

        download_title = RMS.objects.text("download_title", "Song Name")
        download_title.set_property("font", skin_grab("Fonts/default.ttf"))
        download_title.set_property("font_size", 48)
        download_title.set_property("text_align", "center")
        download_title.set_property("position", [1280/2,720/2-60])
        download_title.set_property("priority", 100)
        download_title.set_property("visible", False)
        camera.add_item(download_title)

        download_progress = RMS.objects.text("download_progress", "Downloading Song...")
        download_progress.set_property("font", skin_grab("Fonts/sub.ttf"))
        download_progress.set_property("font_size", 32)
        download_progress.set_property("text_align", "center")
        download_progress.set_property("position", [1280/2,720/2+10])
        download_progress.set_property("priority", 100)
        download_progress.set_property("visible", False)
        camera.add_item(download_progress)

        ###

        ### Song Info Text
        texts = ["BPM", "Chartist"]
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

        #

        currently_downloading = ""
        download = {}
        requested = ""
        charts = []
        ext = ""
        request_fulfilled = False
        last_ping = time.time() + 10

        ###

        camera.cache_image(skin_grab(f"Menus/Download/tab.png"))
        camera.cache_image(skin_grab(f"Menus/Download/tab_owned.png"))
        songs = []
        send("sql", "SELECT * FROM songs")

        #

        thread = threading.Thread(target=client_update)
        thread.start()
    else:
        fancy_print("Unable to Connect", "Download Songs / Socket", "!")
        error = RMS.objects.image("error", skin_grab(f"Menus/Download/error.png"))
        error.set_property("size", [1280,720])
        error.set_property("position", [1280/2,720/2])
        error.set_property("visible", True)
        error.set_property("priority", 99)
        camera.add_item(error)

def client_update():
    global connected, currently_downloading, download, requested, charts, ext, request_fulfilled

    while connected:
        # Check for UTF-8
        pre = client.recv(2560000)
        if not pre: continue

        utf8 = False
        try:
            message = pre.decode("utf-8")
            utf8 = True
        except:
            message = pre

        if utf8:
            if not " || " in message: continue

            fancy_print(message, "Server", ">")

            message = message.split(" || ")
            match message[0]:
                case "sql":
                    load_songs(message[1])
                case "msg":
                    fancy_print(message, "Message from Server", ">")
                case "dl_fin":
                    if currently_downloading != "":
                        split = message[1].split(" | ")
                        if not "content" in download[split[0]]:
                            request_fulfilled = True
                            continue_download(split[0])
                        else:
                            if not download[split[0]]["finished"]:
                                if len(download[split[0]]["content"]) < int(split[1]):
                                    fancy_print(f"{split[0]} states it has finished downloading\nbut size does not match\n({len(download[split[0]]["content"])} < {split[1]})", f"Download: {currently_downloading}", "D")
                                    request_fulfilled = True
                                    continue_download(split[0])
                                else:
                                    fancy_print(f"{split[0]} has finished downloading", f"Download: {currently_downloading}", "D")
                                    download[split[0]]["finished"] = True
                                    request_fulfilled = True
                                    continue_download(split[0])
                case "dl_text":
                    if currently_downloading != "":
                        if not "content" in download[requested].keys(): download[requested]["content"] = message[1]
                        else: download[requested]["content"] += message[1]
                        
                        fancy_print(f"Recieved {len(message[1])/1000}KB of {requested}", f"Download: {currently_downloading}", "D")
                        request_fulfilled = True

                        continue_download(requested)
                case "charts":
                    charts = message[1].split("|")
                    request_fulfilled = True

                    send("download", f"get_audio_ext|{currently_downloading}")                    
                case "ext":
                    fancy_print(f"Audio Extension: {message[1]}", f"Server", "D")
                    ext = message[1]
                    request_fulfilled = True

                    continue_download("audio")
        else:
            if currently_downloading != "":
                if not "content" in download[requested].keys(): download[requested]["content"] = message
                else: download[requested]["content"] += message
                fancy_print(f"Recieved {len(message)/1000}KB of {requested} (RAW)", f"Download: {currently_downloading}", "D")

                time.sleep(0.05)

                request_fulfilled = True
                continue_download(requested)

def update():
    scene.render_scene()

def handle_event(event):
    global connected, thread, selection_id

    match event.type:
        case pygame.KEYDOWN:
            if camera.has_item("error"):
                connected = False
                thread = None
                send("sys", "disconnect")
                master_data.append(["switch_scene", "menu", [False, "content"]])
            else:
                match event.key:
                    case pygame.K_ESCAPE:
                        connected = False
                        thread = None
                        send("sys", "disconnect")
                        master_data.append(["switch_scene", "menu", [False, "content"]])
                    case pygame.K_UP:
                        if len(songs) > 0 and currently_downloading == "":
                            selection_id -= 1
                            if selection_id < 0: selection_id = len(songs)-1
                            select_song(selection_id)
                            menu_sfx["scroll"].stop()
                            menu_sfx["scroll"].play()
                    case pygame.K_DOWN:
                        if len(songs) > 0 and currently_downloading == "":
                            selection_id += 1
                            if selection_id > len(songs)-1: selection_id = 0
                            select_song(selection_id)
                            menu_sfx["scroll"].stop()
                            menu_sfx["scroll"].play()
                    case pygame.K_RETURN:
                        if len(songs) > 0 and currently_downloading == "":
                            if os.path.exists(f"{profile_options["Customisation"]["content_folder"]}/Songs/{songs[selection_id][0]}"):
                                master_data.append(["switch_scene", "song_selection"])
                            else:
                                menu_sfx["select"].stop()
                                menu_sfx["select"].play()
                                download_chart(songs[selection_id][0])
                    case _: pass
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

def get_text(key, sub = ""):
    sub = str(sub)
    if not key in ui_texts.keys(): return sub
    else: return ui_texts[key].replace("%s", sub)

def get_ui_property(parent, key, otherwise):
    if not parent in ui.keys(): return otherwise
    if not key in ui[parent].keys(): return otherwise
    else: return ui[parent][key]

def grab_json(name, key):
    path = f"{skin_dir}/{name}"
    dict = {}

    if not os.path.isfile(f"{skin_dir}/{name}"): path = (f"Assets/Game/Default/{name}")

    dict = json.load(open(path))
    if key not in dict.keys():
        dict = json.load(open((f"Assets/Game/Default/{name}")))
    
    return dict[key]

#

def connect(ip, port):
    global connected, thread
    
    try:
        client.connect((ip, port))
        return True
    except:
        menu_sfx["back"].play()
        fancy_print("Unable to Connect", "Download Songs / Socket", "!")
        error = RMS.objects.image("error", skin_grab(f"Menus/Download/error.png"))
        error.set_property("size", [1280,720])
        error.set_property("position", [1280/2,720/2])
        error.set_property("priority", 99)
        camera.add_item(error)
        return False

def disconnect():
    send("sys", "disconnect")
    exit()

def send(type, content = ""):
    global connected

    try:
        message = f"{type};{content}"
        message = message.encode("utf-8")
        message_len = len(message)
        send_len = str(message_len).encode("utf-8")
        send_len += b' ' * (header - len(send_len))
        
        client.send(send_len)
        client.send(message)
    except:
        connected = False

#

def load_songs(output):
    global selection_id
    
    output_list = []
    output_list_0 = output.split("|")
    for list in output_list_0:
        output_list_1 = list.split(",")
        output_list.append(output_list_1)

    for song in output_list:
        make_song_tab(song[0], song[1], song[2], song[3], song[4])
    
    selection_id = 0
    select_song(selection_id)

def make_song_tab(id, display_name, artist, chartist, bpm):
    tab_texture = "tab"
    if os.path.exists(f"{profile_options["Customisation"]["content_folder"]}/Songs/{id}"): tab_texture = "tab_owned"

    tab_bg = RMS.objects.image(f"tab_{id}", skin_grab(f"Menus/Download/{tab_texture}.png"))
    tab_bg.set_property("size", camera.get_image_size(skin_grab(f"Menus/Download/{tab_texture}.png")))

    tab_bg.set_property("position:x", ui["tab_bg"]["position"][0]+(camera.get_image_size(skin_grab(f"Menus/Download/{tab_texture}.png"))[0]/2))
    tab_bg.set_property("position:y", ui["tab_bg"]["position"][1]+((camera.get_image_size(skin_grab(f"Menus/Download/{tab_texture}.png"))[1]+ui["tab_bg"]["seperation"])*len(songs)))
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

    songs.append([id, tab_bg, tab_name, tab_artist, chartist, bpm])

def select_song(id):
    move_vertical = 0

    selection_pos_down = songs[id][1].get_property("position:y") + (songs[id][1].get_property("size:y") / 2)
    selection_pos_up = songs[id][1].get_property("position:y") - (songs[id][1].get_property("size:y") / 2)

    if selection_pos_down > 720: move_vertical = selection_pos_down - 720 + 20
    elif selection_pos_up < 0: move_vertical = (selection_pos_up - (ui["tab_bg"]["position"][1]))

    # Change Tabs
    for i in range(len(songs)):
        positon_relative = 0
        opacity = 255/2

        if i == id:
            positon_relative = ui["tab_bg"]["selection"]
            opacity = 255

        positions = [
            ui["tab_bg"]["position"][0]+(camera.get_image_size(skin_grab(f"Menus/Download/tab.png"))[0]/2)+positon_relative,
            (camera.get_image_size(skin_grab(f"Menus/Download/tab.png"))[0]/2)
        ]

        for x in range(3):
            camera.cancel_tween(f"x_{x}_{i}")
            camera.cancel_tween(f"o_{x}_{i}")

        if not songs[i][1].get_property("position:x") == positions[0]:
            camera.do_tween(f"x_0_{i}", songs[i][1], "position:x", positions[0], 0.5, "cubic", "out")
            camera.do_tween(f"x_1_{i}", songs[i][2], "position:x", positions[0]-positions[1]+ui["tab_name"]["position"][0], 0.5, "cubic", "out")
            camera.do_tween(f"x_2_{i}", songs[i][3], "position:x", positions[0]-positions[1]+ui["tab_artist"]["position"][0], 0.5, "cubic", "out")

        for x in range(3): camera.do_tween(f"o_{x}_{i}", songs[i][x+1], "opacity", opacity, 0.25)
        
        if move_vertical != 0:
            for x in range(1,4): camera.cancel_tween(f"y_{x}_{i}")
            for x in range(1,4): camera.do_tween(f"y_{x}_{i}", songs[i][x], "position:y", songs[i][x].get_property("position:y") - move_vertical, 0.5, "cubic", "out")

    # Modify Info

    ### Texts
    bpm = camera.get_item("bpm")
    chartist = camera.get_item("chartist")

    bpm.set_property("text", get_text("bpm", songs[id][5]))
    chartist.set_property("text", get_text("chartist", songs[id][4]))

    # Tween Info
    ### Album

    texts = ["bpm", "chartist"]
    i = 1
    for t in texts:
        camera.cancel_tween(f"{t}_x")
        x = camera.get_item(t)
        x.set_property("position:x", ui["info_texts"]["position"][0] + 10)
        camera.do_tween(f"{t}_x", x, "position:x", ui["info_texts"]["position"][0], 0.5, "cubic", "out", 0.015*(i-1))
        i += i
    del i

#

def download_chart(id):
    global currently_downloading, download, requested
    
    currently_downloading = id

    # Make Directories
    if not os.path.exists(f"{profile_options["Customisation"]["content_folder"]}/Songs/{id}"):
        os.mkdir(f"{profile_options["Customisation"]["content_folder"]}/Songs/{id}")
        os.mkdir(f"{profile_options["Customisation"]["content_folder"]}/Songs/{id}/charts")
    
    # Start Download
    download = {
        "meta": {"finished": False},
        "audio": {"finished": False}
    }

    # Show Overlay
    camera.get_item("download_background").set_property("visible", True)
    camera.get_item("download_title").set_property("visible", True)
    camera.get_item("download_progress").set_property("visible", True)

    camera.get_item("download_title").set_property("text", songs[selection_id][2].get_property("text"))
    camera.get_item("download_progress").set_property("text", "Starting Download...")

    camera.cancel_tween("zoom_x")
    camera.cancel_tween("zoom_y")

    camera.set_property("zoom", [1.2,1.2])
    camera.do_tween("zoom_x", camera, "zoom:x", 1, 5, "cubic", "out")
    camera.do_tween("zoom_y", camera, "zoom:y", 1, 5, "cubic", "out")

    songs[selection_id][1].set_property("image_location", skin_grab(f"Menus/Download/tab_owned.png"))

    send("download", f"get_charts|{currently_downloading}")
    
def continue_download(current):
    global requested, ext, request_fulfilled, currently_downloading

    if not request_fulfilled: return
    request_fulfilled = False

    if current not in download:
        download[current] = {
            "finished": False,
            "content": ""
        }
    
    if download[current]["finished"]:
        write_file(current)
        match current:
            case "meta": current = charts[0]
            case "audio": current = "meta"
            case _: 
                if current in charts:
                    current_index = charts.index(current)+1
                    if current_index >= len(charts):
                        fancy_print(f"Download has completed", f"Download: {currently_downloading}", "D")
                        camera.get_item("download_background").set_property("visible", False)
                        camera.get_item("download_title").set_property("visible", False)
                        camera.get_item("download_progress").set_property("visible", False)

                        camera.cancel_tween("zoom_x")
                        camera.cancel_tween("zoom_y")

                        camera.set_property("zoom", [1.2,1.2])
                        camera.do_tween("zoom_x", camera, "zoom:x", 1, 0.5, "cubic", "out")
                        camera.do_tween("zoom_y", camera, "zoom:y", 1, 0.5, "cubic", "out")

                        currently_downloading = ""
                        menu_sfx["play"].play()
                        return
                    else:
                        current = charts[current_index]
                        camera.get_item("download_progress").set_property("text", f"Downloading Chart {current_index+1}/{len(charts)}...")
    else:
        match current:
            case "audio": camera.get_item("download_progress").set_property("text", f"Downloading Audio...")
            case "meta": camera.get_item("download_progress").set_property("text", f"Downloading Meta...")

    requested = current

    camera.get_item("download_progress").set_property("scale", [1.1,1.1])
    camera.cancel_tween("progress_bump_x")
    camera.cancel_tween("progress_bump_y")
    camera.do_tween("progress_bump_x", camera.get_item("download_progress"), "scale:x", 1, 0.5, "back", "out")
    camera.do_tween("progress_bump_y", camera.get_item("download_progress"), "scale:y", 1, 0.5, "back", "out")

    if not current in download: download[current] = {"finished": False}
    if current != "" and not download[current]["finished"]:
        send("download", f"{currently_downloading}|{current}")

def write_file(name):
    if currently_downloading != "":
        fancy_print(f"Writing File \"{name}\"...", f"Download: {currently_downloading}", "D")

        file_name = name
        if not name in ["meta", "audio"]: file_name = f"charts/{name}"
        elif name == "audio": file_name = f"audio{ext}"
        elif name == "meta": file_name = f"meta.json"

        file = open(f"{profile_options["Customisation"]["content_folder"]}/Songs/{currently_downloading}/{file_name}", "w")
        try:
            file.write(download[name]["content"])
        except:
            file.close()
            file = open(f"{profile_options["Customisation"]["content_folder"]}/Songs/{currently_downloading}/{file_name}", "wb")
            file.write(download[name]["content"])

        file.close()
        fancy_print(f"Written File \"{name}\" Successfully...", f"Download: {currently_downloading}", "D")

#

def fancy_print(content, header = "", icon = ""):
    print()
    to_print = ""
    if header != "": to_print = (f"[{header} - {time.strftime("%H:%M:%S", time.gmtime())}]")
    else: to_print = (f"[{time.strftime("%H:%M:%S", time.gmtime())}]")
    if icon != "": to_print = f"[{icon}] {to_print}"

    print(f"{to_print} ---------")
    print(content)