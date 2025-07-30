def update(self):
    for item in camera.items.keys():
        if item == "background": continue
        i = camera.items[item]
        i.set_property("rotation", random.randint(0,360))