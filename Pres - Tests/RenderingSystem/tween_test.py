import pygame, RMS.scenes, RMS.cameras, RMS.objects, math, time

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

pygame.display.set_caption("Rendering Stuff")

clock = pygame.time.Clock()
fps_cap = 0

ease_types = ["in", "out", "in-out"]
eases = ["cubic", "quad", "quart", "quint", "circ", "back", "elastic", "bounce", "expo"]

new_scene = RMS.scenes.scene(screen, "test")
new_camera = RMS.cameras.camera("top", 1)

i = 0
for trans in eases:
    x = 0
    for ease in ease_types:
        new_image = RMS.objects.image(f"{trans}_{ease}", "images/jibby.jpg")
        new_image.set_property("size", [50,50])
        new_image.set_property("position", [50 + (400*x),50+(60*i)])
        new_camera.add_item(new_image)

        new_camera.do_tween(f"{trans}_{ease}_tween", new_image, "position:x", (50 + (400*x) + 300), 0.5, trans, ease, ((i * 3) + x) * 0.5)
        x += 1
    i += 1


new_scene.add_camera(new_camera)

current_scene = new_scene

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        match event.type:
            case pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    new_camera.set_property("scale:x", new_camera.get_property("scale:x")+0.2)
                    new_camera.set_property("scale:y", new_camera.get_property("scale:y")+0.2)
                elif event.key == pygame.K_DOWN:
                    new_camera.set_property("scale:x", new_camera.get_property("scale:x")-0.2)
                    new_camera.set_property("scale:y", new_camera.get_property("scale:y")-0.2)
            case pygame.VIDEORESIZE:
                new_camera.set_property("scale", [1280/event.w, 720/event.h])
    new_scene.render_scene()