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
        Entity.update(self, worldmap)

class Ooze(Enemy):
    def __init__(self, style, x, y, sizex, sizey, landspeed, sewerspeed):
        Enemy.__init__(self, style, x, y, sizex, sizey, landspeed)
        self.sewerspeed = sewerspeed
    def update(self, worldmap, rat):
        ratx, raty = rat.getcenter()
        if self.isvisible(ratx, raty, worldmap):
            self.targetx = ratx
            self.targety = raty
        speed = self.getspeed()
        self.speedx = self.targetx - self.x
        self.speedy = self.targety - self.y
        if self.insewer(worldmap):
            self.tempmaxspeed = self.sewerspeed
        if speed != 0 and speed > self.tempmaxspeed:
            self.setspeed(self.tempmaxspeed)
        Enemy.update(self, worldmap, rat)

class RedOoze(Ooze):
    def __init__(self, x, y):
        Ooze.__init__(self, "Red Ooze", x, y, 24, 24, 10, 8)
class SewerOoze(Ooze):
    def __init__(self, x, y):
        Ooze.__init__(self, "Sewer Ooze", x, y, 24, 24, 7, 14)

ENEMY_LIST = {"Red Ooze": RedOoze, "Sewer Ooze": SewerOoze}
ENEMY_BANK = {enemy : pygame.image.load("Enemies\\"+enemy.replace(" ", "_")+".png").convert_alpha() for enemy in ENEMY_LIST}
