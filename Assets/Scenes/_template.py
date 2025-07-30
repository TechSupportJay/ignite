import pygame.locals
import RMS.scenes, RMS.cameras, RMS.objects
import pygame, os, math, time, json, random

screen = None
master_data = []

# Variables

screen = None
scene = None
camera = None

#

profile_options = {}

# Master Functions

def init(data = []):
    global scene, camera

    scene = RMS.scenes.scene(screen, "Template")
    camera = RMS.cameras.camera("HUD", 1)
    scene.add_camera(camera)

def update():
    scene.render_scene()

def handle_event(event):
    match event.type:
        case pygame.KEYDOWN:
            match event.key:
                case _: pass
        case pygame.VIDEORESIZE:
            camera.set_property("scale", [event.w/1280, event.h/720])
            camera.set_property("position", [(event.w-1280)/2,(event.h-720)/2])

def destroy():
    global camera, scene
    del camera, scene

def resize(size):
    for cam in scene.cameras.keys():
        scene.cameras[cam].set_property("scale", [size[0]/1280,size[1]/720])
        scene.cameras[cam].set_property("position", [(size[0]-1280)/2,(size[1]-720)/2])