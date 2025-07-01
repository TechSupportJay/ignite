def create(self):
    self.starting = time.time_ns() / 1_000_000.0 / 1_000.0
    self.fps = 0
    self.framerate = 0

    self.fps_counter = RMS.objects.text("fps_counter", "X FPS")
    self.fps_counter.set_property("font", f"{skin_dir}/Fonts/default.ttf")
    self.fps_counter.set_property("font_size", 14)
    self.fps_counter.set_property("color", "#FFFFFF")
    self.fps_counter.set_property("position", [5,300])

    camera.add_item(self.fps_counter)

def update(self):
    self.fps += 1
    fuckMeInTheAss = time.time_ns() / 1_000_000.0 / 1_000.0
    if fuckMeInTheAss >= self.starting + 1.0:
        self.framerate = self.fps
        self.fps = 0
        self.starting = fuckMeInTheAss
    self.fps_counter.set_property("text", f"{int(self.framerate)} FPS")