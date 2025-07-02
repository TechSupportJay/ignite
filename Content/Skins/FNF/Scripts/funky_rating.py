def create(self):
    rating.set_property("position", [0,-200])
    self.rating_count = 0
    self.to_kill = []

def get_rating(self, diff):
    if diff <= profile_options["Gameplay"]["timings"]["perfect"]: return "perf"
    elif diff <= profile_options["Gameplay"]["timings"]["okay"]: return "okay"
    else: return "bad"

def slap_some_tweens_on_it(self, obj):
    pos_1 = (720/2) - random.randint(50,70)
    pos_2 = pos_1 + random.randint(100,125)

    camera.do_tween(f"rating_{self.rating_count}_y1", obj, "position:y", pos_1, 0.35, "cubic", "out")
    camera.do_tween(f"rating_{self.rating_count}_y2", obj, "position:y", pos_2, 0.65, "cubic", "in", 0.35)
    camera.do_tween(f"rating_{self.rating_count}_x", obj, "position:x", (1280/2 + random.randint(-50,50)), 1, "cubic", "out")
    camera.do_tween(f"rating_{self.rating_count}_alpha", obj, "opacity", 0, 0.8, "linear", "out", 0.2)

def note_hit(self, lane, diff):
    new_rating = RMS.objects.image(f"rating_{self.rating_count}", f"{skin_dir}/Ratings/{self.get_rating(diff)}.png")
    new_rating.set_property("size", camera.get_image_size(f"{skin_dir}/Ratings/{self.get_rating(diff)}.png"))
    new_rating.set_property("scale", [0.5,0.5])
    new_rating.set_property("position", [1280/2,720/2])

    self.to_kill.append(new_rating)

    camera.add_item(new_rating)

    self.slap_some_tweens_on_it(new_rating)

    self.rating_count += 1

def beat_hit(self):
    if len(self.to_kill) == 0: return
    while self.to_kill[0].get_property("opacity") <= 0:
        camera.remove_item(self.to_kill[0].get_property("tag"))
        self.to_kill.pop(0)
        if len(self.to_kill) == 0: return