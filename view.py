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
    


    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height,
        0, GL_RGBA, GL_UNSIGNED_BYTE, image.tostring()
    )
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glGenerateMipmapEXT(GL_TEXTURE_2D)
    return tex

def init(width, height):
    global window, planet_tex, ship_tex, goo_tex, asteroid_tex
    window = pyglet.window.Window(1024, 768)
    planet_tex = load_texture("assets/planet.png")
    ship_tex = load_texture("assets/ship.png")
    goo_tex = load_texture("assets/goo.png")
    asteroid_tex = load_texture("assets/asteroid.png")

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
        glColor4f(0.6, 0.6, 0.6, 1)
    elif owner == 1:
        glColor4f(1, 0.5, 0.5, 1)
    else:
        glColor4f(0.5, 1, 0.5, 1)
        
def scale_for_fleetsize(size):
    return math.log(size+1)/2.0

class Fleet():
    def __init__(self,ships,position,direction,player):
        self.ships = ships
        self.direction = direction
        self.position = position
        self.player = player
    

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
    glScalef(20, 20, 1)

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


    ship_textures = [ship_tex,goo_tex,asteroid_tex]
    fleets= []
    
    #glBindTexture(GL_TEXTURE_2D, ship_tex)
    for planet in state['planets']:
        pos = vector.Point(planet['x'], planet['y'])
        direction = vector.Point(1,0)
        fleet = Fleet(planet['ships'], pos, direction, planet['owner_id'] )
        fleets.append(fleet)
        

    
    for fleet in state['fleets']:
        origin = planet_by_id[fleet['origin']]
        target = planet_by_id[fleet['target']]
        origin = vector.Point(origin['x'], origin['y'])
        target = vector.Point(target['x'], target['y'])

        time_remaining = fleet['eta'] - state['round']
        direction = vector.Normalize(origin - target)
        
        pos = target + direction * time_remaining
        owner = fleet['owner_id']
        ships = fleet['ships']
        fleets.append(Fleet(ships,pos,direction,owner))
        
        
    for fleet in fleets:
        owner = fleet.player
        ships = fleet.ships
        pos = fleet.position
        angle = vector.Angle(fleet.direction)
        size = scale_for_fleetsize(sum(ships))
        glPushMatrix()
        glTranslatef(pos.x, pos.y, 0)
        glRotatef(angle+180,0,0,1)
        #glScalef(size, size, 1)
        color_for_owner(owner)
        for i,ship in enumerate(ships):
            glPushMatrix()
            glRotatef(i*120,0,0,1)
            glTranslatef(size*0.5,0,0)
            glRotatef(i*-120,0,0,1)
            scale = scale_for_fleetsize(ship)
            glScalef(scale,scale,1)
            glBindTexture(GL_TEXTURE_2D, ship_textures[i])
            draw_image()
            glPopMatrix()
        glPopMatrix()


    glPopMatrix()

    window.flip()


