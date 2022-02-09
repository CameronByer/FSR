import math
import Tools

FPS = 60
BLOCKPIXELS = 32
BLOCKFEET = 3

class Entity:

    def __init__(self, x, y, sizex, sizey, image, maxspeed=0):
        self.x = x
        self.y = y
        self.sizex = sizex
        self.sizey = sizey
        self.speedx = 0
        self.speedy = 0
        self.image = image
        self.maxspeed = maxspeed
        self.tempmaxspeed = maxspeed
        self.active = True

    def iscollision(self, other):
        if self.x >= other.x+other.sizex:
            return False
        if self.y >= other.y+other.sizey:
            return False
        if self.x+self.sizex <= other.x:
            return False
        if self.y+self.sizey <= other.y:
            return False
        return True

    def isvisible(self, other, worldmap):
        line = Tools.Line((self.x, self.y), (other.x, other.y))
        sightline = []
        xrange = list(range(math.floor(min(self.x, other.x)//32), math.ceil(max(self.x, other.x)//32)+1))
        yrange = list(range(math.floor(min(self.y, other.y)//32), math.ceil(max(self.y, other.y)//32)+1))
        if line.slope == None:
            x = self.x // 32
            for y in yrange:
                if worldmap.tiles[x][y].solid:
                    return False
            return True
        if line.slope < 0:
            yrange.reverse()
        y = yrange[0]
        for x in xrange:
            if worldmap.tiles[x][y].solid:
                return False
            while line.getx(y) < x:
                y += 1
                if worldmap.tiles[x][y].solid:
                    return False
        return True     

    def getcollisions(self, entitylist):
        return [entity for entity in entitylist if self.iscollision(entity)]

    def gettilecollisions(self, worldmap, offx=0, offy=0):
        collisions = []
        for i in range(int(self.x+offx)//BLOCKPIXELS, int(self.x+self.sizex-1+offx)//BLOCKPIXELS+1):
            for j in range(int(self.y+offy)//BLOCKPIXELS, int(self.y+self.sizey-1+offy)//BLOCKPIXELS+1):
                collisions.append(worldmap.tiles[i][j])
        return collisions

    def draw(self, screen, camerax, cameray):
        if self.active:
            screen.blit(self.image, (self.x-camerax, self.y-cameray))

    def insewer(self, worldmap):
        for tile in self.gettilecollisions(worldmap):
            if tile.style == "Sewer":
                return True
        return False

    def getspeed(self): # Feet per second
        return (self.speedx**2+self.speedy**2)**0.5

    def setspeed(self, speed): # Feet per second
        curspeed = self.getspeed()
        if curspeed != 0:
            self.speedx *= speed/curspeed
            self.speedy *= speed/curspeed

    def update(self, worldmap):
        if self.getspeed() >= self.tempmaxspeed:
            self.setspeed(self.tempmaxspeed)
        xmovement = self.speedx/FPS * BLOCKPIXELS/BLOCKFEET
        ymovement = self.speedy/FPS * BLOCKPIXELS/BLOCKFEET
        if any(tile.solid for tile in self.gettilecollisions(worldmap, xmovement, ymovement)):
            if any(tile.solid for tile in self.gettilecollisions(worldmap, xmovement, 0)):
                xmovement = 0
                if any(tile.solid for tile in self.gettilecollisions(worldmap, 0, ymovement)):
                    ymovement = 0
            else:
                ymovement = 0
        self.x += xmovement
        self.y += ymovement

        self.tempmaxspeed = self.maxspeed
