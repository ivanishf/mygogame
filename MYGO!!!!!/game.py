from typing import Type, List

import pygame
import random
import math
from enum import IntEnum

from character import Character
from utils import *


class Game:
    FEILD_X = 60  # 412
    FEILD_Y = 40  # 348
    CUBE_WIDTH = 44
    CUBE_HEIGHT = 44
    SKILL_AREA_X = 160
    SKILL_AREA_Y = 500
    SKILL_WIDTH = 60
    SKILL_HEIGHT = 60
    FIELD_DROPING = 1  # 是否有物品下落
    FIELD_DROPING_STEP = 1  # 是否在处理物品下落
    FIELD_AFTER_SWAP = 1
    TRY_TO_SWAP = 0
    GAME_LOOP = 1
    FPS = 30
    GLOBAL_TIME = 0
    DELTA = 0
    SWAPPING = 0
    SHOW_SWAP = 0
    SWAP_SPEED = 4
    DROP_SPEED = 11
    USING_SKILL = 0
    MOUSEDOWN=False

    def __init__(self, screen, charas: List[Character]):
        self.screen = screen
        self.field = [[0 for y in range(8)] for x in range(8)]
        self.drop_list = []
        self.swap_list = []
        self.bg_win = pygame.image.load('images/bg/bg_win.png')
        self.distance = 0
        self.clock = pygame.time.Clock()
        self.swap_source = (0, 0)
        self.swap_dest = (0, 0)
        self.charas =charas
        # TBC
        self.cube_empty = pygame.image.load('images/bg/background_cube.png')
        self.cube_map = {0: self.cube_empty}
        for i in range(len(self.charas)):
            self.cube_map[i + 1] = charas[i].img

    def init_field(self):
        """
        初始化游戏场地
        :return:
        """
        while self.FIELD_DROPING:
            self.generate()
            self.gravity()
            self.draw()
        self.after_swap()

    def generate(self):
        """
        在第0行空块处生成新元素
        :return:
        """
        for i in range(len(self.field[0])):
            if self.field[0][i] == self.CubeType.EMPTY:  # TBC
                self.field[0][i] = random.randint(1, len(self.charas))

    def gravity(self):
        """
        遍历棋盘，若元素下方为空，将该元素加入下移列表，调用drop_anime播放下坠动画
        :return:
        """
        for i in range(6, -1, -1):  # 从倒数第二行开始
            for j in range(0, 8):
                if self.field[i + 1][j] == self.CubeType.EMPTY and self.field[i][j] != self.CubeType.EMPTY:
                    self.drop_list.append((i, j))
        # 如果掉落列表为空，停止掉落
        if len(self.drop_list) == 0:
            self.FIELD_DROPING = 0
        else:
            self.FIELD_DROPING_STEP = 1
            self.all_anime()
            for i, j in self.drop_list:
                self.field[i][j], self.field[i + 1][j] = self.field[i + 1][j], self.field[i][j]
            self.drop_list.clear()

    def pos_to_num(self, mx, my):
        i = (my - self.FEILD_Y) // self.CUBE_HEIGHT
        j = (mx - self.FEILD_X) // self.CUBE_WIDTH
        return i, j

    def swap(self):
        # i1 = (self.swap_source[1] - self.FEILD_Y) // self.CUBE_HEIGHT
        # j1 = (self.swap_source[0] - self.FEILD_X) // self.CUBE_WIDTH
        # i2 = (self.swap_dest[1] - self.FEILD_Y) // self.CUBE_HEIGHT
        # j2 = (self.swap_dest[0] - self.FEILD_X) // self.CUBE_WIDTH
        i1, j1 = self.pos_to_num(self.swap_source[0], self.swap_source[1])
        i2, j2 = self.pos_to_num(self.swap_dest[0], self.swap_dest[1])
        if i1 == i2:
            if j1 - j2 != 1:
                if j2 - j1 != 1:
                    return 0
        elif j1 == j2:
            if i1 - i2 != 1:
                if i2 - i1 != 1:
                    return 0
        else:
            return 0
        self.field[i1][j1], self.field[i2][j2] = self.field[i2][j2], self.field[i1][j1]
        self.TRY_TO_SWAP = 1
        self.match()
        self.field[i1][j1], self.field[i2][j2] = self.field[i2][j2], self.field[i1][j1]
        if self.TRY_TO_SWAP:
            self.swap_list.append((i1, j1))
            self.swap_list.append((i2, j2))
            self.SHOW_SWAP = 1
            self.all_anime()
            self.field[i1][j1], self.field[i2][j2] = self.field[i2][j2], self.field[i1][j1]
            self.TRY_TO_SWAP = 0
            return 1
        else:
            return 0

    def after_swap(self, mode=0):
        self.FIELD_AFTER_SWAP = 1
        while self.FIELD_AFTER_SWAP:
            self.FIELD_DROPING = 1
            while self.FIELD_DROPING:
                self.generate()
                self.gravity()
            self.draw()
            self.match()

        if mode:
            pass  # 加分与技能效果

    def all_anime(self):
        while self.FIELD_DROPING_STEP:
            self.draw()
        while self.SHOW_SWAP:
            self.draw()

    def draw(self):
        """
        画图，先画背景，再画未动元素，再画下落元素与消除元素
        :return:
        """
        self.draw_background()
        for i in range(1, 8):
            for j in range(0, 8):
                if (i, j) not in self.drop_list:
                    if (i, j) not in self.swap_list:
                        cube = self.cube_map[self.field[i][j]]
                        self.screen.blit(cube,
                                         (self.FEILD_X + j * self.CUBE_WIDTH, self.FEILD_Y + i * self.CUBE_HEIGHT))
        if self.FIELD_DROPING_STEP:
            self.drop_anime()
        if self.SHOW_SWAP:
            self.swap_anime(self.swap_list[0][0], self.swap_list[0][1], self.swap_list[1][0], self.swap_list[1][1])
        pygame.display.update()

    def match(self):
        match_list = []
        damage_sum = [0, 0]
        # 1.横向匹配

        for i in range(1, 8):
            row_match = []
            for j in range(0, 8):
                if len(row_match) == 0:
                    row_match.append((i, j))
                else:  # 与匹配列表最后一项进行比较
                    row_match_last_i, row_match_last_j = row_match[-1][0], row_match[-1][1]
                    if self.field[i][j] == self.field[row_match_last_i][row_match_last_j]:
                        row_match.append((i, j))
                    else:  # self.field[i][j]  !=  self.field[row_match_last_i][row_match_last_j]
                        # 若匹配列表中项数大于3，则将这些元素添加到匹配列表大全，然后清空，否则直接清空
                        if len(row_match) >= 3:
                            match_list.extend(row_match)
                            level = len(row_match) - 2
                            cube_type = self.field[row_match_last_i][row_match_last_j]
                            # TBC skill检查
                            row_match.clear()
                        else:
                            row_match.clear()
                            row_match.append((i, j))
            if len(row_match) >= 3:
                match_list.extend(row_match)

        # 2.纵向匹配
        for j in [0, 1, 2, 3, 4, 5, 6, 7]:
            col_match = []
            for i in [1, 2, 3, 4, 5, 6, 7]:
                if len(col_match) == 0:
                    col_match.append((i, j))
                else:  # 与匹配列表最后一项进行比较
                    col_match_last_i, col_match_last_j = col_match[-1][0], col_match[-1][1]
                    if self.field[i][j] == self.field[col_match_last_i][col_match_last_j]:
                        col_match.append((i, j))
                    else:  # self.field[i][j]  !=  self.field[col_match_last_i][col_match_last_j]
                        # 若匹配列表中项数大于3，则将这些元素添加到匹配列表大全，然后清空，否则清空再添加自己
                        if len(col_match) >= 3:
                            match_list.extend(col_match)
                            level = len(col_match) - 2
                            cube_type = self.field[col_match_last_i][col_match_last_j]
                            # TBC skill检查
                            col_match.clear()
                        else:
                            col_match.clear()
                            col_match.append((i, j))
            if len(col_match) >= 3:
                match_list.extend(col_match)

        if self.TRY_TO_SWAP == 0:
            self.match_logical_anime(match_list)
        if len(match_list) == 0:
            self.FIELD_AFTER_SWAP = 0
            self.TRY_TO_SWAP = 0

    def drop_anime(self):
        """
        将下移列表的中的元素全部下移
        :return:
        """
        start_time = self.GLOBAL_TIME
        self.clock_tick()
        self.distance += self.DROP_SPEED
        # 绘制动画中的方块
        for i, j in self.drop_list:
            cube = self.cube_map[self.field[i][j]]
            self.screen.blit(cube,
                             (self.FEILD_X + j * self.CUBE_WIDTH, self.FEILD_Y + i * self.CUBE_HEIGHT + self.distance))
        if self.distance >= self.CUBE_HEIGHT:
            self.FIELD_DROPING_STEP = 0
            self.distance = 0

    def swap_anime(self, i1, j1, i2, j2):
        self.clock_tick()
        self.distance += self.SWAP_SPEED
        # 绘制动画中的方块
        cube1 = self.cube_map[self.field[i1][j1]]
        cube2 = self.cube_map[self.field[i2][j2]]
        self.screen.blit(cube2, (self.FEILD_X + j2 * self.CUBE_WIDTH + (j1 - j2) * self.distance
                                 , self.FEILD_Y + i2 * self.CUBE_HEIGHT + (i1 - i2) * self.distance))
        self.screen.blit(cube1, (self.FEILD_X + j1 * self.CUBE_WIDTH + (j2 - j1) * self.distance
                                 , self.FEILD_Y + i1 * self.CUBE_HEIGHT + (i2 - i1) * self.distance))
        if self.distance >= self.CUBE_HEIGHT:
            self.SHOW_SWAP = 0
            self.swap_list.clear()
            self.distance = 0

    def draw_background(self):
        self.screen.fill((255, 255, 255))
        # 敌人
        # enemy_hp = self.enemy.stat.hp
        # pygame.draw.rect(self.screen, (255, 120, 120), (765-self.enemy.stat.max_hp, 20, self.enemy.stat.max_hp, 30))
        # pygame.draw.rect(self.screen, (255, 0, 0), (765-enemy_hp, 20, enemy_hp, 30))
        # self.screen.blit(self.enemy.enemy_img, (430, 60))
        # 玩家
        # player_hp, player_mp = self.player.stat.hp, self.player.stat.mp
        # pygame.draw.rect(self.screen, (255, 0, 0), (160, 440, player_hp, 20))
        # pygame.draw.rect(self.screen, (0, 0, 255), (160, 460, player_mp, 20))
        # self.screen.blit(self.player.profile_img, (30, 440))
        # i = 0
        # for skill_index in self.player.stat.skillset:
        #     skill = self.player.skill_map[skill_index]
        #     self.screen.blit(skill, (self.SKILL_AREA_X+i*90, self.SKILL_AREA_Y))
        #     i += 1

    def match_logical_anime(self, match_list_all):
        for elems in match_list_all:
            i, j = elems[0], elems[1]
            self.field[i][j] = 0
        self.draw()

    def run(self):
        """
        runrunrun
        :return:
        """
        self.init_field()
        while True:
            # 结束条件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.MOUSEDOWN=True
                    prex, prey = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONUP:
                    mx, my = pygame.mouse.get_pos()
                    if (self.FEILD_X <= mx <= self.FEILD_X + 8 * self.CUBE_WIDTH and
                            self.FEILD_Y + self.CUBE_HEIGHT <= my <= self.FEILD_Y + 8 * self.CUBE_HEIGHT):
                        if self.USING_SKILL:  # TBC USINGitem
                            self.USING_SKILL = 0
                            self.after_swap(1)
                        elif self.SWAPPING == 0:
                            self.swap_source = (mx, my)
                            self.SWAPPING = 1
                            print('click another')
                        elif self.SWAPPING == 1:
                            if True:
                                print('swaping')
                                self.swap_dest = (mx, my)
                                swapnum = self.swap()
                                self.after_swap(swapnum)
                                self.SWAPPING = 0
                    else:
                        print('cancel swap')
                        self.SWAPPING = 0
                        self.USING_SKILL = 0
                        # self.skill_blocks.clear()
                        # self.skill_block_num = 0
                        if (self.SKILL_AREA_X <= mx <= self.SKILL_AREA_X + 330 and
                                self.SKILL_AREA_Y <= my <= self.SKILL_AREA_Y + self.SKILL_HEIGHT):
                            skill_chosen = (mx - self.SKILL_AREA_X) // 90
                            # if (mx - self.SKILL_AREA_X - skill_chosen * 90) <= 60:
                            #     print(skill_chosen)
                            #     self.USING_SKILL = skill_chosen + 1
                            #     self.skill_block_num = self.player.skill_index(self.field, skill_chosen)
                            #     if self.skill_block_num == 0:
                            #         self.USING_SKILL = 0
                            #         self.after_swap(1)
                            #     elif self.skill_block_num == -1:
                            #         self.USING_SKILL = 0
                        # TBC if in menu area
                if event.type == pygame.QUIT:
                    exit()

    def clock_tick(self):
        self.clock.tick(self.FPS)
        self.GLOBAL_TIME += self.DELTA / 1000

    class CubeType(IntEnum):
        # TBC
        EMPTY = 0
        PHYSICAL_ATTACK = 1
        MAGIC_ATTACK = 2
        HP_POTION = 3
        MP_POTION = 4
        BLOCKS = 5
        PHYSICAL_ATTACK_PRO = 6
        MAGIC_ATTACK_PRO = 7
        HP_POTION_PRO = 8
        MP_POTION_PRO = 9
        ONE = 10


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    charas = []
    level = getfile("levels/2.json")
    for chara in level["charas"]:
        charafile = getfile("charas/" + chara + ".json")
        charas.append(Character.dict2cha(charafile))
    game = Game(screen, charas)
    game.run()
