def create(self):
    self.ms_indicator = RMS.objects.text("ms_indicator", "0MS")
    self.ms_indicator.set_property("position", [1280/2, 720/2 + 30])
    self.ms_indicator.set_property("text_align", "center")
    self.ms_indicator.set_property("font", skin_grab("/Fonts/default.ttf"))
    self.ms_indicator.set_property("font_size", 32)
    self.ms_indicator.set_property("opacity", 0)

    camera.add_item(self.ms_indicator)

def note_hit(self, lane, diff):
    camera.cancel_tween("ms_indicator_pulse")

    self.ms_indicator.set_property("text", f"{round(diff*1000, 3)}MS")
    self.ms_indicator.set_property("opacity", 255)

    camera.do_tween("ms_indicator_pulse", self.ms_indicator, "opacity", 0, 0.45, "cubic", "in")