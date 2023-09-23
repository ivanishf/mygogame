import pygame

class Button():
    def __init__(self):
        pass

    def display(self, screen):
        screen.blit(self.surface, (self.x, self.y))