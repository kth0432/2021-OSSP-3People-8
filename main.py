import shooting_game
import sprites

user_size = 200
level_size = 2
scr_size = user_size * level_size

if __name__ == '__main__':
    while(True):
        if scr_size == 0 :
            break
        user_size = round(scr_size / level_size)
        scr_size = user_size * level_size
        sprites.get_size(user_size, level_size)
        scr_size, level_size = shooting_game.main(scr_size, level_size)