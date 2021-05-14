import shooting_game
import sprites
import pygame
import sys
import mode_one
import mode_two

user_size = 200     # 사용자 지정 화면 크기
level_size = 2      # 값이 커지면 이미지가 작게 보임
scr_size = user_size * level_size
id = ''

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

        if level_size == 1 :
            scr_size, level_size = mode_one.main(scr_size, level_size)

        elif level_size == 1.6 :
            scr_size, level_size = mode_two.main(scr_size, level_size)

        else :
            scr_size, level_size, id = shooting_game.main(scr_size, level_size, id)