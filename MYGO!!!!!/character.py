import pygame
import json


class Character:
    def __init__(self, name, imgpath):
        self.name = name
        self.img = pygame.image.load(imgpath)

    @staticmethod
    def dict2cha(charas):
        Chara = Character(charas["name"],
                          charas["img"])
        return Chara
