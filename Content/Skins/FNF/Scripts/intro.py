def __init__(self):
    self.intro_index = 0
    self.intro_nums = ["3","2","1","Go"]

def create(self):
    self.intro = RMS.objects.image("intro_text", f"{skin_dir}/Intro/2.png")
    self.intro.set_property("position", [1280/2,720/2])
    self.intro.set_property("scale", [0.8,0.8])
    camera.add_item(self.intro)
    
    camera.cache_image_bulk([f"{skin_dir}/Intro/2.png",f"{skin_dir}/Intro/1.png",f"{skin_dir}/Intro/Go.png"])

def play_intro(self, index):
    if index > 0:
        camera.cancel_tween("intro_pulse")
        self.intro.set_property("image_location", f"{skin_dir}/Intro/{self.intro_nums[self.intro_index]}.png")
        self.intro.set_property("size", camera.get_image_size(f"{skin_dir}/Intro/{self.intro_nums[self.intro_index]}.png"))
        self.intro.set_property("opacity", 255)
        camera.do_tween("intro_pulse", self.intro, "opacity", 0, 0.5)
    self.intro_sfx = pygame.mixer.Sound(f"{skin_dir}/Intro/intro{self.intro_nums[self.intro_index]}.ogg")
    self.intro_sfx.set_volume(0.5)
    self.intro_sfx.play()

def update(self, dt):
    if cur_time < 0:
        if cur_time >= -(((step_time*4)) * (4 - self.intro_index)):
            self.play_intro(self.intro_index)
            self.intro_index += 1