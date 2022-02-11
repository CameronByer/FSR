import pygame
from Entity import Entity

class Enemy(Entity):
    def __init__(self, style, x, y, sizex, sizey, maxspeed):
        image = ENEMY_BANK[style]
        image = pygame.transform.scale(ENEMY_BANK[style], (sizex, sizey))
        Entity.__init__(self, x, y, sizex, sizey, image, maxspeed)
        self.style = style
        self.targetx = x
        self.targety = y
    def update(self, worldmap, rat):
        raise NotImplementedError()

class SewerOoze(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, "Sewer Ooze", x, y, 24, 24, 7)
    def update(self, worldmap, rat):
        if self.isvisible(rat, worldmap):
            self.targetx = rat.x
            self.targety = rat.y
        speed = self.getspeed()
        self.speedx = self.targetx - self.x
        self.speedy = self.targety - self.y
        if self.insewer(worldmap):
            self.tempmaxspeed = self.maxspeed*2
        if speed != 0 and speed > self.tempmaxspeed:
            self.setspeed(self.tempmaxspeed)
        Entity.update(self, worldmap)

class RedOoze(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, "Red Ooze", x, y, 24, 24, 10)
    def update(self, worldmap, rat):
        if self.isvisible(rat, worldmap):
            self.targetx = rat.x
            self.targety = rat.y
        speed = self.getspeed()
        self.speedx = self.targetx - self.x
        self.speedy = self.targety - self.y
        if self.insewer(worldmap):
            self.tempmaxspeed = self.maxspeed/2
        if speed != 0 and speed > self.tempmaxspeed:
            self.setspeed(self.tempmaxspeed)
        Entity.update(self, worldmap)

ENEMY_LIST = {"Red Ooze": RedOoze, "Sewer Ooze": SewerOoze}
ENEMY_BANK = {enemy : pygame.image.load("Enemies\\"+enemy.replace(" ", "_")+".png").convert_alpha() for enemy in ENEMY_LIST}
