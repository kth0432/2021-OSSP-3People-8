from shooting_game import *
from sprites import *

scr_x, scr_y = 500, 500

if __name__ == '__main__':
    while(True):
        get_size(scr_x, scr_y)
        scr_x, scr_y = main(scr_x, scr_y)