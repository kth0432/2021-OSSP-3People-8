import shooting_game
import sprites

scr_size = 500

if __name__ == '__main__':
    while(True):
        sprites.get_size(scr_size)
        if scr_size == 0 :
            break
        scr_size = shooting_game.main(scr_size)