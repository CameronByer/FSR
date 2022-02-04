import pygame
from Entity import Entity

class Item:
    def __init__(self, style):
        self.style = style
        self.image = ITEM_BANK[style]
    def draw(self, x, y, sizex, sizey):
        image = pygame.transform.scale(self.image, (sizex, sizey))
        screen.blit(image, (x, y))
    def drop(self, x, y, sizex, sizey):
        return WorldItem(self.style, x, y, sizex, sizey)
    def use(self, player):
        raise NotImplementedError()

class WorldItem(Entity):
    def __init__(self, style, x, y, sizex, sizey):
        self.style = style
        image = ITEM_BANK[style]
        image = pygame.transform.scale(image, (sizex, sizey))
        Entity.__init__(self, x, y, sizex, sizey, image)


class Apple(Item):
    def __init__(self):
        Item.__init__(self, "Apple")
    def use(self, player):
        if self.style == "Apple":
            player.heal(25)
            return True
        return False
class Banana(Item):
    def __init__(self):
        Item.__init__(self, "Banana")
    def use(self, player):
        if self.style == "Banana":
            player.heal(50)
            return False
        return False

pygame.init()
screen = pygame.display.set_mode((1, 1))
ITEM_LIST = {"Apple":Apple, "Banana":Banana}
ITEM_BANK = {item : pygame.image.load("Items\\"+item+".png").convert_alpha() for item in ITEM_LIST}
