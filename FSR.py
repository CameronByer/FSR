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

POISON = 10 #DMG/SEC

BLOCKPIXELS = 32
BLOCKFEET = 3

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FSR")
clock = pygame.time.Clock() ## For syncing the FPS

ITEM_LIST = ["Apple"]
ITEM_BANK = {item : pygame.image.load("Items\\"+item+".png").convert_alpha() for item in ITEM_LIST}

class Rat:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.maxhealth = 100
        self.speedx = 0
        self.speedy = 0
        self.maxspeed = 12
        self.tempmaxspeed = self.maxspeed
        self.radius = 8
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

    def draw(self, camerax, cameray):
        pygame.draw.circle(screen, BROWN, (self.x-camerax, self.y-cameray), self.radius)
        self.drawhealthbar(WIDTH-110, HEIGHT-30)

    def drawhealthbar(self, x, y, width=100, height=20, border=3):
        pygame.draw.rect(screen, BLACK, (x, y, width, height))
        percentpoison = min(1, self.poison/self.maxpoison)
        pygame.draw.rect(screen, PURPLE, (x+width-percentpoison*width, y, percentpoison*width, height))
        
        pygame.draw.rect(screen, GREEN, (x+border, y+border, width-border*2, height-border*2))
        percentmissing = (self.maxhealth-self.health)/self.maxhealth
        missingwidth = percentmissing * (width-2*border)
        pygame.draw.rect(screen, RED, (x+border, y+border, missingwidth, height-border*2))
    
    def update(self, m):
        if self.getspeed() >= self.tempmaxspeed:
            self.setspeed(self.tempmaxspeed)
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

        self.tempmaxspeed = self.maxspeed
        
        if self.poison > 0:
            self.poison -= 1
            self.tempmaxspeed = self.maxspeed * (2-(self.poison/self.maxpoison))/3
            
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
        self.items = {}
        self.generate()

    def additem(self, item, x, y):
        self.items[item] = (x, y)

    def draw(self, camerax, cameray):
        for x in range(self.sizex):
            for y in range(self.sizey):
                self.tiles[x][y].draw(x*BLOCKPIXELS, y*BLOCKPIXELS, camerax, cameray)
        for item, pos in self.items.items():
            item.draw(pos[0], pos[1], camerax, cameray)
            
    def gencorridor(self, x, y, dirx, diry, length, radius, water_radius):
        for i in range(length+2*radius+1):
            relx = x + dirx*(i-radius)
            rely = y + diry*(i-radius)
            for j in range(radius+1):
                if j<water_radius and i>radius-water_radius and i<(length+2*radius-(radius-water_radius)):
                    tile1 = Tile("Sewer", False, True, 3)
                    tile2 = Tile("Sewer", False, True, 3)
                elif j<radius and i>0 and i<length+2*radius:
                    tile1 = Tile("Stone", False, False, 2)
                    tile2 = Tile("Stone", False, False, 2)
                else:
                    tile1 = Tile("Wall", True, False, 1)
                    tile2 = Tile("Wall", True, False, 1)
                self.placetile(tile1, relx+diry*j, rely+dirx*j)
                self.placetile(tile2, relx-diry*j, rely-dirx*j)

    def generate(self):
        self.tiles = [[Tile("Void", True, False) for y in range(self.sizey)] for x in range(self.sizex)]
        mainsewer = 8
        maincorridor = 12
        if self.sizex >= self.sizey:
            variance = self.sizex//10
            midx = self.sizex//2
            startx = random.randint(midx-variance, midx+variance)
            starty = 0
            dx = 0
            dy = 1
            length = self.sizex
            self.spawnx = (startx-(maincorridor+mainsewer)/2+1)*BLOCKPIXELS
            self.spawny = 100
        else:
            variance = self.sizey//10
            midy = self.sizey//2
            startx = 0
            starty = random.randint(midy-variance, midy+variance)
            dx = 1
            dy = 0
            length = self.sizey
            self.spawnx = 100
            self.spawny = (starty-(maincorridor+mainsewer)/2+1)*BLOCKPIXELS
        self.gencorridor(startx, starty, dx, dy, length, maincorridor, mainsewer)
        

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

    def placetile(self, tile, x, y):
        if x>=0 and x<self.sizex and y>=0 and y<self.sizey:
            if tile.priority >= self.tiles[x][y].priority:
                self.tiles[x][y] = tile

    def update(self):
        self.items = {item: pos for item, pos in self.items.items() if item.active}
            

class Tile:

    def __init__(self, style, solid, water, priority = 0):
        self.style = style
        self.solid = solid
        self.water = water
        self.priority = priority
    
    def additem(self, item, x, y):
        self.items[item] = (x, y)

    def draw(self, x, y, camerax, cameray):
        pygame.draw.rect(screen, TILE_COLORS[self.style], (x-camerax, y-cameray, BLOCKPIXELS, BLOCKPIXELS))

class Item:

    def __init__(self, style, radius):
        self.style = style
        self.radius = radius
        self.active = True
        self.image = pygame.transform.scale(ITEM_BANK[style], (radius*2, radius*2))
        self.image.set_colorkey(WHITE)

    def draw(self, x, y, camerax, cameray):
        screen.blit(self.image, (x-camerax-self.radius, y-cameray-self.radius))

m = Map(40, 70)
r = Rat(m.spawnx, m.spawny)
a = Item("Apple", 7)
m.additem(a, m.spawnx+100, m.spawny)

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
    m.draw(camerax, cameray)
    r.draw(camerax, cameray)

    pygame.display.flip()       

pygame.quit()
