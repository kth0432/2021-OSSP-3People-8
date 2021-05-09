import shooting_game
import sprites

user_size = 200     # 사용자 지정 화면 크기
level_size = 2      # 
scr_size = user_size * level_size

if __name__ == '__main__':
    while(True):
        if scr_size == 0 :
            pygame.quit()
            sys.exit()
        user_size = round(scr_size / level_size)
        scr_size = user_size * level_size
        sprites.get_size(user_size, level_size)
        scr_size, level_size = shooting_game.main(scr_size, level_size)