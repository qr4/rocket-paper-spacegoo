import math
import pyglet
import Image
from pyglet.gl import *
from ctypes import pointer
import vector

def load_texture(filename):
    image = Image.open(filename).convert('RGBA')

    width, height = image.size
    tex = GLuint()
    glGenTextures(1, pointer(tex))

    glBindTexture(GL_TEXTURE_2D, tex)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height,
        0, GL_RGBA, GL_UNSIGNED_BYTE, image.tostring()
    )
    return tex

def init(width, height):
    global window, planet_tex, ship_tex
    window = pyglet.window.Window(1024, 768)
    planet_tex = load_texture("planet.png")
    ship_tex = load_texture("ship.png")

def draw_image():
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1)
    glVertex2f(-1, -1)
    glTexCoord2f(1, 1)
    glVertex2f(1, -1)
    glTexCoord2f(1, 0)
    glVertex2f(1, 1)
    glTexCoord2f(0, 0)
    glVertex2f(-1, 1)
    glEnd()

def color_for_owner(owner):
    if owner == 0:
        glColor4f(1, 1, 1, 1)
    elif owner == 1:
        glColor4f(1, 0.5, 0.5, 1)
    else:
        glColor4f(0.5, 1, 0.5, 1)

def update(state):
    window.dispatch_events()
    window.clear()

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)

    glClear(GL_COLOR_BUFFER_BIT)

    glEnable(GL_TEXTURE_2D)

    glPushMatrix()

    glTranslatef(1024/2, 768/2, 0)
    glScalef(30, 30, 1)

    glColor4f(1,0,0,1)

    glBindTexture(GL_TEXTURE_2D, planet_tex)
    planet_by_id = {}
    for planet in state['planets']:
        planet_by_id[planet['id']] = planet
        
        glPushMatrix()
        glTranslatef(planet['x'], planet['y'], 0)
        size = math.sqrt(sum(planet['production']))*2
        glScalef(size, size, 1)
        color_for_owner(planet['owner_id'])
        draw_image()
        glPopMatrix()

    glBindTexture(GL_TEXTURE_2D, ship_tex)
    for planet in state['planets']:
        glPushMatrix()
        glTranslatef(planet['x'], planet['y'], 0)
        size = math.sqrt(sum(planet['ships']))/3
        glScalef(size, size, 1)
        glColor4f(1,1,1,1)
        draw_image()
        glPopMatrix()

    glBindTexture(GL_TEXTURE_2D, ship_tex)
    for fleet in state['fleets']:
        origin = planet_by_id[fleet['origin']]
        target = planet_by_id[fleet['target']]
        origin = vector.Point(origin['x'], origin['y'])
        target = vector.Point(target['x'], target['y'])

        time_remaining = fleet['eta'] - state['round']
        pos = target + vector.Normalize(origin - target) * time_remaining
        size = math.sqrt(sum(fleet['ships']))/3
        glPushMatrix()
        glTranslatef(pos.x, pos.y, 0)
        glScalef(size, size, 1)
        color_for_owner(fleet['owner_id'])
        draw_image()
        glPopMatrix()


    glPopMatrix()

    window.flip()


