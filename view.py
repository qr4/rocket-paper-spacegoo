import math
import pyglet
import Image
from pyglet.gl import *
from ctypes import pointer
import vector


windowheight = 23
windowwidth = 42

server_tex = []
malware_tex = []

def load_texture(filename):
    image = Image.open(filename).convert('RGBA')

    width, height = image.size
    tex = GLuint()
    glGenTextures(1, pointer(tex))

    glBindTexture(GL_TEXTURE_2D, tex)
    

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA, width, height,
        0, GL_RGBA, GL_UNSIGNED_BYTE, image.tostring()
    )
   
    glEnable(GL_TEXTURE_2D) # fix for some ati cards
    glGenerateMipmapEXT(GL_TEXTURE_2D)

    return tex

        
def on_resize(width, height):
    global windowheight,windowwidth
    windowheight = height
    windowwidth = width
    glViewport(0, 0, width, height)
    glMatrixMode(gl.GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(gl.GL_MODELVIEW)
    return pyglet.event.EVENT_HANDLED

def init(width, height):
    global windowheight,windowwidth
    windowheight = height
    windowwidth = width
    global window, server_tex, malware_tex
    window = pyglet.window.Window(width, height, resizable=True, caption = "zomg a shitty viewer window")
    load_texture("assets/dos.png")
    server_tex = map(load_texture,["assets/dos.png", "assets/windows.png", "assets/mac.png"])
    malware_tex =  map(load_texture,["assets/virus.png","assets/trojan.png","assets/worm.png"])
    window.on_resize = on_resize  

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
    
def draw_slice(startRad,endRad):
    if endRad-startRad>2.42: #i have no idea what i'm doing
        #print "angle too big: ", startRad,endRad
        draw_slice(startRad,(startRad+endRad)/2.0)
        draw_slice((startRad+endRad)/2.0,endRad)
        return
    
    def drawPoint(p):
        #print p.x, p.y
        glTexCoord2f(0.5+0.5*p.x, 0.5+0.5*p.y)
        glVertex2f(p.x, p.y)
    #print ""
        
    glBegin(GL_QUADS)
    
    middle = vector.Point(0, 0)
    start = vector.Point(math.cos(startRad), math.sin(startRad))
    end = vector.Point(math.cos(endRad), math.sin(endRad))
    far = vector.Normalize(start+end)*5.23 #again, i have no idea
    
    
    
    drawPoint(middle)
    drawPoint(start)
    drawPoint(far)
    drawPoint(end)
    
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
    
    global windowheight,windowwidth

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)

    glClear(GL_COLOR_BUFFER_BIT)

    glEnable(GL_TEXTURE_2D)

    glPushMatrix()

    glTranslatef(windowwidth/2, windowheight/2, 0)
    
    scale = min(windowwidth/1.33,windowheight)/42
    glScalef(scale, scale, 1)

    glColor4f(1,0,0,1)

    
    planet_by_id = {}
    for planet in state['planets']:
        planet_by_id[planet['id']] = planet
        
        glPushMatrix()
        glTranslatef(planet['x'], planet['y'], 0)
        prodsum = sum(planet['production'])
        size = scale_for_fleetsize(prodsum)*2
        glScalef(size, size, 1)
        #color_for_owner(planet['owner_id'])
#        draw_image()
        radSum = 0.0
        #glRotatef(180,0,0,1)
        for i,prod in enumerate(planet['production']):
            #print "prod: ", i, prod, prodsum
            glBindTexture(GL_TEXTURE_2D, server_tex[i])
            startRad = radSum
            radSum += 2*3.14159*(prod*1.0/prodsum) #FUCK YOU PYTHON AND YOUR INTEGER DIVISION
            color_for_owner(planet['owner_id'])
            draw_slice(startRad,radSum)
        glPopMatrix()

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
            glBindTexture(GL_TEXTURE_2D, malware_tex[i])
            draw_image()
            glPopMatrix()
        glPopMatrix()


    glPopMatrix()

    window.flip()


