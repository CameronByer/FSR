import pygame
import random

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

TILE_COLORS = {
    "Void": BLACK,
    "Sewer": SEWERGREEN,
    "Stone": STONE,
    "Wall": STONEWALL
}

ITEM_COLORS = {
    "Apple": RED
}

POISON = 10 #DMG/SEC

BLOCKPIXELS = 32
BLOCKFEET = 3

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FSR")
clock = pygame.time.Clock() ## For syncing the FPS

def mixcolors(a, b):
    return ((a[0]+b[0])//2, (a[1]+b[1])//2, (a[2]+b[2])//2)

class Rat:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.maxhealth = 100
        self.speedx = 0
        self.speedy = 0
        self.maxspeed = 12
        self.radius = 5
        self.poison = 0
        self.maxpoison = 3*FPS

    def getspeed(self): # Feet per second
        return (self.speedx**2+self.speedy**2)**0.5

    def setspeed(self, speed): # Feet per second
        curspeed = self.getspeed()
        if curspeed != 0:
            self.speedx *= speed/curspeed
            self.speedy *= speed/curspeed

    def pickup(self, item):
        item.active = False
        self.health += 25

    def distancetopoint(self, x, y):
        return ((self.x-x)**2+(self.y-y)**2)**0.5

    def draw(self, camerax, cameray, tileheight):
        pygame.draw.circle(screen, BROWN, (self.x-camerax-tileheight, self.y-cameray-tileheight), self.radius)

    def drawhealthbar(self, x, y, width=100, height=20, border=3):
        pygame.draw.rect(screen, BLACK, (x, y, width, height))
        percentpoison = min(1, self.poison/self.maxpoison)
        pygame.draw.rect(screen, PURPLE, (x+width-percentpoison*width, y, percentpoison*width, height))
        
        pygame.draw.rect(screen, GREEN, (x+border, y+border, width-border*2, height-border*2))
        percentmissing = (self.maxhealth-self.health)/self.maxhealth
        missingwidth = percentmissing * (width-2*border)
        pygame.draw.rect(screen, RED, (x+border, y+border, missingwidth, height-border*2))
    
    def update(self, m):
        if self.getspeed() >= self.maxspeed:
            self.setspeed(self.maxspeed)
        xmovement = self.speedx/FPS * BLOCKPIXELS/BLOCKFEET
        ymovement = self.speedy/FPS * BLOCKPIXELS/BLOCKFEET
        if any(tile.solid for tile in m.gettilecollisions(self.x+xmovement, self.y+ymovement, self.radius)):
            if any(tile.solid for tile in m.gettilecollisions(self.x+xmovement, self.y, self.radius)):
                xmovement = 0
                if any(tile.solid for tile in m.gettilecollisions(self.x, self.y+ymovement, self.radius)):
                    ymovement = 0
            else:
                ymovement = 0
        self.x += xmovement
        self.y += ymovement

        if self.poison > 0:
            self.poison -= 1
            
        for tile in m.gettilecollisions(self.x, self.y, self.radius):
            if tile.style == "Sewer":
                self.poison = self.maxpoison

        for item in m.getitemcollisions(self.x, self.y, self.radius):
            self.health += 25
            item.active = False

        if self.poison > 0:
            self.health -= POISON/FPS

        if self.health <=0:
            print("DEATH")
            self.health = self.maxhealth
        elif self.health > self.maxhealth:
            self.health = self.maxhealth
            

class Map:

    def __init__(self, sizex, sizey):
        self.sizex = sizex
        self.sizey = sizey
        self.tiles = [[Tile("Void", True, False, 0) for y in range(sizey)] for x in range(sizex)]
        self.items = {}

    def additem(self, item, x, y):
        self.items[item] = (x, y)

    def corridor(self, x, y, dirx, diry, length, radius, water_radius):
        for i in range(length+2*radius+1):
            relx = x + dirx*(i-radius)
            rely = y + diry*(i-radius)
            for j in range(radius+1):
                if j<water_radius and i>radius-water_radius and i<(length+2*radius-(radius-water_radius)):
                    tile1 = Tile("Sewer", False, True, -10, 3)
                    tile2 = Tile("Sewer", False, True, -10, 3)
                elif j<radius and i>0 and i<length+2*radius:
                    tile1 = Tile("Stone", False, False, 0, 2)
                    tile2 = Tile("Stone", False, False, 0, 2)
                else:
                    tile1 = Tile("Wall", True, False, 0, 1)
                    tile2 = Tile("Wall", True, False, 0, 1)
                if tile1.priority >= self.tiles[relx+diry*j][rely+dirx*j].priority:
                    self.tiles[relx+diry*j][rely+dirx*j] = tile1
                if tile2.priority >= self.tiles[relx-diry*j][rely-dirx*j].priority:
                    self.tiles[relx-diry*j][rely-dirx*j] = tile2

    def draw(self, camerax, cameray, rat):
        for x in range(self.sizex):
            for y in range(self.sizey):
                self.tiles[x][y].draw(x*BLOCKPIXELS, y*BLOCKPIXELS, camerax, cameray)
                if rat.x >= x*BLOCKPIXELS and rat.x < (x+1)*BLOCKPIXELS and rat.y >= y*BLOCKPIXELS and rat.y < (y+1)*BLOCKPIXELS:
                    rat.draw(camerax, cameray, self.tiles[x][y].height)
        for item, pos in self.items.items():
            item.draw(pos[0], pos[1], camerax, cameray)
            

    def gettilecollisions(self, x, y, radius):
        collisions = []
        for i in range(int(x-radius)//BLOCKPIXELS, int(x+radius)//BLOCKPIXELS+1):
            for j in range(int(y-radius)//BLOCKPIXELS, int(y+radius)//BLOCKPIXELS+1):
                collisions.append(self.tiles[i][j])
        return collisions

    def getitemcollisions(self, x, y, radius):
        collisions = []
        for item, pos in self.items.items():
            if ((x-pos[0])**2+(y-pos[1])**2)**0.5 < radius + item.radius:
                collisions.append(item)
        return collisions

    def update(self):
        self.items = {item: pos for item, pos in self.items.items() if item.active}
            

class Tile:

    def __init__(self, style, solid, water, height, priority = 0):
        self.style = style
        self.solid = solid
        self.water = water
        self.height = height
        self.priority = priority
    
    def additem(self, item, x, y):
        self.items[item] = (x, y)

    def draw(self, x, y, camerax, cameray):
        pygame.draw.rect(screen, TILE_COLORS[self.style], (x-camerax-self.height, y-cameray-self.height, BLOCKPIXELS, BLOCKPIXELS))
        self.drawsides(x, y, camerax, cameray, 10)

    def drawsides(self, x, y, camerax, cameray, length):
        color = mixcolors(TILE_COLORS[self.style], BLACK)
        pygame.draw.polygon(screen, color, ((x-camerax-self.height+BLOCKPIXELS, y-cameray-self.height), #TOP RIGHT of tile
                            (x-camerax-self.height+BLOCKPIXELS+length, y-cameray-self.height+length), 
                            (x-camerax-self.height+BLOCKPIXELS+length, y-cameray-self.height+BLOCKPIXELS+length),
                            (x-camerax-self.height+length, y-cameray-self.height+BLOCKPIXELS+length),
                            (x-camerax-self.height, y-cameray-self.height+BLOCKPIXELS),
                            (x-camerax-self.height+BLOCKPIXELS, y-cameray-self.height+BLOCKPIXELS)
                        ))
        

class Item:

    def __init__(self, style, radius):
        self.style = style
        self.radius = radius
        self.active = True

    def draw(self, x, y, camerax, cameray):
        pygame.draw.rect(screen, ITEM_COLORS[self.style], (x-camerax-self.radius//2, y-cameray-self.radius//2, self.radius, self.radius))

r = Rat(100, 50)
m = Map(30, 30)
m.corridor(5, 20, 0, -1, 15, 5, 2)
m.corridor(5, 5, 1, 0, 12, 5, 2)
m.corridor(17, 5, 0, 1, 6, 5, 2)
a = Item("Apple", 3)
m.additem(a, 250, 350)

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

    m.update()
    r.update(m)
    camerax = r.x - WIDTH//2
    cameray = r.y - HEIGHT//2
    screen.fill(BLACK)
    m.draw(camerax, cameray, r)
    r.drawhealthbar(WIDTH-110, HEIGHT-30)

    pygame.display.flip()       

pygame.quit()
