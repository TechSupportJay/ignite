import pygame, scenes, cameras, objects, math, time

pygame.init()
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.gl_set_attribute(pygame.GL_ACCELERATED_VISUAL, 1)

pygame.display.set_caption("Rendering Stuff")

clock = pygame.time.Clock()
fps_cap = 0

#

scene = scenes.scene(screen, "test")
camera = cameras.camera("top", 1)
fps_counter = objects.text("text", "0 FPS")

fps_counter.set_property("font", "comic.ttf")
fps_counter.set_property("font_size", 14)
fps_counter.set_property("color", "#FFFFFF")
fps_counter.set_property("position", [5,5])

scene.add_camera(camera)
camera.add_item(fps_counter)

image = objects.image("jibby", "images/jibby.jpg")
image.set_property("size", [50,50])
camera.add_item(image)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        match event.type:
            case pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    camera.set_property("scale:x", camera.get_property("scale:x")+0.2)
                    camera.set_property("scale:y", camera.get_property("scale:y")+0.2)
                elif event.key == pygame.K_DOWN:
                    camera.set_property("scale:x", camera.get_property("scale:x")-0.2)
                    camera.set_property("scale:y", camera.get_property("scale:y")-0.2)
            case pygame.VIDEORESIZE:
                camera.set_property("scale", [1280/event.w, 720/event.h])
    
    clock.tick(fps_cap)
    fps_counter.set_property("text", f"{int(clock.get_fps())} FPS")

    # if camera.get_property("scale:x") == 1:
    #     camera.set_property("scale:x", 1.05)
    #     camera.set_property("scale:y", 1.05)
    #     camera.do_tween("bump_tween_x", camera, "scale:x", 1, 0.75, "cubic", "out")
    #     camera.do_tween("bump_tween_y", camera, "scale:y", 1, 0.75, "cubic", "out")

    camera.do_tween("move_tween_x", image, "position:x", pygame.mouse.get_pos()[0], 0.5, "circ", "out")
    camera.do_tween("move_tween_y", image, "position:y", pygame.mouse.get_pos()[1], 0.5, "circ", "out")
    #image.set_property("position", pygame.mouse.get_pos())

    scene.render_scene()