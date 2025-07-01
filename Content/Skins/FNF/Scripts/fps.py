def create(self):
    camera_made_entirely_just_to_display_the_fps_counter = RMS.cameras.camera("camera_made_entirely_just_to_display_the_fps_counter", 2)

    self.starting = time.time_ns() / 1_000_000.0 / 1_000.0
    self.fps = 0
    self.framerate = 0

    self.fps_counter = RMS.objects.text("fps_counter", "FPS: X")
    self.fps_counter.set_property("font", f"{skin_dir}/Fonts/arial.ttf")
    self.fps_counter.set_property("font_size", 12)
    self.fps_counter.set_property("color", "#FFFFFF")
    self.fps_counter.set_property("position", [5,5])

    scene.add_camera(camera_made_entirely_just_to_display_the_fps_counter)
    camera_made_entirely_just_to_display_the_fps_counter.add_item(self.fps_counter)

def update(self, dt):
    self.fps += 1
    fuckMeInTheAss = time.time_ns() / 1_000_000.0 / 1_000.0
    if fuckMeInTheAss >= self.starting + 1.0:
        self.framerate = self.fps
        self.fps = 0
        self.starting = fuckMeInTheAss
    self.fps_counter.set_property("text", f"FPS: {int(self.framerate)}")