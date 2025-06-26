import pygame

class scene():
    def __init__(self, screen, tag):
        self.tag = tag
        self.ordered = []
        self.cameras = {}

        self.screen = screen
    
    def add_camera(self, cam):
        tag = cam.get_property("tag")
        if tag not in self.cameras.keys(): self.cameras[tag] = cam
        elif self.cameras[tag] == None: self.cameras[tag] = cam
        self.order_cams()
    
    def remove_camera(self, tag):
        self.items[tag] = None
        self.order_cams()
    
    def set_screen_size(self, new_size):
        for cam in self.ordered: self.cameras[cam].screen_size = new_size

    # Methods

    def order_cams(self):
        self.ordered = []
        for key in self.cameras.keys(): self.ordered.append(key)
        
        unsorted = False
        while not unsorted:
            unsorted = True
            for i in range(len(self.ordered)-1):
                c1 = self.cameras[self.ordered[i]].get_property("priority")
                c2 = self.cameras[self.ordered[i+1]].get_property("priority")
                if c1 > c2:
                    temp = self.ordered[i+1]
                    self.ordered[i+1] = self.ordered[i]
                    self.ordered[i] = temp
                    unsorted = False

    def render_scene(self):
        self.screen.fill("#000000")
        for tag in self.ordered:
            cam = self.cameras[tag]
            if cam == None: continue
            cam.render(self.screen)
        pygame.display.flip()