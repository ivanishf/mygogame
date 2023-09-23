import pygame
import json


class Character:
    def __init__(self, name):
        self.name = name

    def dict2Cha(self,charas):
        Chara = Character(charas["name"])
        return Chara
