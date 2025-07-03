class object():
    type = ""

    def __init__(self, tag, input_data):
        self.tag = tag

        self.position = [0,0]
        self.size = [0,0]
        self.rotation = 0.0
        self.opacity = 255

        self.priority = 1

    def set_property(self, property, value):
        match property:
            case "position:x": self.position[0] = value
            case "position:y": self.position[1] = value
            case "position": self.position = value
            case "size": self.size = value
            case "size:x": self.size[0] = value
            case "size:y": self.size[1] = value
            case "opacity": self.opacity = int(value)
            case "rotation": self.rotation = value
            case _: print(f"Couldn't find property '{property}' in {self.tag} ({self.type})")
    
    def get_property(self, property):
        match property:
            case "tag": return self.tag
            case "position": return self.position
            case "position:x": return self.position[0]
            case "position:y": return self.position[1]
            case "size": return self.size
            case "size:x": return self.size[0]
            case "size:y": return self.size[1]
            case "opacity": return self.opacity
            case "rotation": return self.rotation
            case _: print(f"Couldn't find property '{property}' in {self.tag} ({self.type})")
    
    def get_type(self):
        return self.type

class image(object):
    def __init__(self, tag, location):
        self.tag = tag
        self.image_location = location

        self.position = [0,0]
        self.size = [0,0]
        self.scale = [1,1]
        self.opacity = 255
        self.rotation = 0.0

        self.priority = 1

        self.type = "image"

    def set_property(self, property, value):
        match property:
            case "priority": self.priority = value
            case "image_location": self.image_location = value
            case "position": self.position = value
            case "position:x": self.position[0] = value
            case "position:y": self.position[1] = value
            case "size": self.size = value
            case "size:x": self.size[0] = value
            case "size:y": self.size[1] = value
            case "scale": self.scale = value
            case "scale:x": self.scale[0] = value
            case "scale:y": self.scale[1] = value
            case "opacity": self.opacity = int(value)
            case "rotation": self.rotation = value
            case _: print(f"Couldn't find property '{property}' in {self.tag} ({self.type})")
    
    def get_property(self, property):
        match property:
            case "priority": return self.priority
            case "tag": return self.tag
            case "image_location": return self.image_location
            case "position": return self.position
            case "position:x": return self.position[0]
            case "position:y": return self.position[1]
            case "size": return self.size
            case "size:x": return self.size[0]
            case "size:y": return self.size[1]
            case "scale": return self.scale
            case "scale:x": return self.scale[0]
            case "scale:y": return self.scale[1]
            case "opacity": return self.opacity
            case "rotation": return self.rotation
            case _: print(f"Couldn't find property '{property}' in {self.tag} ({self.type})")

class text(object):
    def __init__(self, tag, text):
        self.tag = tag

        self.text = text
        self.font = "default"
        self.text_size = 16
        self.color = "#FFFFFF"

        self.position = [0,0]
        self.size = [1,1]
        self.scale = [1,1]
        self.opacity = 255
        self.rotation = 0.0

        self.priority = 1

        self.type = "text"

        self.text_align = "left"

    def set_property(self, property, value):
        match property:
            case "priority": self.priority = value
            case "text": self.text = value
            case "position": self.position = value
            case "position:x": self.position[0] = value
            case "position:y": self.position[1] = value
            case "size": self.size = value
            case "size:x": self.size[0] = value
            case "size:y": self.size[1] = value
            case "scale": self.scale = value
            case "scale:x": self.scale[0] = value
            case "scale:y": self.scale[1] = value
            case "opacity": self.opacity = int(value)
            case "rotation": self.rotation = value
            case "font": self.font = value
            case "font_size": self.text_size = value
            case "color": self.color = value
            case "text_align": self.text_align = value
            case _: print(f"Couldn't find property '{property}' in {self.tag} ({self.type})")
    
    def get_property(self, property):
        match property:
            case "priority": return self.priority
            case "tag": return self.tag
            case "text": return self.text
            case "position": return self.position
            case "position:x": return self.position[0]
            case "position:y": return self.position[1]
            case "size": return self.size
            case "size:x": return self.size[0]
            case "size:y": return self.size[1]
            case "scale": return self.scale
            case "scale:x": return self.scale[0]
            case "scale:y": return self.scale[1]
            case "opacity": return self.opacity
            case "rotation": return self.rotation
            case "font": return self.font
            case "font_size": return self.text_size
            case "color": return self.color
            case "text_align": return self.text_align
            case _: print(f"Couldn't find property '{property}' in {self.tag} ({self.type})")

class rectangle(object):
    def __init__(self, tag, color = "#FF0000"):
        self.tag = tag
        self.color = color

        self.position = [0,0]
        self.size = [0,0]
        self.scale = [1,1]
        self.opacity = 255

        self.priority = 1

        self.type = "rectangle"

    def set_property(self, property, value):
        match property:
            case "priority": self.priority = value
            case "color": self.color = value
            case "position": self.position = value
            case "position:x": self.position[0] = value
            case "position:y": self.position[1] = value
            case "size": self.size = value
            case "size:x": self.size[0] = value
            case "size:y": self.size[1] = value
            case "scale": self.scale = value
            case "scale:x": self.scale[0] = value
            case "scale:y": self.scale[1] = value
            case "opacity": self.opacity = int(value)
            case _: print(f"Couldn't find property '{property}' in {self.tag} ({self.type})")
    
    def get_property(self, property):
        match property:
            case "priority": return self.priority
            case "tag": return self.tag
            case "color": return self.color
            case "position": return self.position
            case "position:x": return self.position[0]
            case "position:y": return self.position[1]
            case "size": return self.size
            case "size:x": return self.size[0]
            case "size:y": return self.size[1]
            case "scale": return self.scale
            case "scale:x": return self.scale[0]
            case "scale:y": return self.scale[1]
            case "opacity": return self.opacity
            case _: print(f"Couldn't find property '{property}' in {self.tag} ({self.type})")