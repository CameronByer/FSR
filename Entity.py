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

    def draw(self, screen, camerax, cameray):
        if self.active:
            screen.blit(self.image, (self.x-camerax, self.y-cameray))

    def getspeed(self): # Feet per second
        return (self.speedx**2+self.speedy**2)**0.5

    def setspeed(self, speed): # Feet per second
        curspeed = self.getspeed()
        if curspeed != 0:
            self.speedx *= speed/curspeed
            self.speedy *= speed/curspeed

    def update(self):
        if self.getspeed() >= self.tempmaxspeed:
            self.setspeed(self.tempmaxspeed)
        self.x += xmovement
        self.y += ymovement
        self.tempmaxspeed = self.maxspeed
