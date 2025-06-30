import pygame, time, RMS.easing

pygame.font.init()

class camera():
    def __init__(self, tag, order):
        self.tag = tag
        self.priority = order

        self.ordered = []
        self.items = {}

        self.textures = {}
        self.fonts = {}

        self.scale = [1,1]
        self.position = [0,0]
        
        self.screen_size = [1280,720]

        self.tween_man = tween_manager()
    
    def add_item(self, item):
        tag = item.get_property("tag")
        if tag not in self.items.keys(): self.items[tag] = item
        elif self.items[tag] == None: self.items[tag] = item

        match item.get_type():
            case "image":
                if item.get_property("image_location") not in self.textures.keys():
                    self.textures[item.get_property("image_location")] = pygame.image.load(item.get_property("image_location")).convert_alpha()
            case "text":
                if (f"{item.get_property("font")}_{item.get_property("font_size")}") not in self.fonts.keys():
                    self.fonts[(f"{item.get_property("font")}_{item.get_property("font_size")}")] = pygame.font.Font(item.get_property("font"), item.get_property("font_size"))

        self.order_items()
    
    def remove_item(self, tag):
        self.items[tag] = None
        self.order_items()
    
    def set_property(self, property, value):
        match property:
            case "scale": self.scale = value
            case "scale:x": self.scale[0] = value
            case "scale:y": self.scale[1] = value
            case "position": self.position = value
            case "position:x": self.position[0] = value
            case "position:y": self.position[1] = value
            case "priority": self.priority = value
            case _: print(f"Couldn't find property '{property}' in {self.tag} (Camera)")
    
    def get_property(self, property):
        match property:
            case "tag": return self.tag
            case "scale": return self.scale
            case "scale:x": return self.scale[0]
            case "scale:y": return self.scale[1]
            case "position": return self.position
            case "position:x": return self.position[0]
            case "position:y": return self.position[1]
            case "priority": return self.priority
            case _: print(f"Couldn't find property '{property}' in {self.tag} (Camera)")
    
    def get_item(self, tag):
        if tag in self.items.keys():
            if not self.items[tag] == None:
                return self.items[tag]
    
    # Methods
    
    def order_items(self):
        self.ordered = []
        for key in self.items.keys():
            if self.get_item(key) is not None: self.ordered.append(key)

        unsorted = False
        while not unsorted:
            unsorted = True
            for i in range(len(self.ordered)-1):
                i1 = self.items[self.ordered[i]].get_property("priority")
                i2 = self.items[self.ordered[i+1]].get_property("priority")
                if i1 > i2:
                    temp = self.ordered[i+1]
                    self.items[i+1] = self.ordered[i]
                    self.items[i] = temp
                    unsorted = False
    
    def render(self, screen):
        if self.tween_man.return_size() > 0:
            for tag in self.tween_man.valid_tweens:
                tween = self.tween_man.tweens[tag]
                if tween.complete: tween = None; self.tween_man.set_valid()
                else: tween.item.set_property(tween.property, tween.return_tween_value())

        for tag in self.ordered:
            item = self.items[tag]
            match item.get_type():
                case "image":
                    to_blit = self.textures[item.get_property("image_location")]
                    to_blit = pygame.transform.scale(to_blit, [item.get_property("size")[0] * self.scale[0], item.get_property("size")[1] * self.scale[1]])
                    to_blit = pygame.transform.rotate(to_blit, item.get_property("rotation"))

                    orig_pos_x = (item.get_property("position")[0] - item.get_property("size")[0]/2)
                    orig_pos_y = (item.get_property("position")[1] - item.get_property("size")[1]/2)
                    orig_pos = (orig_pos_x, orig_pos_y)

                    new_pos_x = (orig_pos[0] - self.screen_size[0]/2) * self.scale[0] + self.screen_size[0]/2
                    new_pos_y = (orig_pos[1] - self.screen_size[1]/2) * self.scale[1] + self.screen_size[1]/2
                    new_pos = (new_pos_x, new_pos_y)
                    
                    screen.blit(to_blit, new_pos)
                case "text":
                    pre_blit = self.fonts[(f"{item.get_property("font")}_{item.get_property("font_size")}")]

                    to_blit = pre_blit.render(item.get_property("text"), True, item.get_property("color"))

                    to_blit = pygame.transform.scale_by(to_blit, [item.get_property("size")[0] * self.scale[0], item.get_property("size")[1] * self.scale[1]])
                    to_blit = pygame.transform.rotate(to_blit, item.get_property("rotation"))

                    orig_pos = item.get_property("position")
                    new_pos_x = (orig_pos[0] - self.screen_size[0]/2) * self.scale[0] + self.screen_size[0]/2
                    new_pos_y = (orig_pos[1] - self.screen_size[1]/2) * self.scale[1] + self.screen_size[1]/2
                    new_pos = (new_pos_x, new_pos_y)
                    
                    screen.blit(to_blit, new_pos)
                case "_": pass
    
    def do_tween(self, tween_tag, item, property, value, duration, trans, easing, delay = 0):
        tween = tween_instance(self, tween_tag, item, property, value, duration, easing, trans, delay)
        self.tween_man.tweens[tween_tag] = tween
        self.tween_man.set_valid()
    
    def cancel_tween(self, tween_tag):
        if not tween_tag in self.tween_man.tweens: return
        self.tween_man.tweens[tween_tag] = None
        self.tween_man.set_valid()
        

class tween_manager():
    def __init__(self):
        self.tweens = {}
        self.valid_tweens = {}
    
    def return_size(self):
        x = 0
        for item in self.tweens.keys():
            if item != None: x += 1
        return x

    def set_valid(self):
        self.valid_tweens = {}
        for tag in self.tweens.keys():
            tween = self.tweens[tag]
            if tween != None:
                if tween.start_time <= time.perf_counter():
                    self.valid_tweens[tween.tag] = tween

class tween_instance():
    def __init__(self, camera, tween_tag, item, property, end_result, duration, ease, trans, delay):
        self.tag = tween_tag
        self.item = item
        self.property = property

        self.start_prop = self.item.get_property(property)
        self.end_prop = end_result
        
        self.start_time = time.perf_counter() + delay
        self.end_time = duration

        self.easing = ease
        self.trans = RMS.easing.eases[trans.lower()]

        self.complete = False
    
    def return_tween_value(self):
        if not time.perf_counter() >= self.start_time: pos = 0
        else: pos = ((time.perf_counter() - self.start_time) / self.end_time)

        if pos >= 1:
            self.complete = True
            return self.end_prop
        else: return self.start_prop + ((self.end_prop-self.start_prop) * self.trans.process_ease(pos, self.easing))