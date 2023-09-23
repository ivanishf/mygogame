import json
from typing import Type

from character import Character
from utils import *

charas = []
level = getfile("levels/1.json")
for chara in level["charas"]:
    charafile= getfile("charas/"+chara+".json")
    charas.append(Character.dict2Cha(Type[Character],charafile))
print(charas[0].name)