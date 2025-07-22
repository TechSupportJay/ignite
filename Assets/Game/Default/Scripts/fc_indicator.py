def __init__(self):
    self.fcing = True

def create(self):
    self.fc_indicator = RMS.objects.text("fc_indicator", "FC")
    self.fc_indicator.set_property("position:x", 1280/2)
    if downscroll: self.fc_indicator.set_property("position:y", -50)
    else: self.fc_indicator.set_property("position:y", 720)
    self.fc_indicator.set_property("text_align", "center")
    self.fc_indicator.set_property("font", skin_grab("Fonts/default.ttf"))
    self.fc_indicator.set_property("font_size", 64)

    if downscroll: camera.do_tween("fc_move", self.fc_indicator, "position:y", 10, 1, "back", "out")
    else: camera.do_tween("fc_move", self.fc_indicator, "position:y", 630, 1, "back", "out")

    camera.add_item(self.fc_indicator)

def note_miss(self, lane):
    if self.fcing:
        self.fcing = False

        camera.cancel_tween("fc_move")
        camera.remove_item("fc_indicator")