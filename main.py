import shooting_game
import sprites
import pygame
import sys
import mode_one
import mode_two
import time

user_size = 200     # 사용자 지정 화면 크기
level_size = 2      # 값이 커지면 이미지가 작게 보임
scr_size = user_size * level_size
id = ''

mode1_lvl_size = 1
mode2_lvl_size = 1.6

if __name__ == '__main__':
    while(True):
        print(id)
        if scr_size <= 300 :
            if scr_size == 0 :
                pygame.quit()
                sys.exit()
            scr_size = 300

        user_size = round(scr_size / level_size)
        sprites.get_size(user_size, level_size)
        time.sleep(0.1) # 과도한 리사이즈(초당 60번)를 하지 않도록 함

        if level_size == mode1_lvl_size :
            scr_size, level_size, id = mode_one.main(scr_size, level_size, id)

        elif level_size == mode2_lvl_size :
            scr_size, level_size, id = mode_two.main(scr_size, level_size, id)

        else :
            scr_size, level_size, id = shooting_game.main(scr_size, level_size, id)
