def spawn_a_text(self, pos):
    score_text = RMS.objects.text(f"score_txt_{pos[0]}_{pos[1]}", "Score: X  |  Misses: X  |  Rating: Sick!! (100%)")
    score_text.set_property("font", f"{skin_dir}/Fonts/default.ttf")
    score_text.set_property("font_size", 20)
    score_text.set_property("color", "#000000")
    score_text.set_property("text_align", "center")
    score_text.set_property("position", [1280/2 + pos[0], 50 + pos[1]])

    camera.add_item(score_text)
    self.all_texts.append(score_text)

def create(self):
    self.all_texts = []

    outline_size = 1
    poses = [
        [-outline_size,-outline_size],[-outline_size,0],[-outline_size,outline_size],
        [0,-outline_size],[0,outline_size],
        [outline_size,-outline_size],[outline_size,0],[outline_size,outline_size]
    ]
    for p in poses: self.spawn_a_text(p)

    score_text = RMS.objects.text("score_txt", "Score: X  |  Misses: X  |  Rating: Sick!! (100%)")
    score_text.set_property("font", f"{skin_dir}/Fonts/default.ttf")
    score_text.set_property("font_size", 20)
    score_text.set_property("text_align", "center")
    score_text.set_property("position", [1280/2, 50])

    camera.add_item(score_text)
    self.all_texts.append(score_text)

def update(self, dt):
    rank = skin_texts['Gameplay']['ranks'][player_stats['rank']]
    if player_stats["score"] == 0 and player_stats["accuracy"] == 0:
        rank = "?"
    for st in self.all_texts:
        st.set_property("text", f"Score: {player_stats["score"]}  |  Misses: {player_stats["misses"]}  |  Rating: {rank} ({round(player_stats["accuracy"] * 100, 2)}%)")

def note_hit(self, a, b):
    for i in range(9):
        camera.cancel_tween(f"score_text_bump_{i}_x")
        camera.cancel_tween(f"score_text_bump_{i}_y")

    i = 0
    for st in self.all_texts:
        st.set_property("size", [1.1,1.1])
        camera.do_tween(f"score_text_bump_{i}_x", st, "size:x", 1, 0.5, "cubic", "out")
        camera.do_tween(f"score_text_bump_{i}_y", st, "size:y", 1, 0.5, "cubic", "out")
        i += 1