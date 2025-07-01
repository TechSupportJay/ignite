import json, os, shutil

path = input("Enter Mod Songs Folder Path (Codename/Mods/Mod Name/Songs)\n> ")

output_path = input("Enter Output Path (Ignite/Content/Songs)\n> ")

if not os.path.isdir(path):
    print("[!] Path does not exist.")
    input("")
    exit()

songs = next(os.walk(path))[1]

if os.path.isdir("output"):
    shutil.rmtree("output")
    os.mkdir("output")

for song in songs:
    if not os.path.isdir(f"{output_path}/{song}"): os.mkdir(f"{output_path}{song}")
    if not os.path.isdir(f"{output_path}/{song}/charts"): os.mkdir(f"{output_path}/{song}/charts")

    # Chart

    charts = next(os.walk(f"{path}/{song}/charts"), (None, None, []))[2]

    og_meta_file = json.loads(open(f"{path}/{song}/meta.json", "r").read())

    meta_file = {"Name": "", "Artist": ""}
    meta = {"BPM": 0}

    meta["BPM"] = og_meta_file["bpm"]
    
    meta_file["Name"] = og_meta_file["displayName"]
    meta_file["Artist"] = "CODENAME TO IGNITE CONVERTER"

    # new_file = open(f"{output_path}/{song}/meta.json", "w")
    # new_file.write(json.dumps(meta_file))
    # new_file.close()

    for chart in charts:
        chart_file = open(f"{path}/{song}/charts/{chart}", "r").read().strip()

        notes = []
        template_note = {"p": 1, "t": 0.0}

        json_sls = json.loads(chart_file)["strumLines"]

        sec = []

        for section in json_sls:
            if "type" in section.keys():
                if section["type"] == 1:
                    sec = section["notes"]
                    break

        if sec == []: print(f"[!] {song} > {chart} Failed (No Valid Section).")

        notes_added = 0

        def new_note(time, position):
            global notes_added

            notes_added += 1

            note = template_note.copy()
            note["t"] = time
            note["p"] = position
            notes.append(note)

        for note in sec:
            new_note(float(note["time"]) / 1000, int(note["id"]+1))

        if notes_added == 0: print(f"[!] {song} > {chart} Failed (No Added Notes).")

        s_diff = chart.replace(".json", "")

        file_dict = {"notes": notes, "meta": meta}

        new_file = open(f"{output_path}/{song}/charts/{s_diff}.json", "w")
        new_file.write(json.dumps(file_dict))
        new_file.close()

        print(f"[/] {song} > {chart} Has Been Added")