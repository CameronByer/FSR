import pygame
import random
from os.path import exists

from Entity import Entity

WIDTH = 800
HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
SEWERGREEN = (160, 192, 144)
BLUE = (0, 0, 255)
BROWN = (143, 77, 44)
PURPLE = (127, 0, 255)
STONE = (127, 127, 127)
STONEWALL = (40, 40, 30)

RATSIZE = 16

POISON = 10 #DMG/SEC

BLOCKPIXELS = 32
BLOCKFEET = 3

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FSR")
clock = pygame.time.Clock() ## For syncing the FPS

def loadtile(tile):
    if exists("Tiles\\"+tile+".png"):
        return[pygame.image.load("Tiles\\"+tile+".png").convert_alpha()]
    tilelist = []
    index = 0
    while exists("Tiles\\"+tile+"_"+str(index)+".png"):
        tilelist.append(pygame.image.load("Tiles\\"+tile+"_"+str(index)+".png").convert_alpha())
        index += 1
    return tilelist

ITEM_LIST = ["Apple"]
ITEM_BANK = {item : pygame.image.load("Items\\"+item+".png").convert_alpha() for item in ITEM_LIST}

TILE_LIST = ["Sewer", "Stone", "Void", "Wall"]
TILE_BANK = {tile : loadtile(tile) for tile in TILE_LIST}

ENEMY_LIST = ["Sewer Ooze"]
ENEMY_BANK = {enemy : pygame.image.load("Enemies\\"+enemy.replace(" ", "_")+".png").convert_alpha() for enemy in ENEMY_LIST}

RAT_IMAGE = pygame.image.load("Rat.png").convert_alpha()

class Rat(Entity):

    def __init__(self, x, y):
        Entity.__init__(self, x, y, RATSIZE, RATSIZE, RAT_IMAGE, 12)
        self.health = 100
        self.maxhealth = 100
        self.inventory = [None]*5
        self.poison = 0
        self.maxpoison = 3*FPS

    def pickup(self, worlditem):
        for slot in range(5):
            if self.inventory[slot] == None:
                self.inventory[slot] = Item(worlditem.style)
                return True
        return False

    def distancetopoint(self, x, y):
        return ((self.x-x)**2+(self.y-y)**2)**0.5

    def draw(self, camerax, cameray):
        Entity.draw(self, screen, camerax, cameray)
        self.drawhealthbar(WIDTH-110, HEIGHT-30)

    def drawhealthbar(self, x, y, width=100, height=20, border=3):
        pygame.draw.rect(screen, BLACK, (x, y, width, height))
        percentpoison = min(1, self.poison/self.maxpoison)
        pygame.draw.rect(screen, PURPLE, (x+width-percentpoison*width, y, percentpoison*width, height))
        
        pygame.draw.rect(screen, GREEN, (x+border, y+border, width-border*2, height-border*2))
        percentmissing = (self.maxhealth-self.health)/self.maxhealth
        missingwidth = percentmissing * (width-2*border)
        pygame.draw.rect(screen, RED, (x+border, y+border, missingwidth, height-border*2))

    def drawinventory(self, slotsize = 40, spacing = 10, border = 2):
        for i in range(5):
            pygame.draw.rect(screen, BLACK, (spacing+(slotsize+spacing)*i, HEIGHT-slotsize-spacing, slotsize, slotsize))
            pygame.draw.rect(screen, WHITE, (spacing+(slotsize+spacing)*i+border, HEIGHT-slotsize-spacing+border, slotsize-2*border, slotsize-2*border))
            if self.inventory[i] != None:
                self.inventory[i].draw(spacing+(slotsize+spacing)*i+border, HEIGHT-spacing-slotsize+border, slotsize-4*border, slotsize-4*border)
    
    def update(self, worldmap):
        Entity.update(self, worldmap, FPS)
        inpoison = False
        for tile in worldmap.gettilecollisions(self):
            if tile.style == "Sewer":
                inpoison = True
                
        if inpoison:
            self.poison += 1
            self.poison = min(self.poison, self.maxpoison)
            self.tempmaxspeed = self.maxspeed*2/3
        else:
            if self.poison > 0:
                self.poison -= 1

        for item in worldmap.getitemcollisions(self):
            if self.pickup(item):
                item.active = False

        if self.poison > 0:
            self.health -= POISON/FPS

        if self.health <=0:
            self.health = self.maxhealth
            self.poison = 0
            self.inventory = [None]*5
            self.x = worldmap.spawnx
            self.y = worldmap.spawny
        elif self.health > self.maxhealth:
            self.health = self.maxhealth
            

class Map:

    def __init__(self, sizex, sizey):
        self.sizex = sizex
        self.sizey = sizey
        self.spawnx = 0
        self.spawny = 0
        self.enemies = []
        self.items = []
        self.tiles = [[Tile("Void", x*BLOCKPIXELS, y*BLOCKPIXELS, True, False) for y in range(self.sizey)] for x in range(self.sizex)]
        self.nodes = []
        self.generate()

    def connectnodes(self, a, b, radius, water_radius):
        if a.x == b.x:
            self.gencorridor(a.x, a.y, 0, int((b.y-a.y)/abs(b.y-a.y)), abs(b.y-a.y), radius, water_radius)
            a.child = b
        elif a.y == b.y:
            self.gencorridor(a.x, a.y, int((b.x-a.x)/abs(b.x-a.x)), 0, abs(b.x-a.x), radius, water_radius)
            a.child = b
        else:
            if random.randint(0, 1):
                cornernode = Node(a.x, b.y)
            else:
                cornernode = Node(b.x, a.y)
            self.nodes.append(cornernode)
            self.connectnodes(a, cornernode, radius, water_radius)
            self.connectnodes(cornernode, b, radius, water_radius)
            

    def draw(self, camerax, cameray):
        for x in range(self.sizex):
            for y in range(self.sizey):
                self.tiles[x][y].draw(x*BLOCKPIXELS, y*BLOCKPIXELS, camerax, cameray)
        for item in self.items:
            item.draw(screen, camerax, cameray)
        for enemy in self.enemies:
            enemy.draw(screen, camerax, cameray)
            
    def gencorridor(self, x, y, dirx, diry, length, radius, water_radius):
        for i in range(length+2*radius+1):
            relx = x + dirx*(i-radius)
            rely = y + diry*(i-radius)
            for j in range(radius+1):
                if j<water_radius and i>radius-water_radius and i<(length+2*radius-(radius-water_radius)):
                    tile1 = Tile("Sewer", (relx+diry*j)*BLOCKPIXELS, (rely+dirx*j)*BLOCKPIXELS, False, True, 3)
                    tile2 = Tile("Sewer", (relx-diry*j)*BLOCKPIXELS, (rely-dirx*j)*BLOCKPIXELS, False, True, 3)
                elif j<radius and i>0 and i<length+2*radius:
                    tile1 = Tile("Stone", (relx+diry*j)*BLOCKPIXELS, (rely+dirx*j)*BLOCKPIXELS, False, False, 2)
                    tile2 = Tile("Stone", (relx-diry*j)*BLOCKPIXELS, (rely-dirx*j)*BLOCKPIXELS, False, False, 2)
                else:
                    tile1 = Tile("Wall", (relx+diry*j)*BLOCKPIXELS, (rely+dirx*j)*BLOCKPIXELS, True, False, 1)
                    tile2 = Tile("Wall", (relx-diry*j)*BLOCKPIXELS, (rely-dirx*j)*BLOCKPIXELS, True, False, 1)
                self.placetile(tile1, relx+diry*j, rely+dirx*j)
                self.placetile(tile2, relx-diry*j, rely-dirx*j)

    def generate(self, tunnelradius=5, sewageradius=2, nodenum=10):
        startx = tunnelradius
        starty = tunnelradius
        startnode = Node(startx, starty, None)
        self.nodes.append(startnode)
        newnodes = []
        for i in range(nodenum):
            newnodes.append(Node(random.randint(tunnelradius, self.sizex-tunnelradius-1), random.randint(tunnelradius, self.sizey-tunnelradius-1)))
        while newnodes != []:
            closestdist = self.sizex+self.sizey
            closestconnection = None
            for node in self.nodes:
                for newnode in newnodes:
                    dist = node.dist(newnode)
                    if dist < closestdist:
                        closestconnection = (node, newnode)
                        closestdist = dist
            if dist > 0:
                self.connectnodes(closestconnection[0], closestconnection[1], tunnelradius, sewageradius)
                self.nodes.append(closestconnection[1])
            newnodes.remove(closestconnection[1])

        for i in range(self.sizex*self.sizey//100):
            x = random.randint(0, self.sizex*BLOCKPIXELS-1)
            y = random.randint(0, self.sizey*BLOCKPIXELS-1)
            if self.tiles[x//BLOCKPIXELS][y//BLOCKPIXELS].style == "Stone":
                a = WorldItem("Apple", x, y, 14, 14)
                self.items.append(a)

        for i in range(self.sizex*self.sizey//200):
            x = random.randint(0, self.sizex*BLOCKPIXELS-1)
            y = random.randint(0, self.sizey*BLOCKPIXELS-1)
            if self.tiles[x//BLOCKPIXELS][y//BLOCKPIXELS].style == "Stone":
                s = Enemy("Sewer Ooze", x, y, 24, 24, 8)
                self.enemies.append(s)

        while self.spawnx == 0 and self.spawny == 0:
            x = random.randint(BLOCKPIXELS, (self.sizex-1)*BLOCKPIXELS)
            y = random.randint(BLOCKPIXELS, (self.sizey-1)*BLOCKPIXELS)
            if self.tiles[x//BLOCKPIXELS][y//BLOCKPIXELS].style == "Stone":
                self.spawnx = x
                self.spawny = y

    def gettilecollisions(self, entity, offx=0, offy=0):
        collisions = []
        for i in range(int(entity.x+offx)//BLOCKPIXELS, int(entity.x+entity.sizex+offx)//BLOCKPIXELS+1):
            for j in range(int(entity.y+offy)//BLOCKPIXELS, int(entity.y+entity.sizey+offy)//BLOCKPIXELS+1):
                collisions.append(self.tiles[i][j])
        return collisions

    def getitemcollisions(self, entity):
        return [item for item in self.items if entity.iscollision(item)]

    def placetile(self, tile, x, y):
        if x>=0 and x<self.sizex and y>=0 and y<self.sizey:
            if tile.priority >= self.tiles[x][y].priority:
                self.tiles[x][y] = tile

    def update(self, rat):
        for enemy in self.enemies:
            enemy.update(self, rat)
        self.items = [item for item in self.items if item.active]


class Enemy(Entity):

    def __init__(self, style, x, y, sizex, sizey, maxspeed):
        image = ENEMY_BANK[style]
        image = pygame.transform.scale(ENEMY_BANK[style], (sizex, sizey))
        Entity.__init__(self, x, y, sizex, sizey, image, maxspeed)
        self.style = style

    def update(self, worldmap, rat):
        self.speedx = rat.x - self.x
        self.speedy = rat.y - self.y
        if self.getspeed() != 0:
            self.setspeed(self.tempmaxspeed)
        Entity.update(self, worldmap, FPS)

        inpoison = False
        for tile in worldmap.gettilecollisions(self):
            if tile.style == "Sewer":
                inpoison = True
                
        if inpoison:
            self.tempmaxspeed = self.maxspeed*2
        

class Node:

    def __init__(self, x, y, child=None):
        self.x = x
        self.y = y
        self.child = child

    def dist(self, other):
        return ((self.x-other.x)**2+(self.y-other.y)**2)**0.5


class Tile(Entity):

    def __init__(self, style, x, y, solid, water, priority = 0):
        self.style = style
        self.solid = solid
        self.water = water
        self.priority = priority
        self.image = None
        if style in TILE_LIST:
            self.image = pygame.transform.scale(random.choice(TILE_BANK[style]), (BLOCKPIXELS, BLOCKPIXELS))

    def draw(self, x, y, camerax, cameray):
        if self.image == None:
            pygame.draw.rect(screen, TILE_COLORS[self.style], (x-camerax, y-cameray, BLOCKPIXELS, BLOCKPIXELS))
        else:
            screen.blit(self.image, (x-camerax, y-cameray))


class WorldItem(Entity):

    def __init__(self, style, x, y, sizex, sizey):
        self.style = style
        image = ITEM_BANK[style]
        image = pygame.transform.scale(image, (sizex, sizey))
        image.set_colorkey(WHITE)
        Entity.__init__(self, x, y, sizex, sizey, image)


class Item:

    def __init__(self, style):
        self.style = style
        self.image = ITEM_BANK[style]
        self.image.set_colorkey(WHITE)

    def draw(self, x, y, sizex, sizey):
        image = pygame.transform.scale(self.image, (sizex, sizey))
        screen.blit(image, (x, y))


m = Map(60, 60)
r = Rat(m.spawnx, m.spawny)

running = True
while running:

    clock.tick(FPS) ## will make the loop run at the same speed all the time
    keysdown = state = pygame.key.get_pressed()
    if keysdown[pygame.K_d]:
        r.speedx = r.maxspeed
    elif keysdown[pygame.K_a]:
        r.speedx = -r.maxspeed
    else:
        r.speedx = 0
    if keysdown[pygame.K_s]:
        r.speedy = r.maxspeed
    elif keysdown[pygame.K_w]:
        r.speedy = -r.maxspeed
    else:
        r.speedy = 0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            pass
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: #Left Click
                pass
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: #Left Click
                pass

    m.update(r)
    r.update(m)
    camerax = r.x - WIDTH//2
    cameray = r.y - HEIGHT//2
    screen.fill(BLACK)
    m.draw(camerax, cameray)
    r.draw(camerax, cameray)
    r.drawinventory()

    pygame.display.flip()       

pygame.quit()
