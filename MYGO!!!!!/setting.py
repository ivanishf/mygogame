GAME_TITLE = 'MYGO三消'
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BUTTON_WIDTH = 190
BUTTON_HEIGHT = 50


def inarea(x, y, tarx, tary, width, height):
    if (tarx <= x <= tarx + width and tary <= y <= tary + height):
        return True
    return False
