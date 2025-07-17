import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random

screen = None
master_data = []

# Variables

screen = None
scene = None
camera = None

# Master Functions

def init():
    global scene, camera

    scene = RMS.scenes.scene(screen, "Splash")
    camera = RMS.cameras.camera("HUD", 1)
    scene.add_camera(camera)

    camera.set_property("zoom", [1.15,1.15])

    temp_text = RMS.objects.text("temp_splash_text", "[TEMP]: Press Enter to Load Game")
    temp_text.set_property("position:x", 1280/2)
    temp_text.set_property("position:y", 800)
    temp_text.set_property("text_align", "center")
    temp_text.set_property("font", "Assets/UI/Fonts/default.ttf")
    temp_text.set_property("font_size", 32)

    camera.do_tween("text_rise", temp_text, "position:y", 720/2, 0.5, "back", "out")
    camera.do_tween("zoom_scene_x", camera, "zoom:x", 1, 1, "cubic", "out")
    camera.do_tween("zoom_scene_y", camera, "zoom:y", 1, 1, "cubic", "out")

    camera.add_item(temp_text)

def update():
    scene.render_scene()

def handle_event(event):
    match event.type:
        case pygame.KEYDOWN:
            match event.key:
                case pygame.K_RETURN: master_data.append(["switch_scene", "song_selection"])

def destroy():
    global camera, scene
    del camera, scene