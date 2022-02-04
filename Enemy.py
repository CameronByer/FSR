import pygame
from Entity import Entity

class Enemy(Entity):
    def __init__(self, style, x, y, sizex, sizey, maxspeed):
        image = ENEMY_BANK[style]
        image = pygame.transform.scale(ENEMY_BANK[style], (sizex, sizey))
        Entity.__init__(self, x, y, sizex, sizey, image, maxspeed)
        self.style = style
    def update(self, worldmap, rat):
        raise NotImplementedError()

class SewerOoze(Enemy):
    def __init__(self, x, y):
        Enemy.__init__(self, "Sewer Ooze", x, y, 24, 24, 8)
    def update(self, worldmap, rat):
        self.speedx = rat.x - self.x
        self.speedy = rat.y - self.y
        if self.getspeed() != 0:
            self.setspeed(self.tempmaxspeed)
        Entity.update(self, worldmap)
        if self.insewer(worldmap):
            self.tempmaxspeed = self.maxspeed*2

ENEMY_LIST = {"Sewer Ooze": SewerOoze}
ENEMY_BANK = {enemy : pygame.image.load("Enemies\\"+enemy.replace(" ", "_")+".png").convert_alpha() for enemy in ENEMY_LIST}
