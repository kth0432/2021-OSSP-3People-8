from os import kill
import pygame
import random
from collections import deque
import sys
import grequests
import time

import sprites
from sprites import (MasterSprite, Ship2, Ship3, Alien, Missile, BombPowerup, DistPowerup,
                     ShieldPowerup, DoublemissilePowerup, Explosion, Siney, Spikey, Fasty,
                     Roundy, Crawly)
from database import Database
from load import load_image, load_sound, load_music

if not pygame.mixer:
    print('Warning, sound disabled')
if not pygame.font:
    print('Warning, fonts disabled')


# BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK= (0, 0, 0)
WHITE= (255, 255, 255)
GREEN= (0, 255, 0)
YELLOW = (255, 255, 0)

url = "http://osspcshooting.shop"

class Button:
    def __init__(self, gameDisplay, img_in, x, y, width, height, img_act, x_act, y_act, action = None):
        self.lvl_size = 0
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x + width > mouse[0] > x and y + height > mouse[1] > y:
            gameDisplay.blit(img_act,(x_act, y_act))
            if click[0] and action == 'quitgame':
                pygame.quit()
                sys.exit()
            elif click[0] and action == 'mode_one':
                self.lvl_size = -1

            elif click[0] and action == 'shooting_game':
                self.lvl_size = -2
        else:
            gameDisplay.blit(img_in,(x,y))


class Keyboard(object):
    keys = {pygame.K_a: 'A', pygame.K_b: 'B', pygame.K_c: 'C', pygame.K_d: 'D',
            pygame.K_e: 'E', pygame.K_f: 'F', pygame.K_g: 'G', pygame.K_h: 'H',
            pygame.K_i: 'I', pygame.K_j: 'J', pygame.K_k: 'K', pygame.K_l: 'L',
            pygame.K_m: 'M', pygame.K_n: 'N', pygame.K_o: 'O', pygame.K_p: 'P',
            pygame.K_q: 'Q', pygame.K_r: 'R', pygame.K_s: 'S', pygame.K_t: 'T',
            pygame.K_u: 'U', pygame.K_v: 'V', pygame.K_w: 'W', pygame.K_x: 'X',
            pygame.K_y: 'Y', pygame.K_z: 'Z'}

def main(scr, level, id, language):
    scr_size, level_size = scr, level
    user_size = round(scr_size / level_size)
    id = id
    language = language
    main_lvl_size = 2
    mode1_lvl_size = 3
    mode2_lvl_size = 1.6

    class size :
        x_background_ratio = 2
        x_background = scr_size*x_background_ratio
        speed = scr_size*0.004
        background = scr_size*4
        backgroundLoc = scr_size*3
        star_seq = round(scr_size*0.06)
        star_s = round(scr_size*0.004)
        star_l = round(scr_size*0.01)
        font_eng = round(scr_size*0.065)
        font_kor =  round(scr_size*0.040)
        toppos = scr_size*0.2
        ratio = scr_size*0.002
        middletoppos = scr_size*0.35
        topendpos = scr_size*0.15
        middlepos = scr_size*0.5
        achievement = scr_size/3000
        achievementpos = scr_size*0.25
        hi_achievement = scr_size*0.0001
        hi_achievementx = scr_size*0.3
        hi_achievementx2 = scr_size*0.35
        hi_achievementy = scr_size*0.16
        hi_achievementy_seq = scr_size*0.043
        selectitemposx = scr_size*0.2
        selectitemposy = scr_size*0.5
        button1pos_1 = round(x_background*0.08)
        button2pos_1 = round(x_background*0.43)
        button3pos_1 = round(x_background*0.86)
        buttonpos_2 = round(scr_size*0.9)
        buttonpos_3 = round(scr_size*0.25)
        buttonpos_4 = round(scr_size*0.1)
        button1pos_1_ad = round(x_background*0.07)
        button2pos_1_ad = round(x_background*0.42)
        button3pos_1_ad = round(x_background*0.85)
        button_ad = round(scr_size*0.896)
        lifex = scr_size * 0.80
        lifey = scr_size * 0.01

    def set_size(scr_size) :
        size.x_background = scr_size*size.x_background_ratio
        size.speed = scr_size*0.004
        size.background = scr_size*4
        size.backgroundLoc = scr_size*3
        size.star_seq = round(scr_size*0.06)
        size.star_s = round(scr_size*0.004)
        size.star_l = round(scr_size*0.01)
        size.font_eng = round(scr_size*0.065)
        size.font_kor =  round(scr_size*0.040)
        size.toppos = scr_size*0.2
        size.ratio = scr_size*0.002
        size.middletoppos = scr_size*0.35
        size.topendpos = scr_size*0.15
        size.middlepos = size.x_background*0.5
        size.achievement = scr_size/3000
        size.achievementpos = scr_size*0.25
        size.hi_achievement = scr_size*0.0001
        size.hi_achievementx = scr_size*0.3
        size.hi_achievementx2 = scr_size*0.35
        size.hi_achievementy = scr_size*0.16
        size.hi_achievementy_seq = scr_size*0.043
        size.selectitemposx = scr_size*0.2
        size.selectitemposy = scr_size*0.5
        size.button1pos_1 = round(size.x_background*0.08)
        size.button2pos_1 = round(size.x_background*0.48)
        size.button3pos_1 = round(size.x_background*0.86)
        size.buttonpos_2 = round(scr_size*0.9)
        size.buttonpos_3 = round(scr_size*0.25)
        size.buttonpos_4 = round(scr_size*0.1)
        size.button1pos_1_ad = round(size.x_background*0.07)
        size.button2pos_1_ad = round(size.x_background*0.45)
        size.button3pos_1_ad = round(size.x_background*0.85)
        size.button_ad = round(size.x_background*0.896)
        size.lifex = scr_size * 0.80
        size.lifey = scr_size * 0.01

    def resize(x, y, level_size) :

        scr_size = min(x//size.x_background_ratio, y)
        if scr_size < 300 :
            scr_size = 300
        user_size = round(scr_size / level_size)
        set_size(scr_size)
        sprites.get_size(user_size, level_size)
        time.sleep(0.1) # 과도한 리사이즈(초당 60번)를 하지 않도록 함

        screen = pygame.display.set_mode((size.x_background, scr_size), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

        background = pygame.Surface((size.x_background, size.background))
        background = background.convert()
        background.fill(BLACK)

        backgroundLoc = size.backgroundLoc
        finalStars = deque()
        for y in range(0, size.backgroundLoc, size.star_seq):
            starsize = random.randint(size.star_s, size.star_l)
            x = random.randint(0, size.x_background - starsize)
            if y <= scr_size:
                finalStars.appendleft((x, y + size.backgroundLoc, starsize))
            pygame.draw.rect(
                background, RED, pygame.Rect(x, y, starsize, starsize))
        while finalStars:
            x, y, starsize = finalStars.pop()
            pygame.draw.rect(
                background, RED, pygame.Rect(x, y, starsize, starsize))

        font = pygame.font.Font(None, size.font_eng)
        font2 = pygame.font.SysFont('nanumgothic', size.font_kor)

        title, titleRect = load_image('title_mode2.png')
        title = pygame.transform.scale(title, (round(title.get_width()*size.ratio), round(title.get_height()*size.ratio)))
        titleRect = pygame.Rect(0, 0, title.get_width(), title.get_height())
        pause,pauseRect = load_image('pause.png',WHITE)
        pause = pygame.transform.scale(pause, (round(pause.get_width()*size.ratio), round(pause.get_height()*size.ratio)))
        pauseRect = pygame.Rect(0, 0, pause.get_width(), pause.get_height())
        titleRect.midtop = screen.get_rect().inflate(0, -size.middletoppos).midtop
        pauseRect.midtop = screen.get_rect().inflate(0, -size.middletoppos).midtop

        dist, distRect = load_image('black.png', WHITE)
        dist = pygame.transform.scale(dist, (scr_size, scr_size))
        distRect = pygame.Rect(0, 0, dist.get_width(), dist.get_height())
        distRect.midtop = screen.get_rect().inflate(0, 0).midtop

        dist2, distRect2 = load_image('black.png', WHITE)
        dist2 = pygame.transform.scale(dist2, (scr_size, scr_size))
        distRect2 = pygame.Rect(0, 0, dist2.get_width(), dist2.get_height())
        distRect2.midtop = screen.get_rect().inflate(0, 0).midtop

        text_eng_set = [font.render('START GAME', 1, WHITE),
                        font.render('SOUND FX', 1, WHITE),
                        font.render('   ON', 1, RED),
                        font.render('   OFF', 1, RED),
                        font.render('MUSIC', 1, WHITE),
                        font.render('   ON', 1, RED),
                        font.render('   OFF', 1, RED),
                        font.render('QUIT', 1, WHITE),
                        font.render('RESTART', 1, WHITE),
                        font.render('LANGUAGE', 1, WHITE),
                        font.render('GAME OVER', 1, WHITE),
                        font.render('SPEED UP!', 1, RED)]

        text_kor_set = [font2.render('게임 시작', 1, WHITE),
                        font2.render('효과음        ', 1, WHITE),
                        font2.render('켜짐      ', 1, RED),
                        font2.render('꺼짐', 1, RED),
                        font2.render('음악', 1, WHITE),
                        font2.render('켜짐', 1, RED),
                        font2.render('꺼짐', 1, RED),
                        font2.render('종료', 1, WHITE),
                        font2.render('다시 시작', 1, WHITE),
                        font2.render('언어', 1, WHITE),
                        font2.render('게임 종료', 1, WHITE),
                        font2.render('스피드 업!', 1, RED)]

        startText, fxText, fxOnText, fxOffText, musicText, musicOnText, musicOffText, quitText, restartText, languageText, gameOverText, speedUpText = set_language(language)

        startPos = startText.get_rect(midtop=titleRect.inflate(0, size.topendpos).midbottom)
        fxPos = fxText.get_rect(topleft=startPos.bottomleft)
        fxOnPos = fxOnText.get_rect(topleft=fxPos.topright)
        fxOffPos = fxOffText.get_rect(topleft=fxPos.topright)
        musicPos = fxText.get_rect(topleft=fxPos.bottomleft)
        musicOnPos = musicOnText.get_rect(topleft=musicPos.topright)
        musicOffPos = musicOffText.get_rect(topleft=musicPos.topright)
        quitPos = quitText.get_rect(topleft=musicPos.bottomleft)
        languagePos = languageText.get_rect(topleft=quitPos.bottomleft)

        selectText = font.render('> ', 1, WHITE)
        selectPos = selectText.get_rect(topright=startPos.topleft)
        restartPos = restartText.get_rect(bottomleft=fxPos.topleft)


        playerText, player2Text, bstartText, switchText = beforegame_text_update(language)
        playerPos = playerText.get_rect(topleft=screen.get_rect().topleft)
        player2Pos = player2Text.get_rect(topleft=screen.get_rect().midtop)
        bstartPos = bstartText.get_rect(center=screen.get_rect().center)
        switchPos = switchText.get_rect(midbottom=screen.get_rect().midbottom)

        menuDict = {1: startPos, 2: fxPos, 3: musicPos, 4: quitPos, 5: languagePos}

        # 버튼 구현
        mainImg = pygame.image.load("data/main.png")
        mainImg = pygame.transform.scale(mainImg, (round(mainImg.get_width()*size.ratio), round(mainImg.get_height()*size.ratio)))
        modeImg_one = pygame.image.load("data/mode1.png")
        modeImg_one = pygame.transform.scale(modeImg_one, (round(modeImg_one.get_width()*size.ratio), round(modeImg_one.get_height()*size.ratio)))
        modeImg_two = pygame.image.load("data/mode2.png")
        modeImg_two = pygame.transform.scale(modeImg_two, (round(modeImg_two.get_width()*size.ratio), round(modeImg_two.get_height()*size.ratio)))
        quitImg = pygame.image.load("data/quiticon.png")
        quitImg = pygame.transform.scale(quitImg, (round(quitImg.get_width()*size.ratio), round(quitImg.get_height()*size.ratio)))
        clickmainImg = pygame.image.load("data/mainclicked.png")
        clickmainImg = pygame.transform.scale(clickmainImg, (round(clickmainImg.get_width()*size.ratio), round(clickmainImg.get_height()*size.ratio)))
        clickmodeImg_one = pygame.image.load("data/mode1clicked.png")
        clickmodeImg_one = pygame.transform.scale(clickmodeImg_one, (round(clickmodeImg_one.get_width()*size.ratio), round(clickmodeImg_one.get_height()*size.ratio)))
        clickmodeImg_two = pygame.image.load("data/mode2clicked.png")
        clickmodeImg_two = pygame.transform.scale(clickmodeImg_two, (round(clickmodeImg_two.get_width()*size.ratio), round(clickmodeImg_two.get_height()*size.ratio)))
        clickQuitImg = pygame.image.load("data/clickedQuitIcon.png")
        clickQuitImg = pygame.transform.scale(clickQuitImg, (round(clickQuitImg.get_width()*size.ratio), round(clickQuitImg.get_height()*size.ratio)))

        return scr_size, user_size, screen, background, backgroundLoc, finalStars, font, font2, title, titleRect, pause, pauseRect, text_eng_set, text_kor_set, startPos, startText, fxPos, fxOnPos, fxOffPos, musicPos, musicOnPos, musicOffPos, quitPos, languagePos, selectText, selectPos, restartPos, menuDict, dist, distRect, dist2, distRect2, playerText, player2Text, bstartText, switchText, playerPos, player2Pos, bstartPos, switchPos

    def kill_alien(alien, aliensLeftThisWave, kill_count, score) :
        aliensLeftThisWave -= 1
        kill_count += 1
        #score differentiation by Alien color
        #wave1 aliens
        if alien.pType == 'green' or alien.pType == 'orange':
            score += 1
        #wave2 alien
        elif alien.pType == 'white':
            score += 2
        #wave3 alien
        elif alien.pType == 'red':
            score += 4
        #wave4 alien
        elif alien.pType == 'yellow':
            score += 8
        return aliensLeftThisWave, kill_count, score

    def background_update(screen, background, backgroundLoc) :
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, size.x_background, scr_size))
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = size.backgroundLoc
        return screen, background, backgroundLoc

    # 인게임에서 배경색으로 플레이어 영역 구분
    def background_update_half(screen, background, backgroundLoc) :
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, size.x_background, scr_size))
        screen.fill((80, 20, 30, 125),(0, 0, screen.get_width()//size.x_background_ratio, screen.get_height()), special_flags = 1) # special_flags = 3 : 별 색깔만 바뀜
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = size.backgroundLoc
        return screen, background, backgroundLoc

    def background_update_half_two(screen, background, backgroundLoc) :
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, size.x_background, scr_size))
        screen.fill((80, 20, 30, 125),(screen.get_width()//size.x_background_ratio, 0, screen.get_width()//size.x_background_ratio, screen.get_height()), special_flags = 1)
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = size.backgroundLoc
        return screen, background, backgroundLoc

    def set_language(lan) :
        # 언어 설정
        if language == "ENG": #기본 설정 영어
            return text_eng_set
        else :
            return text_kor_set

    def beforegame_text_update(language) :
        if language == "ENG" :
            return [font.render("PLAYER 1" , 1, WHITE),
                    font.render("PLAYER 2" , 1, WHITE),
                    font.render("START : Press U" , 1, WHITE),
                    font.render("Switch Player : Press L" , 1, WHITE)]
        else :
            return [font2.render("플레이어1" , 1, WHITE),
                    font2.render("플레이어2" , 1, WHITE),
                    font2.render("시작버튼: U키" , 1, WHITE),
                    font2.render("플레이어 위치 변경: L키 ", 1, WHITE)]

    def ingame_text_update(language) :
        if language == "ENG" :
            return [font.render("Wave: " + str(wave), 1, WHITE),
                    font.render("Aliens Left: " + str(aliensLeftThisWave), 1, WHITE),
                    font.render("Score: " + str(score), 1, WHITE),
                    font.render("Score: " + str(score2), 1, WHITE),
                    font.render("Bombs: " + str(bombsHeld), 1, WHITE),
                    font.render("Bombs: " + str(bombsHeld2), 1, WHITE),
                    font.render('PLAYER 1 WIN!', 1, WHITE),
                    font.render('PLAYER 2 WIN!', 1, WHITE),
                    font.render('DRAW!', 1, WHITE)]

        else :
            return [font2.render("웨이브: " + str(wave), 1, WHITE),
                    font2.render("남은 적: " + str(aliensLeftThisWave), 1, WHITE),
                    font2.render("점수: " + str(score), 1, WHITE),
                    font2.render("점수: " + str(score2), 1, WHITE),
                    font2.render("폭탄: " + str(bombsHeld), 1, WHITE),
                    font2.render("폭탄: " + str(bombsHeld2), 1, WHITE),
                    font2.render("플레이어 1 승!", 1, WHITE),
                    font2.render("플레이어 2 승!", 1, WHITE),
                    font2.render('무승부!', 1, WHITE)]

    direction = {None: (0, 0), pygame.K_UP: (0, -size.speed), pygame.K_DOWN: (0, size.speed),
             pygame.K_LEFT: (-size.speed, 0), pygame.K_RIGHT: (size.speed, 0)}

    direction2 = {None: (0, 0), pygame.K_w: (0, -size.speed), pygame.K_s: (0, size.speed),
             pygame.K_a: (-size.speed, 0), pygame.K_d: (size.speed, 0)}

    # Initialize everything
    pygame.mixer.pre_init(11025, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((size.x_background, scr_size), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
    pygame.display.set_caption('Shooting Game')
    pygame.mouse.set_visible(True)

# Create the background which will scroll and loop over a set of different
# size stars
    background = pygame.Surface((size.x_background, size.background))
    background = background.convert()
    background.fill(BLACK)

    backgroundLoc = size.backgroundLoc
    finalStars = deque()
    for y in range(0, size.backgroundLoc, size.star_seq):
        starsize = random.randint(size.star_s, size.star_l)
        x = random.randint(0, size.x_background - starsize)
        if y <= scr_size:
            finalStars.appendleft((x, y + size.backgroundLoc, starsize))
        pygame.draw.rect(
            background, RED, pygame.Rect(x, y, starsize, starsize))
    while finalStars:
        x, y, starsize = finalStars.pop()
        pygame.draw.rect(
            background, RED, pygame.Rect(x, y, starsize, starsize))

# Display the background
    screen.blit(background, (0, 0))
    pygame.display.flip()

# Prepare game objects
    speed = 1.5
    MasterSprite.speed = speed
    alienPeriod = 60 / speed
    clockTime = 60  # maximum FPS
    clock = pygame.time.Clock()
    ship = Ship2()
    ship2 = Ship3()
    initialAlienTypes = (Siney, Spikey)
    powerupTypes = (BombPowerup, ShieldPowerup, DoublemissilePowerup, DistPowerup)
    # Sprite groups
    alldrawings = pygame.sprite.Group()
    allsprites = pygame.sprite.RenderPlain((ship, ship2))
    MasterSprite.allsprites = allsprites
    Alien.pool = pygame.sprite.Group(
        [alien() for alien in initialAlienTypes for _ in range(5)])
    Alien.active = pygame.sprite.Group()
    Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
    Missile.active = pygame.sprite.Group()
    Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])
    Explosion.active = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    bombs2 = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    # Sounds
    missile_sound = load_sound('missile.ogg')
    bomb_sound = load_sound('bomb.ogg')
    alien_explode_sound = load_sound('alien_explode.ogg')
    ship_explode_sound = load_sound('ship_explode.ogg')
    load_music('music_loop.ogg')

    aliennum = 10 # 아이템 나오는 alien 숫자(aliennum 이상 남은 경우)
    setaliennum = 10 # 4웨이브마다 초기 웨이브 수
    speedup = 0.5 # 웨이브마다 speed += speedup
    aliennumup = 2 # 4웨이브 주기로 alienthiswave = int(alienthiswave * aliennumup)
    finalwave = 4

    alienPeriod = clockTime // 2
    curTime = 0
    aliensThisWave, aliensLeftThisWave, Alien.numOffScreen = 10, 10, 10
    wave = 1
    bombsHeld = 3
    doublemissile = False #doublemissile아이템이 지속되는 동안(5초) 미사일이 두배로 발사됨
    Itemdouble = False
    score = 0
    bombsHeld2 = 3
    doublemissile2 = False
    Itemdouble2 = False
    score2 = 0
    missilesFired = 0
    powerupTime = 1 * clockTime
    powerupTimeLeft = powerupTime
    betweenWaveTime = 5 * clockTime
    betweenWaveCount = betweenWaveTime
    betweenDoubleTime = 2 * clockTime
    betweenDoubleCount = betweenDoubleTime
    betweenDoubleCount2 = betweenDoubleTime
    font = pygame.font.Font(None, size.font_eng)
    font2 = pygame.font.SysFont('nanumgothic', size.font_kor)
    inMenu = True
    half_tf = True
    distTime = 2 * clockTime # 2초동안 화면이 안보임
    distItem = 0 # 화면 안보이는 시간(distItem = distTime)
    distItem2 = 0
    before_game = True

    hiScores = Database.getScores()
    highScoreTexts = [font.render("NAME", 1, RED),
                      font.render("SCORE", 1, RED),
                      font.render("ACCURACY", 1, RED)]
    highScorePos = [highScoreTexts[0].get_rect(
                      topleft=screen.get_rect().inflate(-size.toppos, -size.toppos).topleft),
                    highScoreTexts[1].get_rect(
                      midtop=screen.get_rect().inflate(-size.toppos, -size.toppos).midtop),
                    highScoreTexts[2].get_rect(
                      topright=screen.get_rect().inflate(-size.toppos, -size.toppos).topright)]
    for hs in hiScores:
        highScoreTexts.extend([font.render(str(hs[x]), 1, WHITE)
                               for x in range(3)])
        highScorePos.extend([highScoreTexts[x].get_rect(
            topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])

    ########

    title, titleRect = load_image('title_mode2.png')
    title = pygame.transform.scale(title, (round(title.get_width()*size.ratio), round(title.get_height()*size.ratio)))
    titleRect = pygame.Rect(0, 0, title.get_width(), title.get_height())
    pause,pauseRect = load_image('pause.png',WHITE)
    pause = pygame.transform.scale(pause, (round(pause.get_width()*size.ratio), round(pause.get_height()*size.ratio)))
    pauseRect = pygame.Rect(0, 0, pause.get_width(), pause.get_height())
    titleRect.midtop = screen.get_rect().inflate(0, -size.middletoppos).midtop
    pauseRect.midtop = screen.get_rect().inflate(0, -size.middletoppos).midtop

    dist, distRect = load_image('black.png', WHITE)
    dist = pygame.transform.scale(dist, (scr_size, scr_size))
    distRect = pygame.Rect(0, 0, dist.get_width(), dist.get_height())
    distRect.midtop = screen.get_rect().inflate(0, 0).midtop

    dist2, distRect2 = load_image('black.png', WHITE)
    dist2 = pygame.transform.scale(dist2, (scr_size, scr_size))
    distRect2 = pygame.Rect(0, 0, dist2.get_width(), dist2.get_height())
    distRect2.midtop = screen.get_rect().inflate(0, 0).midtop


    text_eng_set = [font.render('START GAME', 1, WHITE),
                    font.render('SOUND FX', 1, WHITE),
                    font.render('   ON', 1, RED),
                    font.render('   OFF', 1, RED),
                    font.render('MUSIC', 1, WHITE),
                    font.render('   ON', 1, RED),
                    font.render('   OFF', 1, RED),
                    font.render('QUIT', 1, WHITE),
                    font.render('RESTART', 1, WHITE),
                    font.render('LANGUAGE', 1, WHITE),
                    font.render('GAME OVER', 1, WHITE),
                    font.render('SPEED UP!', 1, RED)]

    text_kor_set = [font2.render('게임 시작', 1, WHITE),
                    font2.render('효과음        ', 1, WHITE),
                    font2.render('켜짐      ', 1, RED),
                    font2.render('꺼짐', 1, RED),
                    font2.render('음악', 1, WHITE),
                    font2.render('켜짐', 1, RED),
                    font2.render('꺼짐', 1, RED),
                    font2.render('종료', 1, WHITE),
                    font2.render('다시 시작', 1, WHITE),
                    font2.render('언어', 1, WHITE),
                    font2.render('게임 종료', 1, WHITE),
                    font2.render('스피드 업!', 1, RED)]

    startText, fxText, fxOnText, fxOffText, musicText, musicOnText, musicOffText, quitText, restartText, languageText, gameOverText, speedUpText = set_language(language)
    ### 언어 설정 끝

    startPos = startText.get_rect(midtop=titleRect.inflate(0, size.topendpos).midbottom)
    fxPos = fxText.get_rect(topleft=startPos.bottomleft)
    fxOnPos = fxOnText.get_rect(topleft=fxPos.topright)
    fxOffPos = fxOffText.get_rect(topleft=fxPos.topright)
    musicPos = fxText.get_rect(topleft=fxPos.bottomleft)
    musicOnPos = musicOnText.get_rect(topleft=musicPos.topright)
    musicOffPos = musicOffText.get_rect(topleft=musicPos.topright)
    quitPos = quitText.get_rect(topleft=musicPos.bottomleft)
    languagePos = languageText.get_rect(topleft=quitPos.bottomleft)

    selectText = font.render('> ', 1, WHITE)
    selectPos = selectText.get_rect(topright=startPos.topleft)
    restartPos = restartText.get_rect(bottomleft=fxPos.topleft)

    playerText, player2Text, bstartText, switchText = beforegame_text_update(language)
    playerPos = playerText.get_rect(topleft=screen.get_rect().topleft)
    player2Pos = player2Text.get_rect(topleft=screen.get_rect().midtop)
    bstartPos = bstartText.get_rect(center=screen.get_rect().center)
    switchPos = switchText.get_rect(midbottom=screen.get_rect().midbottom)

    selection = 1
    soundFX = Database.getSound()
    music = Database.getSound(music=True)

    menuDict = {1: startPos, 2: fxPos, 3: musicPos, 4: quitPos, 5: languagePos}

    # 버튼 구현
    mainImg = pygame.image.load("data/main.png")
    mainImg = pygame.transform.scale(mainImg, (round(mainImg.get_width()*size.ratio), round(mainImg.get_height()*size.ratio)))
    modeImg_one = pygame.image.load("data/mode1.png")
    modeImg_one = pygame.transform.scale(modeImg_one, (round(modeImg_one.get_width()*size.ratio), round(modeImg_one.get_height()*size.ratio)))
    modeImg_two = pygame.image.load("data/mode2.png")
    modeImg_two = pygame.transform.scale(modeImg_two, (round(modeImg_two.get_width()*size.ratio), round(modeImg_two.get_height()*size.ratio)))
    quitImg = pygame.image.load("data/quiticon.png")
    quitImg = pygame.transform.scale(quitImg, (round(quitImg.get_width()*size.ratio), round(quitImg.get_height()*size.ratio)))
    clickmainImg = pygame.image.load("data/mainclicked.png")
    clickmainImg = pygame.transform.scale(clickmainImg, (round(clickmainImg.get_width()*size.ratio), round(clickmainImg.get_height()*size.ratio)))
    clickmodeImg_one = pygame.image.load("data/mode1clicked.png")
    clickmodeImg_one = pygame.transform.scale(clickmodeImg_one, (round(clickmodeImg_one.get_width()*size.ratio), round(clickmodeImg_one.get_height()*size.ratio)))
    clickmodeImg_two = pygame.image.load("data/mode2clicked.png")
    clickmodeImg_two = pygame.transform.scale(clickmodeImg_two, (round(clickmodeImg_two.get_width()*size.ratio), round(clickmodeImg_two.get_height()*size.ratio)))
    clickQuitImg = pygame.image.load("data/clickedQuitIcon.png")
    clickQuitImg = pygame.transform.scale(clickQuitImg, (round(clickQuitImg.get_width()*size.ratio), round(clickQuitImg.get_height()*size.ratio)))

    if music and pygame.mixer:
        pygame.mixer.music.play(loops=-1)

    # 메인 메뉴
    while inMenu:
        scr_x, scr_y = pygame.display.get_surface().get_size()
        if size.x_background != scr_x or scr_size != scr_y :
            return min(scr_x//size.x_background_ratio, scr_y), level_size, id, language    # 메뉴화면에서만 창 사이즈 크기 확인하고, 변경되면 main 재시작
        clock.tick(clockTime)

        screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                sys.exit()
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_RETURN): # K_RETURN은 enter누르면
                if selection == 1:
                    inMenu = False
                    shoot_count , kill_count = 0, 0
                    playerText, player2Text, bstartText, switchText = beforegame_text_update(language)
                    ship.initializeKeys()
                    ship2.initializeKeys()
                elif selection == 2 :
                    soundFX = not soundFX
                    if soundFX:
                        missile_sound.play()
                    Database.setSound(int(soundFX))
                elif selection == 3 and pygame.mixer:
                    music = not music
                    if music:
                        pygame.mixer.music.play(loops=-1)
                    else:
                        pygame.mixer.music.stop()
                    Database.setSound(int(music), music=True)
                elif selection == 4 :
                     pygame.quit()
                     sys.exit()
                elif selection == 5 and language == "ENG":
                    language = "KOR"
                elif selection == 5 and language == "KOR":
                    language = "ENG"

            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_UP
                  and selection > 1):
                selection -= 1
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_DOWN
                  and selection < len(menuDict)):
                selection += 1

        selectPos = selectText.get_rect(topright=menuDict[selection].topleft)


        textOverlays = zip([startText, fxText,
                            musicText, quitText, languageText, selectText,
                            fxOnText if soundFX else fxOffText,
                            musicOnText if music else musicOffText],
                            [startPos, fxPos,
                            musicPos, quitPos, languagePos, selectPos,
                            fxOnPos if soundFX else fxOffPos,
                            musicOnPos if music else musicOffPos])
        screen.blit(title, titleRect)

        #Text Update
        startText, fxText, fxOnText, fxOffText, musicText, musicOnText, musicOffText, quitText, restartText, languageText, gameOverText, speedUpText = set_language(language)

        for txt, pos in textOverlays:
            screen.blit(txt, pos)

        #버튼 구현
        modeButton_one = Button(screen,modeImg_one,size.button1pos_1,size.buttonpos_2,size.buttonpos_3,size.buttonpos_4,clickmodeImg_one,size.button1pos_1_ad,size.button_ad,'mode_one') # 버튼 클릭시 실행하고 싶은 파일을 'mode_one'에 써주면 된다.
        modeButton_two = Button(screen,mainImg,size.button2pos_1,size.buttonpos_2,size.buttonpos_3,size.buttonpos_4,clickmainImg,size.button2pos_1_ad,size.button_ad,'shooting_game')
        quitButton = Button(screen,quitImg,size.button3pos_1,size.buttonpos_2,size.buttonpos_3,size.buttonpos_4,clickQuitImg,size.button3pos_1_ad,size.button_ad,'quitgame')

        if modeButton_one.lvl_size == -1 :
            return scr_size, mode1_lvl_size, id, language
        if modeButton_two.lvl_size == -2 :
            return scr_size, main_lvl_size, id, language

        pygame.display.flip()
        #여기까지 버튼 구현size.button_ad

    while before_game:

        # resize
        scr_x , scr_y = pygame.display.get_surface().get_size()
        if size.x_background != scr_x or scr_size != scr_y :
            prev_scr_size = scr_size
            scr_size, user_size, screen, background, backgroundLoc, finalStars, font, font2, title, titleRect, pause, pauseRect, text_eng_set, text_kor_set, startPos, startText, fxPos, fxOnPos, fxOffPos, musicPos, musicOnPos, musicOffPos, quitPos, languagePos, selectText, selectPos, restartPos, menuDict, dist, distRect, dist2, distRect2, playerText, player2Text, bstartText, switchText, playerPos, player2Pos, bstartPos, switchPos = resize(scr_x, scr_y, mode2_lvl_size)
            shipx, shipy = ship.rect[0] * scr_size / prev_scr_size, ship.rect[1] * scr_size / prev_scr_size
            shipspeed = ship.speed
            shipx2, shipy2 = ship2.rect[0] * scr_size / prev_scr_size, ship2.rect[1] * scr_size / prev_scr_size
            shipspeed2 = ship2.speed

            Alien.pool = pygame.sprite.Group([alien() for alien in initialAlienTypes for _ in range(5)])
            powerupTypes = (BombPowerup, ShieldPowerup, DoublemissilePowerup)
            Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
            Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])

            for i in allsprites.sprites() :
                for j in i.rect :
                    j = j * scr_size / prev_scr_size
                i.image = pygame.transform.scale(i.image, (round(i.image.get_width()* scr_size / prev_scr_size), round(i.image.get_height()*scr_size / prev_scr_size)))
                i.rect = pygame.Rect(0, 0, i.image.get_width(), i.image.get_height())
                i.screen = pygame.display.get_surface()
                i.area = ship.screen.get_rect()

            ship.speed = round(shipspeed * scr_size / prev_scr_size)
            ship.shield = pygame.transform.scale(ship.shield, (round(ship.shield.get_width()* scr_size / prev_scr_size), round(ship.shield.get_height()*scr_size / prev_scr_size)))
            ship.rect[0], ship.rect[1] = shipx, shipy
            ship.original = ship.image
            ship.radius = max(ship.rect.width, ship.rect.height)

            ship2.speed = round(shipspeed2 * scr_size / prev_scr_size)
            ship2.shield = pygame.transform.scale(ship2.shield, (round(ship2.shield.get_width()* scr_size / prev_scr_size), round(ship2.shield.get_height()*scr_size / prev_scr_size)))
            ship2.rect[0], ship2.rect[1] = shipx2, shipy2
            ship2.original = ship2.image
            ship2.radius = max(ship2.rect.width, ship2.rect.height)
        # resize

        clock.tick(clockTime)

        for event in pygame.event.get():
            if (event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif (event.type == pygame.KEYDOWN
                  and event.key in direction.keys()):
                ship.horiz += direction[event.key][0] * speed
                ship.vert += direction[event.key][1] * speed
            elif (event.type == pygame.KEYUP
                  and event.key in direction.keys()):
                ship.horiz -= direction[event.key][0] * speed
                ship.vert -= direction[event.key][1] * speed
            elif (event.type == pygame.KEYDOWN
                  and event.key in direction2.keys()):
                ship2.horiz += direction2[event.key][0] * speed
                ship2.vert += direction2[event.key][1] * speed
            elif (event.type == pygame.KEYUP
                  and event.key in direction2.keys()):
                ship2.horiz -= direction2[event.key][0] * speed
                ship2.vert -= direction2[event.key][1] * speed
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_u):
                before_game = False
                break
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_l):
                half_tf = not half_tf
                ship, ship2 = ship2, ship
                if half_tf :
                    playerText, player2Text, bstartText, switchText = beforegame_text_update(language)
                else :
                    player2Text, playerText, bstartText, switchText = beforegame_text_update(language)

        if half_tf:
            screen, background, backgroundLoc = background_update_half(screen, background, backgroundLoc)
        else:
            screen, background, backgroundLoc = background_update_half_two(screen, background, backgroundLoc)

        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()

        textOverlays = zip([playerText,player2Text,bstartText,switchText],
                                        [playerPos,player2Pos,bstartPos,switchPos])
        for txt, pos in textOverlays:
            screen.blit(txt, pos)

        pygame.display.flip()

    while ship.alive and ship2.alive:

        # resize
        scr_x , scr_y = pygame.display.get_surface().get_size()
        if size.x_background != scr_x or scr_size != scr_y :
            prev_scr_size = scr_size
            scr_size, user_size, screen, background, backgroundLoc, finalStars, font, font2, title, titleRect, pause, pauseRect, text_eng_set, text_kor_set, startPos, startText, fxPos, fxOnPos, fxOffPos, musicPos, musicOnPos, musicOffPos, quitPos, languagePos, selectText, selectPos, restartPos, menuDict, dist, distRect, dist2, distRect2, playerText, player2Text, bstartText, switchText, playerPos, player2Pos, bstartPos, switchPos = resize(scr_x, scr_y, mode2_lvl_size)
            shipx, shipy = ship.rect[0] * scr_size / prev_scr_size, ship.rect[1] * scr_size / prev_scr_size
            shipspeed = ship.speed
            shipx2, shipy2 = ship2.rect[0] * scr_size / prev_scr_size, ship2.rect[1] * scr_size / prev_scr_size
            shipspeed2 = ship2.speed

            Alien.pool = pygame.sprite.Group([alien() for alien in initialAlienTypes for _ in range(5)])
            powerupTypes = (BombPowerup, ShieldPowerup, DoublemissilePowerup)
            Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
            Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])

            for i in allsprites.sprites() :
                for j in i.rect :
                    j = j * scr_size / prev_scr_size
                i.image = pygame.transform.scale(i.image, (round(i.image.get_width()* scr_size / prev_scr_size), round(i.image.get_height()*scr_size / prev_scr_size)))
                i.rect = pygame.Rect(0, 0, i.image.get_width(), i.image.get_height())
                i.screen = pygame.display.get_surface()
                i.area = ship.screen.get_rect()

            ship.speed = round(shipspeed * scr_size / prev_scr_size)
            ship.shield = pygame.transform.scale(ship.shield, (round(ship.shield.get_width()* scr_size / prev_scr_size), round(ship.shield.get_height()*scr_size / prev_scr_size)))
            ship.rect[0], ship.rect[1] = shipx, shipy
            ship.original = ship.image
            ship.radius = max(ship.rect.width, ship.rect.height)

            ship2.speed = round(shipspeed2 * scr_size / prev_scr_size)
            ship2.shield = pygame.transform.scale(ship2.shield, (round(ship2.shield.get_width()* scr_size / prev_scr_size), round(ship2.shield.get_height()*scr_size / prev_scr_size)))
            ship2.rect[0], ship2.rect[1] = shipx2, shipy2
            ship2.original = ship2.image
            ship2.radius = max(ship2.rect.width, ship2.rect.height)
        # resize

        clock.tick(clockTime)

        if aliensLeftThisWave >= aliennum:
            powerupTimeLeft -= 1
        if powerupTimeLeft <= 0:
            powerupTimeLeft = powerupTime
            random.choice(powerupTypes)().add(powerups, allsprites)

        # Event Handling
        for event in pygame.event.get():
            if (event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif (event.type == pygame.KEYDOWN
                  and event.key in direction.keys()):
                ship.horiz += direction[event.key][0] * speed
                ship.vert += direction[event.key][1] * speed
            elif (event.type == pygame.KEYUP
                  and event.key in direction.keys()):
                ship.horiz -= direction[event.key][0] * speed
                ship.vert -= direction[event.key][1] * speed
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_SPACE):
                shoot_count += 1
                # doublemissile 구현
                if doublemissile:
                    Missile.position(ship.rect.topleft)
                    Missile.position(ship.rect.topright)
                    missilesFired += 2
                else:
                    Missile.position(ship.rect.midtop)
                    missilesFired += 1
                if soundFX:
                    missile_sound.play()
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_b):
                if bombsHeld > 0:
                    bombsHeld -= 1
                    newBomb = ship.bomb()
                    newBomb.add(bombs, alldrawings)
                    if soundFX:
                        bomb_sound.play()

            elif (event.type == pygame.KEYDOWN
                  and event.key in direction2.keys()):
                ship2.horiz += direction2[event.key][0] * speed
                ship2.vert += direction2[event.key][1] * speed
            elif (event.type == pygame.KEYUP
                  and event.key in direction2.keys()):
                ship2.horiz -= direction2[event.key][0] * speed
                ship2.vert -= direction2[event.key][1] * speed
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_v):
                shoot_count += 1
                # doublemissile 구현
                if doublemissile2:
                    Missile.position(ship2.rect.topleft)
                    Missile.position(ship2.rect.topright)
                    missilesFired += 2
                else:
                    Missile.position(ship2.rect.midtop)
                    missilesFired += 1
                if soundFX:
                    missile_sound.play()
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_q):
                if bombsHeld2 > 0:
                    bombsHeld2 -= 1
                    newBomb = ship2.bomb()
                    newBomb.add(bombs2, alldrawings)
                    if soundFX:
                        bomb_sound.play()

            # pause 구현부분
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_p):
                inPmenu = True
                menuDict = {1: restartPos, 2: fxPos, 3: musicPos, 4: quitPos}
                selectPos = selectText.get_rect(topright=restartPos.topleft)

                while inPmenu:

                    # resize
                    scr_x , scr_y = pygame.display.get_surface().get_size()
                    if size.x_background != scr_x or scr_size != scr_y :
                        prev_scr_size = scr_size
                        scr_size, user_size, screen, background, backgroundLoc, finalStars, font, font2, title, titleRect, pause, pauseRect, text_eng_set, text_kor_set, startPos, startText, fxPos, fxOnPos, fxOffPos, musicPos, musicOnPos, musicOffPos, quitPos, languagePos, selectText, selectPos, restartPos, menuDict, dist, distRect, dist2, distRect2, playerText, player2Text, bstartText, switchText, playerPos, player2Pos, bstartPos, switchPos = resize(scr_x, scr_y, mode2_lvl_size)
                        shipx, shipy = ship.rect[0] * scr_size / prev_scr_size, ship.rect[1] * scr_size / prev_scr_size
                        shipspeed = ship.speed
                        shipx2, shipy2 = ship2.rect[0] * scr_size / prev_scr_size, ship2.rect[1] * scr_size / prev_scr_size
                        shipspeed2 = ship2.speed

                        Alien.pool = pygame.sprite.Group([alien() for alien in initialAlienTypes for _ in range(5)])
                        powerupTypes = (BombPowerup, ShieldPowerup, DoublemissilePowerup)
                        Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
                        Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])

                        for i in allsprites.sprites() :
                            for j in i.rect :
                                j = j * scr_size / prev_scr_size
                            i.image = pygame.transform.scale(i.image, (round(i.image.get_width()* scr_size / prev_scr_size), round(i.image.get_height()*scr_size / prev_scr_size)))
                            i.rect = pygame.Rect(0, 0, i.image.get_width(), i.image.get_height())
                            i.screen = pygame.display.get_surface()
                            i.area = ship.screen.get_rect()

                        ship.speed = round(shipspeed * scr_size / prev_scr_size)
                        ship.shield = pygame.transform.scale(ship.shield, (round(ship.shield.get_width()* scr_size / prev_scr_size), round(ship.shield.get_height()*scr_size / prev_scr_size)))
                        ship.rect[0], ship.rect[1] = shipx, shipy
                        ship.original = ship.image
                        ship.radius = max(ship.rect.width, ship.rect.height)

                        ship2.speed = round(shipspeed2 * scr_size / prev_scr_size)
                        ship2.shield = pygame.transform.scale(ship2.shield, (round(ship2.shield.get_width()* scr_size / prev_scr_size), round(ship2.shield.get_height()*scr_size / prev_scr_size)))
                        ship2.rect[0], ship2.rect[1] = shipx2, shipy2
                        ship2.original = ship2.image
                        ship2.radius = max(ship2.rect.width, ship2.rect.height)
                        menuDict = {1: restartPos, 2: fxPos, 3: musicPos, 4: quitPos}

                    # resize

                    clock.tick(clockTime)
                    screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)

                    textOverlays = zip([restartText, fxText,
                                            musicText, quitText, selectText,
                                            fxOnText if soundFX else fxOffText,
                                            musicOnText if music else musicOffText],
                                        [restartPos, fxPos,
                                            musicPos, quitPos, selectPos,
                                            fxOnPos if soundFX else fxOffPos,
                                            musicOnPos if music else musicOffPos])

                    screen.blit(pause, pauseRect)

                    for txt, pos in textOverlays:
                        screen.blit(txt, pos)
                    pygame.display.flip()

                    ###
                    for event in pygame.event.get():
                        if (event.type == pygame.QUIT):
                            pygame.quit()
                            sys.exit()
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_RETURN): # K_RETURN은 enter누르면
                            if selection == 1:
                                inPmenu = False
                                break
                            elif selection == 2:
                                soundFX = not soundFX
                                if soundFX:
                                    missile_sound.play()
                                Database.setSound(int(soundFX))
                            elif selection == 3 and pygame.mixer:
                                music = not music
                                if music:
                                    pygame.mixer.music.play(loops=-1)
                                else:
                                    pygame.mixer.music.stop()
                                Database.setSound(int(music), music=True)
                            elif selection == 4 and id == '':
                                pygame.quit()
                                sys.exit()
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_UP
                            and selection > 1):
                            selection -= 1
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_DOWN
                            and selection < len(menuDict)):
                            selection += 1

                        selectPos = selectText.get_rect(topright=menuDict[selection].topleft)


     # Collision Detection
        # Aliens
        for alien in Alien.active:
            for bomb in bombs:
                if pygame.sprite.collide_circle(
                        bomb, alien) and alien in Alien.active:
                    alien.table()
                    Explosion.position(alien.rect.center)
                    aliensLeftThisWave, kill_count, score = kill_alien(alien, aliensLeftThisWave, kill_count, score)
                    missilesFired += 1
                    if soundFX:
                        alien_explode_sound.play()
            for bomb in bombs2:
                if pygame.sprite.collide_circle(
                        bomb, alien) and alien in Alien.active:
                    alien.table()
                    Explosion.position(alien.rect.center)
                    aliensLeftThisWave, kill_count, score2 = kill_alien(alien, aliensLeftThisWave, kill_count, score2)
                    if soundFX:
                        alien_explode_sound.play()
            for missile in Missile.active:
                if pygame.sprite.collide_rect(
                        missile, alien) and alien in Alien.active:
                    alien.table()
                    missile.table()
                    Explosion.position(alien.rect.center)
                    if alien.rect.center[0] < scr_size :
                        aliensLeftThisWave, kill_count, score = kill_alien(alien, aliensLeftThisWave, kill_count, score)
                    else :
                        aliensLeftThisWave, kill_count, score2 = kill_alien(alien, aliensLeftThisWave, kill_count, score2)
                    if soundFX:
                        alien_explode_sound.play()
            if pygame.sprite.collide_rect(alien, ship):
                if ship.shieldUp:
                    alien.table()
                    Explosion.position(alien.rect.center)
                    aliensLeftThisWave, kill_count, score = kill_alien(alien, aliensLeftThisWave, kill_count, score)
                    missilesFired += 1
                    ship.shieldUp = False
                else:
                    # life 구현 부분
                    if ship.lives == 1:
                        ship.alive = False
                        ship.remove(allsprites)
                        Explosion.position(ship.rect.center)
                        if soundFX:
                            ship_explode_sound.play()
                    else:
                        alien.table()
                        Explosion.position(alien.rect.center)
                        aliensLeftThisWave -= 1
                        ship.lives -=1

            if pygame.sprite.collide_rect(alien, ship2):
                if ship2.shieldUp:
                    alien.table()
                    Explosion.position(alien.rect.center)
                    aliensLeftThisWave, kill_count, score2 = kill_alien(alien, aliensLeftThisWave, kill_count, score2)
                    missilesFired += 1
                    ship2.shieldUp = False
                else:
                    # life 구현 부분
                    if ship2.lives == 1:
                        ship2.alive = False
                        ship2.remove(allsprites)
                        Explosion.position(ship2.rect.center)
                        if soundFX:
                            ship_explode_sound.play()
                    else:
                        alien.table()
                        Explosion.position(alien.rect.center)
                        aliensLeftThisWave -= 1
                        ship2.lives -=1

        # PowerUps
        for powerup in powerups:
            if pygame.sprite.collide_circle(powerup, ship):
                if powerup.pType == 'bomb':
                    bombsHeld += 1
                elif powerup.pType == 'dist':
                    distItem = distTime
                elif powerup.pType == 'shield':
                    ship.shieldUp = True
                elif powerup.pType == 'doublemissile':
                    doublemissile = True
                powerup.kill()
            elif powerup.rect.top > powerup.area.bottom:
                powerup.kill()

        for powerup in powerups:
            if pygame.sprite.collide_circle(powerup, ship2):
                if powerup.pType == 'bomb':
                    bombsHeld2 += 1
                elif powerup.pType == 'dist':
                    distItem2 = distTime
                elif powerup.pType == 'shield':
                    ship2.shieldUp = True
                elif powerup.pType == 'doublemissile':
                    doublemissile2 = True
                powerup.kill()
            elif powerup.rect.top > powerup.area.bottom:
                powerup.kill()

     # Update Aliens
        if curTime <= 0 and aliensLeftThisWave > 0:
            Alien.position()
            curTime = alienPeriod
        elif curTime > 0:
            curTime -= 1

     # Update text overlays
        if half_tf :
            waveText, leftText, scoreText, scoreText2, bombText, bombText2, ship1winText, ship2winText, drawText = ingame_text_update(language)
        else :
            waveText, leftText, scoreText2, scoreText, bombText2, bombText, ship1winText, ship2winText, drawText = ingame_text_update(language)

        wavePos = waveText.get_rect(topright=screen.get_rect().midtop)
        leftPos = leftText.get_rect(topleft=screen.get_rect().midtop)
        scorePos = scoreText.get_rect(topleft=screen.get_rect().topleft)
        bombPos = bombText.get_rect(bottomleft=screen.get_rect().bottomleft)
        scorePos2 = scoreText2.get_rect(topright=screen.get_rect().topright)
        bombPos2 = bombText2.get_rect(bottomleft=screen.get_rect().midbottom)

        text = [waveText, leftText, scoreText, bombText, scoreText2, bombText2]
        textposition = [wavePos, leftPos, scorePos, bombPos, scorePos2, bombPos2]

        #5초동안 doublemissile상태를 유지
        if doublemissile:
            if betweenDoubleCount > 0:
                betweenDoubleCount -= 1
            elif betweenDoubleCount == 0:
                doublemissile = False
                betweenDoubleCount = betweenDoubleTime
        if Itemdouble:
            if betweenDoubleCount > 0:
                betweenDoubleCount -= 1
            elif betweenDoubleCount == 0:
                doublemissile = False
                Itemdouble = False
                betweenDoubleCount = betweenDoubleTime

        if doublemissile2:
            if betweenDoubleCount2 > 0:
                betweenDoubleCount2 -= 1
            elif betweenDoubleCount2 == 0:
                doublemissile2 = False
                betweenDoubleCount = betweenDoubleTime
        if Itemdouble2:
            if betweenDoubleCount2 > 0:
                betweenDoubleCount2 -= 1
            elif betweenDoubleCount2 == 0:
                doublemissile2 = False
                Itemdouble2 = False
                betweenDoubleCount2 = betweenDoubleTime

     # Detertmine when to move to next wave
        if aliensLeftThisWave <= 0:
            if wave == finalwave :
                break
            elif betweenWaveCount > 0:
                betweenWaveCount -= 1
                nextWaveText = font.render(
                    'Wave ' + str(wave + 1) + ' in', 1, WHITE)
                nextWaveNum = font.render(
                    str((betweenWaveCount // clockTime) + 1), 1, WHITE)
                text.extend([nextWaveText, nextWaveNum])
                nextWavePos = nextWaveText.get_rect(
                    center=screen.get_rect().center)
                nextWaveNumPos = nextWaveNum.get_rect(
                    midtop=nextWavePos.midbottom)
                textposition.extend([nextWavePos, nextWaveNumPos])
                text.append(speedUpText)
                speedUpPos = speedUpText.get_rect(midtop=nextWaveNumPos.midbottom)
                textposition.append(speedUpPos)
            elif betweenWaveCount == 0:
                if wave % 4 == 0:
                    speed += speedup
                    MasterSprite.speed = speed
                    ship.initializeKeys()
                    ship2.initializeKeys()
                    aliensThisWave = setaliennum
                    aliensLeftThisWave = Alien.numOffScreen = aliensThisWave
                else:
                    aliensThisWave = int(aliensThisWave * aliennumup)
                    aliensLeftThisWave = Alien.numOffScreen = aliensThisWave
                if wave == 1:
                    Alien.pool.add([Fasty() for _ in range(5)])
                if wave == 2:
                    Alien.pool.add([Roundy() for _ in range(5)])
                if wave == 3:
                    Alien.pool.add([Crawly() for _ in range(5)])
                wave += 1
                betweenWaveCount = betweenWaveTime
                if doublemissile:
                    Itemdouble = True

                selectPos = selectText.get_rect(topright=menuDict[selection].topleft)

                textOverlays = zip([restartText, fxText,
                                    musicText, quitText, selectText,
                                    fxOnText if soundFX else fxOffText,
                                    musicOnText if music else musicOffText],
                                [restartPos, fxPos,
                                    musicPos, quitPos, selectPos,
                                    fxOnPos if soundFX else fxOffPos,
                                    musicOnPos if music else musicOffPos])

                for txt, pos in textOverlays:
                    screen.blit(txt, pos)
                pygame.display.flip()
        textOverlays = zip(text, textposition)

     # Update and draw all sprites and text
        if half_tf:
            screen, background, backgroundLoc = background_update_half(screen, background, backgroundLoc)
        else:
            screen, background, backgroundLoc = background_update_half_two(screen, background, backgroundLoc)

        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()

        for txt, pos in textOverlays:
            screen.blit(txt, pos)
        # life 구현
        ship.draw_lives(screen, size.lifex, size.lifey)
        ship2.draw_lives(screen, size.lifex, size.lifey)
        if distItem >= 0 :
            distItem -= 1
            if half_tf :
                distRect.topleft = screen.get_rect().inflate(0, 0).midtop

            else :
                distRect.topright = screen.get_rect().inflate(0, 0).midtop
            screen.blit(dist, distRect)
        if distItem2 >= 0 :
            distItem2 -= 1
            if half_tf :
                distRect2.topright = screen.get_rect().inflate(0, 0).midtop
            else :
                distRect2.topleft = screen.get_rect().inflate(0, 0).midtop
            screen.blit(dist2, distRect2)

        pygame.display.flip()


    while True:

        # resize
        scr_x , scr_y = pygame.display.get_surface().get_size()
        if size.x_background != scr_x or scr_size != scr_y :
            prev_scr_size = scr_size
            scr_size, user_size, screen, background, backgroundLoc, finalStars, font, font2, title, titleRect, pause, pauseRect, text_eng_set, text_kor_set, startPos, startText, fxPos, fxOnPos, fxOffPos, musicPos, musicOnPos, musicOffPos, quitPos, languagePos, selectText, selectPos, restartPos, menuDict, dist, distRect, dist2, distRect2, playerText, player2Text, bstartText, switchText, playerPos, player2Pos, bstartPos, switchPos = resize(scr_x, scr_y, mode2_lvl_size)
            shipx, shipy = ship.rect[0] * scr_size / prev_scr_size, ship.rect[1] * scr_size / prev_scr_size
            shipspeed = ship.speed
            shipx2, shipy2 = ship2.rect[0] * scr_size / prev_scr_size, ship2.rect[1] * scr_size / prev_scr_size
            shipspeed2 = ship2.speed

            Alien.pool = pygame.sprite.Group([alien() for alien in initialAlienTypes for _ in range(5)])
            powerupTypes = (BombPowerup, ShieldPowerup, DoublemissilePowerup)
            Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
            Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])

            for i in allsprites.sprites() :
                for j in i.rect :
                    j = j * scr_size / prev_scr_size
                i.image = pygame.transform.scale(i.image, (round(i.image.get_width()* scr_size / prev_scr_size), round(i.image.get_height()*scr_size / prev_scr_size)))
                i.rect = pygame.Rect(0, 0, i.image.get_width(), i.image.get_height())
                i.screen = pygame.display.get_surface()
                i.area = ship.screen.get_rect()

            ship.speed = round(shipspeed * scr_size / prev_scr_size)
            ship.shield = pygame.transform.scale(ship.shield, (round(ship.shield.get_width()* scr_size / prev_scr_size), round(ship.shield.get_height()*scr_size / prev_scr_size)))
            ship.rect[0], ship.rect[1] = shipx, shipy
            ship.original = ship.image
            ship.radius = max(ship.rect.width, ship.rect.height)

            ship2.speed = round(shipspeed2 * scr_size / prev_scr_size)
            ship2.shield = pygame.transform.scale(ship2.shield, (round(ship2.shield.get_width()* scr_size / prev_scr_size), round(ship2.shield.get_height()*scr_size / prev_scr_size)))
            ship2.rect[0], ship2.rect[1] = shipx2, shipy2
            ship2.original = ship2.image
            ship2.radius = max(ship2.rect.width, ship2.rect.height)
        # resize

        clock.tick(clockTime)

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN :
                return scr_size, level_size, id, language

        ship1winPos = ship1winText.get_rect(center=screen.get_rect().center)
        ship2winPos = ship2winText.get_rect(center=screen.get_rect().center)
        drawPos = drawText.get_rect(center=screen.get_rect().center)

    # Update and draw all sprites
        screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()

        if ship.alive and not ship2.alive :
            screen.blit(ship1winText, ship1winPos)
        elif ship2.alive and not ship.alive :
            screen.blit(ship2winText, ship2winPos)
        elif not ship.alive and not ship2.alive :
            screen.blit(drawText, drawPos)

        elif ship.alive and ship2.alive :
            if score > score2 :
                screen.blit(ship1winText, ship1winPos)
            elif score < score2 :
                screen.blit(ship2winText, ship2winPos)
            elif score == score2 :
                screen.blit(drawText, drawPos)

        pygame.display.flip()
