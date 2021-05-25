import pygame
import random
from collections import deque
import sys
# from pygame.font import Font
import grequests

from sprites import (MasterSprite, Ship, Alien, Missile, BombPowerup,CoinPowerup,CoinTwoPowerup,
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

url = "http://15.164.204.93"

class Button:
    def __init__(self, gameDisplay,img_in, x, y, width, height, img_act, x_act, y_act, action = None):
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

            elif click[0] and action == 'mode_two':
                self.lvl_size = -2
        else:
            gameDisplay.blit(img_in,(x,y))
    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


class Keyboard(object):
    keys = {pygame.K_a: 'A', pygame.K_b: 'B', pygame.K_c: 'C', pygame.K_d: 'D',
            pygame.K_e: 'E', pygame.K_f: 'F', pygame.K_g: 'G', pygame.K_h: 'H',
            pygame.K_i: 'I', pygame.K_j: 'J', pygame.K_k: 'K', pygame.K_l: 'L',
            pygame.K_m: 'M', pygame.K_n: 'N', pygame.K_o: 'O', pygame.K_p: 'P',
            pygame.K_q: 'Q', pygame.K_r: 'R', pygame.K_s: 'S', pygame.K_t: 'T',
            pygame.K_u: 'U', pygame.K_v: 'V', pygame.K_w: 'W', pygame.K_x: 'X',
            pygame.K_y: 'Y', pygame.K_z: 'Z'}

def main(scr, level, id):
    scr_size, level_size = scr, level
    user_size = round(scr_size * level_size)
    id = id

    url = "http://15.164.204.93"

    shoot_progress = [10, 100, 1000]
    kill_progress = [10, 100, 1000]

    direction = {None: (0, 0), pygame.K_UP: (0, -scr_size*0.004), pygame.K_DOWN: (0, scr_size*0.004),
             pygame.K_LEFT: (-scr_size*0.004, 0), pygame.K_RIGHT: (scr_size*0.004, 0)}

    # Initialize everything
    pygame.mixer.pre_init(11025, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((scr_size, scr_size), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
    pygame.display.set_caption('Shooting Game')
    pygame.mouse.set_visible(1)

# Create the background which will scroll and loop over a set of different
# size stars
    background = pygame.Surface((scr_size, scr_size*4))
    background = background.convert()
    background.fill((0, 0, 0))

    backgroundLoc = scr_size*3
    finalStars = deque()
    for y in range(0, scr_size*3, round(scr_size*0.06)):
        size = random.randint(round(scr_size*0.004), round(scr_size*0.01))
        x = random.randint(0, scr_size - size)
        if y <= scr_size:
            finalStars.appendleft((x, y + scr_size*3, size))
        pygame.draw.rect(
            background, (255, 0, 0), pygame.Rect(x, y, size, size))
    while finalStars:
        x, y, size = finalStars.pop()
        pygame.draw.rect(
            background, (255, 0, 0), pygame.Rect(x, y, size, size))

# Display the background
    screen.blit(background, (0, 0))
    pygame.display.flip()

# Prepare game objects
    speed = 1.5
    MasterSprite.speed = speed
    alienPeriod = 60 / speed
    clockTime = 60  # maximum FPS
    clock = pygame.time.Clock()
    ship = Ship()
    initialAlienTypes = (Siney, Spikey)
    powerupTypes = (BombPowerup, ShieldPowerup, DoublemissilePowerup)
    coinTypes = (CoinPowerup,CoinTwoPowerup)
    # Sprite groups
    alldrawings = pygame.sprite.Group()
    allsprites = pygame.sprite.RenderPlain((ship,))
    MasterSprite.allsprites = allsprites
    Alien.pool = pygame.sprite.Group(
        [alien() for alien in initialAlienTypes for _ in range(5)])
    Alien.active = pygame.sprite.Group()
    Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)])
    Missile.active = pygame.sprite.Group()
    Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])
    Explosion.active = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    coingroup = pygame.sprite.Group()

    # Sounds
    missile_sound = load_sound('missile.ogg')
    bomb_sound = load_sound('bomb.ogg')
    alien_explode_sound = load_sound('alien_explode.ogg')
    ship_explode_sound = load_sound('ship_explode.ogg')
    load_music('music_loop.ogg')

    alienPeriod = clockTime // 2
    curTime = 0
    aliensThisWave, aliensLeftThisWave, Alien.numOffScreen = 10, 10, 10
    wave = 1
    bombsHeld = 3
    coinsHeld = 0 # coin 구현
    doublemissile = False #doublemissile아이템이 지속되는 동안(5초) 미사일이 두배로 발사됨
    Itemdouble = False
    score = 0
    missilesFired = 0
    powerupTime = 10 * clockTime
    powerupTimeLeft = powerupTime
    betweenWaveTime = 5 * clockTime
    betweenWaveCount = betweenWaveTime
    betweenDoubleTime = 8 * clockTime
    betweenDoubleCount = betweenDoubleTime
    coinTime = 8 * clockTime # coin 구현 
    coinTimeLeft = coinTime # coin 구현
    font = pygame.font.Font(None, round(scr_size*0.065))
    font2 = pygame.font.SysFont('hy견고딕', round(scr_size*0.045))
    inMenu = True
    if id != '' :
        data = {"id": id, "language": ''}
        req = grequests.post(url + '/get_language/', json=data)
        res = grequests.map([req])
        if req.response == None : return scr_size, level_size, ''
        language = str(res[0].content.decode()[1:-1])
    else :
        language = "ENG"

    hiScores = Database.getScores()
    highScoreTexts = [font.render("NAME", 1, RED),
                      font.render("SCORE", 1, RED),
                      font.render("ACCURACY", 1, RED)]
    highScorePos = [highScoreTexts[0].get_rect(
                      topleft=screen.get_rect().inflate(-scr_size*0.2, -scr_size*0.2).topleft),
                    highScoreTexts[1].get_rect(
                      midtop=screen.get_rect().inflate(-scr_size*0.2, -scr_size*0.2).midtop),
                    highScoreTexts[2].get_rect(
                      topright=screen.get_rect().inflate(-scr_size*0.2, -scr_size*0.2).topright)]
    for hs in hiScores:
        highScoreTexts.extend([font.render(str(hs[x]), 1, WHITE)
                               for x in range(3)])
        highScorePos.extend([highScoreTexts[x].get_rect(
            topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])

    #database에 저장된 업적과 연동해야함, hiScoreTexts.extend ~ 라인 참고
    achieveTexts = [font.render("ACHIEVEMENT NAME", 1, RED),
                    font.render("Progress", 1, RED)]
    achievePos = [achieveTexts[0].get_rect(
                    topleft=screen.get_rect().inflate(-scr_size*0.2, -scr_size*0.2).topleft),
                  achieveTexts[1].get_rect(
                    topright=screen.get_rect().inflate(-scr_size*0.2, -scr_size*0.2).topright)]
    ########

    title, titleRect = load_image('title.png')
    title = pygame.transform.scale(title, (round(title.get_width()*scr_size/500), round(title.get_height()*scr_size/500)))
    titleRect = pygame.Rect(0, 0, title.get_width(), title.get_height())
    pause,pauseRect = load_image('pause.png',WHITE)
    pause = pygame.transform.scale(pause, (round(pause.get_width()*scr_size/500), round(pause.get_height()*scr_size/500)))
    pauseRect = pygame.Rect(0, 0, pause.get_width(), pause.get_height())
    titleRect.midtop = screen.get_rect().inflate(0, -scr_size*0.35).midtop
    pauseRect.midtop = screen.get_rect().inflate(0, -scr_size*0.35).midtop
    # 언어 설정
    if language == "ENG": #기본 설정 영어
        startText = font.render('START GAME', 1, WHITE)
        loginText = font.render('LOGIN', 1, WHITE)
        hiScoreText = font.render('HIGH SCORES', 1, WHITE)
        createaccountText = font.render('CREATE ACCOUNT', 1, WHITE)
        fxText = font.render('SOUND FX ', 1, WHITE)
        fxOnText = font.render('ON', 1, RED)
        fxOffText = font.render('OFF', 1, RED)
        musicText = font.render('MUSIC', 1, WHITE)
        achievementText = font.render('ACHIEVEMENTS', 1, WHITE)
        musicOnText = font.render('ON', 1, RED)
        musicOffText = font.render('OFF', 1, RED)
        quitText = font.render('QUIT', 1, WHITE)
        restartText = font.render('RESTART', 1, WHITE)
        languageText = font.render('LANGUAGE', 1, WHITE)
        logoutText = font.render('LOGOUT', 1, WHITE)

    elif language == "KOR":
        startText = font2.render('게임 시작', 1, WHITE)
        loginText = font2.render('로그인', 1, WHITE)
        hiScoreText = font2.render('최고 점수', 1, WHITE)
        createaccountText = font2.render('계정 생성', 1, WHITE)
        fxText = font2.render('효과음 ', 1, WHITE)
        fxOnText = font2.render('켜짐', 1, RED)
        fxOffText = font2.render('꺼짐', 1, RED)
        musicText = font2.render('음악', 1, WHITE)
        achievementText = font2.render('업적', 1, WHITE)
        musicOnText = font2.render('켜짐', 1, RED)
        musicOffText = font2.render('꺼짐', 1, RED)
        quitText = font2.render('종료', 1, WHITE)
        restartText = font2.render('다시 시작', 1, WHITE)
        languageText = font2.render('언어', 1, WHITE)
        logoutText = font2.render('로그아웃', 1, WHITE)

    startPos = startText.get_rect(midtop=titleRect.inflate(0, scr_size*0.15).midbottom)
    loginPos = loginText.get_rect(topleft=startPos.bottomleft)
    createaccountPos = createaccountText.get_rect(topleft=loginPos.bottomleft)
    if id == '' :
        hiScorePos = hiScoreText.get_rect(topleft=createaccountPos.bottomleft)
    else :
        hiScorePos = hiScoreText.get_rect(topleft=startPos.bottomleft)
    fxPos = fxText.get_rect(topleft=hiScorePos.bottomleft)
    fxOnPos = fxOnText.get_rect(topleft=fxPos.topright)
    fxOffPos = fxOffText.get_rect(topleft=fxPos.topright)
    musicPos = fxText.get_rect(topleft=fxPos.bottomleft)
    achievementPos = achievementText.get_rect(topleft=musicPos.bottomleft)
    musicOnPos = musicOnText.get_rect(topleft=musicPos.topright)
    musicOffPos = musicOffText.get_rect(topleft=musicPos.topright)
    if id == '':
        quitPos = quitText.get_rect(topleft=musicPos.bottomleft)
    else:
        quitPos = quitText.get_rect(topleft=achievementPos.bottomleft)

    languagePos = languageText.get_rect(topleft=quitPos.bottomleft)
    logoutPos = logoutText.get_rect(topleft=languagePos.bottomleft)    

    selectText = font.render('> ', 1, WHITE)
    selectPos = selectText.get_rect(topright=startPos.topleft)
    restartPos = restartText.get_rect(bottomleft=hiScorePos.topleft)
    
    ### 언어 설정 끝

    # Coin shop 준비
    next,nextRect = load_image('next.png',WHITE)
    next = pygame.transform.scale(next, (round(next.get_width()*scr_size/200), round(next.get_height()*scr_size/250)))
    nextRect = pygame.Rect(0, 0, next.get_width(), next.get_height())
    nextRect.centerx = scr_size*0.5
    nextRect.centery = scr_size*0.25    
    
    continue_img,continueRect = load_image('continue.png',WHITE)
    continue_img = pygame.transform.scale(continue_img, (round(continue_img.get_width()*scr_size/500), round(continue_img.get_height()*scr_size/500)))
    continueRect = pygame.Rect(0, 0, continue_img.get_width(), continue_img.get_height())
    continueRect.centerx = scr_size * 0.2
    continueRect.centery = scr_size * 0.7

    bomb_img,bombRect = load_image('bomb_click.png')
    bomb_img = pygame.transform.scale(bomb_img, (round(bomb_img.get_width()*scr_size/500), round(bomb_img.get_height()*scr_size/500)))
    bombRect = pygame.Rect(0, 0, bomb_img.get_width(), bomb_img.get_height())
    bombRect.centerx = scr_size * 0.4
    bombRect.centery = scr_size * 0.7

    shield_img,shieldRect = load_image('shield_click.png')
    shield_img = pygame.transform.scale(shield_img, (round(shield_img.get_width()*scr_size/500), round(shield_img.get_height()*scr_size/500)))
    shieldRect = pygame.Rect(0, 0, shield_img.get_width(), shield_img.get_height())
    shieldRect.centerx = scr_size * 0.6
    shieldRect.centery = scr_size * 0.7
    # ---
    shield_on_img,shieldOnRect = load_image('ship_shield.png')
    shield_on_img = pygame.transform.scale(shield_on_img, (round(shield_on_img.get_width()*scr_size/500), round(shield_on_img.get_height()*scr_size/500)))
    shieldOnRect = pygame.Rect(0, 0, shield_on_img.get_width(), shield_on_img.get_height())
    shieldOnRect.centerx = scr_size * 0.6
    shieldOnRect.centery = scr_size * 0.7

    double_img,doubleRect = load_image('doublemissile_powerup.png')
    double_img = pygame.transform.scale(double_img, (round(double_img.get_width()*scr_size/500), round(double_img.get_height()*scr_size/500)))
    doubleRect = pygame.Rect(0, 0, double_img.get_width(), double_img.get_height())
    doubleRect.centerx = scr_size * 0.8
    doubleRect.centery = scr_size * 0.7
    # ---
    double_on_img,doubleOnRect = load_image('doublemissile_click.png')
    double_on_img = pygame.transform.scale(double_on_img, (round(double_on_img.get_width()*scr_size/500), round(double_on_img.get_height()*scr_size/500)))
    doubleOnRect = pygame.Rect(0, 0, double_on_img.get_width(), double_on_img.get_height())
    doubleOnRect.centerx = scr_size * 0.8
    doubleOnRect.centery = scr_size * 0.7

    continueText = font.render('Continue',1,WHITE)
    continuePos = pygame.Rect(0,0,continueText.get_width(), continueText.get_height())
    continuePos.centerx = scr_size * 0.2
    continuePos.centery = scr_size * 0.8

    bombText_Item = font.render('Bomb',1,WHITE)
    bombItemPos = pygame.Rect(0,0,bombText_Item.get_width(), bombText_Item.get_height())
    bombItemPos.centerx = scr_size * 0.4
    bombItemPos.centery = scr_size * 0.8

    shieldText = font.render('Shield',1,WHITE)
    shieldPos = pygame.Rect(0,0,shieldText.get_width(), shieldText.get_height())
    shieldPos.centerx = scr_size * 0.6
    shieldPos.centery = scr_size * 0.8

    doubleText = font.render('Double',1,WHITE)
    doublePos = pygame.Rect(0,0,doubleText.get_width(), doubleText.get_height())
    doublePos.centerx = scr_size * 0.8
    doublePos.centery = scr_size * 0.8

    selectItem = font.render('^',1,WHITE)
    selectItemPos = pygame.Rect(0,0,selectItem.get_width(), selectItem.get_height())
    selectItemPos.centerx = scr_size * 0.2
    selectItemPos.centery = scr_size * 0.8
    
    ###########

    # 업적 이미지 생성

    achievement_set = ['' for i in range(12)]
    achievement_imgset = ['shoot_10.png', 'shoot_100.png', 'shoot_1000.png', 'kill_10.png', 'kill_100.png', 'kill_1000.png']
    for i in range(len(achievement_imgset)) :
        achievement_set[i], achievement_set[i+6] = load_image(achievement_imgset[i])
        achievement_set[i] = pygame.transform.scale(achievement_set[i], (round(achievement_set[i].get_width()*scr_size/3000), round(achievement_set[i].get_height()*scr_size/3000)))
        achievement_set[i+6] = pygame.Rect(0, 0, achievement_set[i].get_width(), achievement_set[i].get_height())
        achievement_set[i+6].centerx = scr_size * 0.25 * (1 + i%3)
        achievement_set[i+6].centery = scr_size * 0.25 * (2 + (i+1)//3)

    shoot10_img, shoot100_img, shoot1000_img, kill10_img, kill100_img, kill1000_img, shoot10Rect, shoot100Rect, shoot1000Rect, kill10Rect, kill100Rect, kill1000Rect = achievement_set
    
    ######################

    selection = 1
    showHiScores = False
    showLogin = False
    showCreateaccount = False
    showAchievement = False
    soundFX = Database.getSound()
    music = Database.getSound(music=True)

    if id != '':
        menuDict = {1: startPos, 2: hiScorePos, 3: fxPos, 4: musicPos, 5: achievementPos , 6: quitPos, 7: languagePos, 8: logoutPos}
    else :
        menuDict = {1: startPos, 2: loginPos, 3: createaccountPos, 4: hiScorePos, 5: fxPos, 6: musicPos, 7: quitPos, 8: languagePos}

    # 버튼 구현
    modeImg_one = pygame.image.load("data/mode1.png")
    modeImg_one = pygame.transform.scale(modeImg_one, (round(modeImg_one.get_width()*scr_size/500), round(modeImg_one.get_height()*scr_size/500)))
    modeImg_two = pygame.image.load("data/mode2.png")
    modeImg_two = pygame.transform.scale(modeImg_two, (round(modeImg_two.get_width()*scr_size/500), round(modeImg_two.get_height()*scr_size/500)))
    quitImg = pygame.image.load("data/quiticon.png")
    quitImg = pygame.transform.scale(quitImg, (round(quitImg.get_width()*scr_size/500), round(quitImg.get_height()*scr_size/500)))
    clickmodeImg_one = pygame.image.load("data/mode1clicked.png")
    clickmodeImg_one = pygame.transform.scale(clickmodeImg_one, (round(clickmodeImg_one.get_width()*scr_size/500), round(clickmodeImg_one.get_height()*scr_size/500)))
    clickmodeImg_two = pygame.image.load("data/mode2clicked.png")
    clickmodeImg_two = pygame.transform.scale(clickmodeImg_two, (round(clickmodeImg_two.get_width()*scr_size/500), round(clickmodeImg_two.get_height()*scr_size/500)))
    clickQuitImg = pygame.image.load("data/clickedQuitIcon.png")
    clickQuitImg = pygame.transform.scale(clickQuitImg, (round(clickQuitImg.get_width()*scr_size/500), round(clickQuitImg.get_height()*scr_size/500)))

    if music and pygame.mixer:
        pygame.mixer.music.play(loops=-1)

    # 메인 메뉴
    while inMenu:
        scr_x , scr_y = pygame.display.get_surface().get_size()
        if scr_size != scr_x or scr_size != scr_y :
            return min(scr_x, scr_y), level_size, id    # 메뉴화면에서만 창 사이즈 크기 확인하고, 변경되면 main 재시작
        clock.tick(clockTime)

        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, scr_size, scr_size))
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = scr_size*3

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                sys.exit()
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_RETURN): # K_RETURN은 enter누르면
                if showHiScores:
                    showHiScores = False
                elif showLogin:
                    showLogin = False
                elif showCreateaccount :
                    showCreateaccount = False
                elif showAchievement :
                    showAchievement = False
                elif selection == 1:
                    screen = pygame.display.set_mode((scr_size, scr_size))  # 리사이즈 불가능하도록 변경
                    inMenu = False
                    shoot_count , kill_count = 0, 0
                    ship.initializeKeys()
                elif selection == 2 and id == '':
                    showLogin = True
                    inMenu = False
                    ship.alive = False
                elif selection == 3 and id == '':
                    showCreateaccount = True
                    inMenu = False
                    ship.alive = False
                elif selection == 4 and id == '' :
                    hiScores = Database.getScores()
                    hiScores_local = []
                    for i in range(len(hiScores)):
                        score_id = hiScores[i][0]
                        score_score = hiScores[i][1]
                        score_accuracy = round(float(hiScores[i][2])*100, 2)
                        hiScores_local.append([score_id, score_score, str(score_accuracy)+"%"])
                        
                    # 중복 아이디 제거
                    hiScores_local = sorted(hiScores_local, key=lambda h: h[1])
                    for i in range(len(hiScores_local)-1):
                        score_id = hiScores_local[i][0]
                        for j in range(i+1, len(hiScores_local)):
                            if score_id == hiScores_local[j][0]:
                                hiScores_local[i][2] = "delete";
                    hiScores_local = [x for x in hiScores_local if x[2] != "delete"]
                    hiScores_local = sorted(hiScores_local, key=lambda h: h[1], reverse=True)
                    print(hiScores_local)
                    highScoreTexts = [font.render("NAME", 1, RED), font.render("SCORE", 1, RED), font.render("ACCURACY", 1, RED)]
                    for hs in hiScores_local:
                        highScoreTexts.extend([font.render(str(hs[x]), 1, WHITE) for x in range(3)])
                        highScorePos.extend([highScoreTexts[x].get_rect(
                        topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])
                    showHiScores = True
                elif selection == 2 and id != '' :
                    req = grequests.get(url + '/get_record/')
                    res = grequests.map([req])
                    Scores = res[0].content.decode()[1:-1].split(',')
                    hiScores = []
                    for i in range(len(Scores)) :
                        if i % 3 == 0 : score_id = Scores[i][2:-1]
                        elif i % 3 == 1 : score_score = int(Scores[i][:])
                        elif i % 3 == 2:
                            score_accuracy = round(float(Scores[i][:-1])*100, 2)
                            hiScores.append([score_id, score_score, str(score_accuracy)+"%"])
                    # 중복 아이디 제거
                    hiScores = sorted(hiScores, key=lambda h: h[1])
                    for i in range(len(hiScores)-1):
                        score_id = hiScores[i][0]
                        for j in range(i+1, len(hiScores)):
                            if score_id == hiScores[j][0]:
                                hiScores[i][2] = "delete";
                    hiScores = [x for x in hiScores if x[2] != "delete"]
                    hiScores = sorted(hiScores, key=lambda h: h[1], reverse=True)
                    print(hiScores)
                    highScoreTexts = [font.render("NAME", 1, RED), font.render("SCORE", 1, RED), font.render("ACCURACY", 1, RED)]
                    for hs in hiScores:
                        highScoreTexts.extend([font.render(str(hs[x]), 1, WHITE) for x in range(3)])
                        highScorePos.extend([highScoreTexts[x].get_rect(
                        topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])
                    showHiScores = True
                elif (selection == 5 and id == '') or (selection == 3 and id != ''):
                    soundFX = not soundFX
                    if soundFX:
                        missile_sound.play()
                    Database.setSound(int(soundFX))
                elif ((selection == 6 and id == '') or (selection == 4 and id != '')) and pygame.mixer:
                    music = not music
                    if music:
                        pygame.mixer.music.play(loops=-1)
                    else:
                        pygame.mixer.music.stop()
                    Database.setSound(int(music), music=True)
                elif (selection == 5 and id != '') and pygame.mixer:
                    data = {"id": id, "shoot": 0, "kill": 0}
                    req = grequests.post(url + '/get_achievement/', json=data)
                    res = grequests.map([req])
                    _ , shoot_record, kill_record = res[0].content.decode()[1:-1].split(',')
                    
                    for i in range(len(shoot_progress)) :
                        if int(shoot_record) < shoot_progress[i] :
                            shootText = shoot_record + " / " + str(shoot_progress[i])
                            break

                    for i in range(len(kill_progress)) :
                        if int(kill_record) < kill_progress[i] :
                            killText = kill_record + " / " + str(kill_progress[i])
                            break

                    achieveTexts = [font.render("ACHIEVEMENT NAME", 1, RED),
                                    font.render("Progress", 1, RED),
                                    font.render("shoot", 1, WHITE),
                                    font.render(shootText, 1, WHITE),
                                    font.render("kill", 1, WHITE),
                                    font.render(killText, 1, WHITE)]
                    achievePos = [achieveTexts[0].get_rect(
                                    topleft=screen.get_rect().inflate(-scr_size*0.2, -scr_size*0.2).topleft),
                                achieveTexts[1].get_rect(
                                    topright=screen.get_rect().inflate(-scr_size*0.2, -scr_size*0.2).topright)]
                    for i in range(4) :
                        achievePos.append(achieveTexts[i].get_rect(topleft=achievePos[i].bottomleft))

                    showAchievement = True
                elif (selection == 7 and id == '') or (selection == 6 and id != ''):
                     pygame.quit()
                     sys.exit()
                elif selection == 8 and id == '' and language == "ENG":
                    language = "KOR"
                elif selection == 7 and id != '' and language == "ENG":
                    language = "KOR"
                    data = {"id": id, "language": "KOR"}
                    req = grequests.post(url + '/record_language/', json=data)
                    res = grequests.map([req])
                    if req.response == None : return scr_size, level_size, ''
                    print(res[0].content)
                elif selection == 8 and id == '' and language == "KOR":
                    language = "ENG"
                elif selection == 7 and id != '' and language == "KOR":
                    language = "ENG"

                    data = {"id": id, "language": "ENG"}
                    req = grequests.post(url + '/record_language/', json=data)
                    res = grequests.map([req])
                    if req.response == None : return scr_size, level_size, ''
                    print(res[0].content)
                elif selection == 8 and id != '' :
                    return scr_size, level_size, ''

            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_UP
                  and selection > 1
                  and not showHiScores
                  and not showAchievement):
                selection -= 1
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_DOWN
                  and selection < len(menuDict)
                  and not showHiScores
                  and not showAchievement):
                selection += 1

        selectPos = selectText.get_rect(topright=menuDict[selection].topleft)

        if showHiScores:
            textOverlays = zip(highScoreTexts, highScorePos)
        elif showAchievement:
            if int(kill_record) >= 1000 :
                screen.blit(kill1000_img, kill1000Rect)
                screen.blit(kill100_img, kill100Rect)
                screen.blit(kill10_img, kill10Rect)
            elif int(kill_record) >= 100 :
                screen.blit(kill100_img, kill100Rect)
                screen.blit(kill10_img, kill10Rect)
            elif int(kill_record) >= 10 :
                screen.blit(kill10_img, kill10Rect)
            
            if int(shoot_record) >= 1000 :
                screen.blit(shoot1000_img, shoot1000Rect)
                screen.blit(shoot100_img, shoot100Rect)
                screen.blit(shoot10_img, shoot10Rect)
            elif int(shoot_record) >= 100 :
                screen.blit(shoot100_img, shoot100Rect)
                screen.blit(shoot10_img, shoot10Rect)
            elif int(shoot_record) >= 10 :
                screen.blit(shoot10_img, shoot10Rect)
                
            textOverlays = zip(achieveTexts, achievePos)
        elif id == '' :
            textOverlays = zip([startText, loginText, hiScoreText, createaccountText, fxText,
                                musicText, quitText, languageText, selectText,
                                fxOnText if soundFX else fxOffText,
                                musicOnText if music else musicOffText],
                               [startPos, loginPos, hiScorePos, createaccountPos, fxPos,
                                musicPos, quitPos, languagePos, selectPos,
                                fxOnPos if soundFX else fxOffPos,
                                musicOnPos if music else musicOffPos])
            screen.blit(title, titleRect)
        else:
            textOverlays = zip([startText, hiScoreText, fxText,

                                musicText, achievementText, quitText, languageText, logoutText, selectText,
                                fxOnText if soundFX else fxOffText,
                                musicOnText if music else musicOffText],
                               [startPos, hiScorePos, fxPos,
                                musicPos, achievementPos, quitPos, languagePos, logoutPos, selectPos,
                                fxOnPos if soundFX else fxOffPos,
                                musicOnPos if music else musicOffPos])
            screen.blit(title, titleRect)

        #Text Update
        if language == "ENG": #기본 설정 영어
            startText = font.render('START GAME', 1, WHITE)
            loginText = font.render('LOGIN', 1, WHITE)
            hiScoreText = font.render('HIGH SCORES', 1, WHITE)
            createaccountText = font.render('CREATE ACCOUNT', 1, WHITE)
            fxText = font.render('SOUND FX ', 1, WHITE)
            fxOnText = font.render('ON', 1, RED)
            fxOffText = font.render('OFF', 1, RED)
            musicText = font.render('MUSIC', 1, WHITE)
            achievementText = font.render('ACHIEVEMENTS', 1, WHITE)
            musicOnText = font.render('ON', 1, RED)
            musicOffText = font.render('OFF', 1, RED)
            quitText = font.render('QUIT', 1, WHITE)
            restartText = font.render('RESTART', 1, WHITE)
            languageText = font.render('LANGUAGE', 1, WHITE)
            logoutText = font.render('LOGOUT', 1, WHITE)
            

        if language == "KOR":
            startText = font2.render('게임 시작', 1, WHITE)
            loginText = font2.render('로그인', 1, WHITE)
            hiScoreText = font2.render('최고 점수', 1, WHITE)
            createaccountText = font2.render('계정 생성', 1, WHITE)
            fxText = font2.render('효과음 ', 1, WHITE)
            fxOnText = font2.render('켜짐', 1, RED)
            fxOffText = font2.render('꺼짐', 1, RED)
            musicText = font2.render('음악', 1, WHITE)
            achievementText = font2.render('업적', 1, WHITE)
            musicOnText = font2.render('켜짐', 1, RED)
            musicOffText = font2.render('꺼짐', 1, RED)
            quitText = font2.render('종료', 1, WHITE)
            restartText = font2.render('다시 시작', 1, WHITE)
            languageText = font2.render('언어', 1, WHITE)
            logoutText = font2.render('로그아웃', 1, WHITE)
            

        for txt, pos in textOverlays:
            screen.blit(txt, pos)

        #버튼 구현
        button1Pos = 0.08 #mode1
        button2Pos = 0.52 #mode2
        button3Pos = 0.82 #quit

        modeButton_one = Button(screen,modeImg_one,round(scr_size*button1Pos),round(scr_size*0.9),round(scr_size*0.08),round(scr_size*0.04),clickmodeImg_one,round(scr_size*(button1Pos-0.01)),round(scr_size*0.896),'mode_one') # 버튼 클릭시 실행하고 싶은 파일을 'mode_one'에 써주면 된다.
        modeButton_two = Button(screen,modeImg_two,round(scr_size*button2Pos),round(scr_size*0.9),round(scr_size*0.08),round(scr_size*0.04),clickmodeImg_two,round(scr_size*(button2Pos-0.01)),round(scr_size*0.896),'mode_two')
        quitButton = Button(screen,quitImg,round(scr_size*button3Pos),round(scr_size*0.9),round(scr_size*0.08),round(scr_size*0.04),clickQuitImg,round(scr_size*(button3Pos-0.01)),round(scr_size*0.896),'quitgame')

        if modeButton_one.lvl_size == -1 :
            return scr_size, 1, id
        if modeButton_two.lvl_size == -2 :
            return scr_size, 1.6, id

        pygame.display.flip()
        #여기까지 버튼 구현

    while ship.alive:
        clock.tick(clockTime)

        if aliensLeftThisWave >= 20:
            powerupTimeLeft -= 1
            coinTimeLeft -=1
        if powerupTimeLeft <= 0:
            powerupTimeLeft = powerupTime
            random.choice(powerupTypes)().add(powerups, allsprites)
        if coinTimeLeft <=0:
            coinTimeLeft = coinTime
            random.choice(coinTypes)().add(coingroup,allsprites)


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
            # pause 구현부분
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_p):
                inPmenu = True
                if id != '':
                    menuDict = {1: restartPos, 2: hiScorePos, 3: fxPos, 4: musicPos, 5: achievementPos , 6: quitPos}
                else:
                    menuDict = {1: restartPos, 2: hiScorePos, 3: fxPos, 4: musicPos, 5: quitPos}
                selectPos = selectText.get_rect(topright=restartPos.topleft)
                while inPmenu:
                    clock.tick(clockTime)
                    screen.blit(
                        background, (0, 0), area=pygame.Rect(
                            0, backgroundLoc, scr_size, scr_size))
                    backgroundLoc -= speed
                    if backgroundLoc - speed <= speed:
                        backgroundLoc = scr_size*3

                    ###
                    for event in pygame.event.get():
                        if (event.type == pygame.QUIT):
                            pygame.quit()
                            sys.exit()
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_RETURN): # K_RETURN은 enter누르면
                            if showHiScores:
                                showHiScores = False
                            elif showAchievement :
                                showAchievement = False
                            elif selection == 1:
                                inPmenu = False
                                break
                            elif selection == 2 and id == '' :
                                hiScores = Database.getScores()
                                hiScores_local = []
                                for i in range(len(hiScores)):
                                    score_id = hiScores[i][0]
                                    score_score = hiScores[i][1]
                                    score_accuracy = round(float(hiScores[i][2])*100, 2)
                                    hiScores_local.append([score_id, score_score, str(score_accuracy)+"%"])
                                # 중복 아이디 제거
                                hiScores_local = sorted(hiScores_local, key=lambda h: h[1])
                                for i in range(len(hiScores_local)-1):
                                    score_id = hiScores_local[i][0]
                                    for j in range(i+1, len(hiScores_local)):
                                        if score_id == hiScores_local[j][0]:
                                            hiScores_local[i][2] = "delete";
                                hiScores_local = [x for x in hiScores_local if x[2] != "delete"]
                                hiScores_local = sorted(hiScores_local, key=lambda h: h[1], reverse=True)
                                print(hiScores_local)
                                highScoreTexts = [font.render("NAME", 1, RED), font.render("SCORE", 1, RED), font.render("ACCURACY", 1, RED)]
                                for hs in hiScores_local:
                                    highScoreTexts.extend([font.render(str(hs[x]), 1, WHITE) for x in range(3)])
                                    highScorePos.extend([highScoreTexts[x].get_rect(
                                    topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])
                                showHiScores = True
                            elif selection == 2 and id != '' :
                                req = grequests.get(url + '/get_record/')
                                res = grequests.map([req])
                                Scores = res[0].content.decode()[1:-1].split(',')
                                hiScores = []
                                for i in range(len(Scores)) :
                                    if i % 3 == 0 : score_id = Scores[i][2:-1]
                                    elif i % 3 == 1 : score_score = int(Scores[i][:])
                                    elif i % 3 == 2:
                                        score_accuracy = round(float(Scores[i][:-1])*100, 2)
                                        hiScores.append([score_id, score_score, str(score_accuracy)+"%"])
                                # 중복 아이디 제거
                                hiScores = sorted(hiScores, key=lambda h: h[1])
                                for i in range(len(hiScores)-1):
                                    score_id = hiScores[i][0]
                                    for j in range(i+1, len(hiScores)):
                                        if score_id == hiScores[j][0]:
                                            hiScores[i][2] = "delete";
                                hiScores = [x for x in hiScores if x[2] != "delete"]
                                hiScores = sorted(hiScores, key=lambda h: h[1], reverse=True)
                                print(hiScores)
                                highScoreTexts = [font.render("NAME", 1, RED), font.render("SCORE", 1, RED), font.render("ACCURACY", 1, RED)]
                                for hs in hiScores:
                                    highScoreTexts.extend([font.render(str(hs[x]), 1, WHITE) for x in range(3)])
                                    highScorePos.extend([highScoreTexts[x].get_rect(
                                    topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])
                                showHiScores = True
                            elif selection == 3:
                                soundFX = not soundFX
                                if soundFX:
                                    missile_sound.play()
                                Database.setSound(int(soundFX))
                            elif selection == 4 and pygame.mixer:
                                music = not music
                                if music:
                                    pygame.mixer.music.play(loops=-1)
                                else:
                                    pygame.mixer.music.stop()
                                Database.setSound(int(music), music=True)
                            elif selection == 5 and id != '':
                                showAchievement = True
                            elif selection == 5 and id == '':
                                pygame.quit()
                                sys.exit()
                            elif selection == 6 and id != '':
                                pygame.quit()
                                sys.exit()
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_UP
                            and selection > 1
                            and not showHiScores
                            and not showAchievement):
                            selection -= 1
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_DOWN
                            and selection < len(menuDict)
                            and not showHiScores
                            and not showAchievement):
                            selection += 1

                    selectPos = selectText.get_rect(topright=menuDict[selection].topleft)

                    if showHiScores:
                        textOverlays = zip(highScoreTexts, highScorePos)
                    elif showAchievement:
                        if int(kill_record) >= 1000 :
                            screen.blit(kill1000_img, kill1000Rect)
                            screen.blit(kill100_img, kill100Rect)
                            screen.blit(kill10_img, kill10Rect)
                        elif int(kill_record) >= 100 :
                            screen.blit(kill100_img, kill100Rect)
                            screen.blit(kill10_img, kill10Rect)
                        elif int(kill_record) >= 10 :
                            screen.blit(kill10_img, kill10Rect)
                        
                        if int(shoot_record) >= 1000 :
                            screen.blit(shoot1000_img, shoot1000Rect)
                            screen.blit(shoot100_img, shoot100Rect)
                            screen.blit(shoot10_img, shoot10Rect)
                        elif int(shoot_record) >= 100 :
                            screen.blit(shoot100_img, shoot100Rect)
                            screen.blit(shoot10_img, shoot10Rect)
                        elif int(shoot_record) >= 10 :
                            screen.blit(shoot10_img, shoot10Rect)

                        textOverlays = zip(achieveTexts, achievePos)
                    elif id == '':
                        textOverlays = zip([restartText, hiScoreText, fxText,
                                            musicText, quitText, selectText,
                                            fxOnText if soundFX else fxOffText,
                                            musicOnText if music else musicOffText],
                                        [restartPos, hiScorePos, fxPos,
                                            musicPos, quitPos, selectPos,
                                            fxOnPos if soundFX else fxOffPos,
                                            musicOnPos if music else musicOffPos])
                        screen.blit(pause, pauseRect)
                    else:
                        textOverlays = zip([restartText, hiScoreText, fxText,
                                            musicText, achievementText, quitText, selectText,
                                            fxOnText if soundFX else fxOffText,
                                            musicOnText if music else musicOffText],
                                        [restartPos, hiScorePos, fxPos,
                                            musicPos, achievementPos, quitPos, selectPos,
                                            fxOnPos if soundFX else fxOffPos,
                                            musicOnPos if music else musicOffPos])
                        screen.blit(pause, titleRect)
                    for txt, pos in textOverlays:
                        screen.blit(txt, pos)
                    pygame.display.flip()
            # 코인 구매 구현
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_i and aliensLeftThisWave <=0 and betweenWaveCount > 0):
                inCoin = True
                ItemDict = {1: continuePos, 2: bombItemPos, 3: shieldPos, 4: doublePos}
                shield_limit = 0
                selectItemPos = pygame.Rect(0,0,selectItem.get_width(), selectItem.get_height())
                selectItemPos.centerx = scr_size * 0.2
                selectItemPos.centerx = scr_size * 0.8
                shield_on = False
                double_on = False
                while inCoin:
                    clock.tick(clockTime)
                    bombCoinText = font.render("Bombs: " + str(bombsHeld), 1, WHITE)
                    coinShopText = font.render("Coins: "+ str(coinsHeld),1,WHITE)
                    bombCoinPos = bombCoinText.get_rect(bottomleft=screen.get_rect().bottomleft)
                    coinShopPos = coinShopText.get_rect(bottomright=screen.get_rect().bottomright)  
                    screen.blit(
                        background, (0, 0), area=pygame.Rect(
                            0, backgroundLoc, scr_size, scr_size))
                    backgroundLoc -= speed
                    if backgroundLoc - speed <= speed:
                        backgroundLoc = scr_size*3

                    for event in pygame.event.get():
                        if (event.type == pygame.QUIT):
                            pygame.quit()
                            sys.exit()
                        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                            if selection == 1:
                                inCoin = False
                                break
                            elif selection == 2:    
                                if coinsHeld >0:
                                    bombsHeld +=1
                                    coinsHeld -=1
                                else:
                                    continue
                            elif selection == 3:
                                if (coinsHeld>0 and shield_limit==0) :
                                    ship.shieldUp = True
                                    shield_on = True
                                    coinsHeld -=1
                                    shield_limit +=1
                                else:
                                    continue
                            elif selection == 4 :
                                if coinsHeld >0 :
                                    coinsHeld -=1
                                    doublemissile = True
                                    double_on = True
                                else:
                                    continue
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_LEFT
                            and selection > 1):
                            selection -= 1
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_RIGHT
                            and selection < len(ItemDict)):
                            selection += 1
                    
                    selectItemPos = selectItem.get_rect(midtop = ItemDict[selection].midbottom)

                    if not shield_on :
                        screen.blit(shield_img, shieldRect)
                    elif shield_on: 
                        screen.blit(shield_on_img,shieldOnRect)
                    if not double_on:
                        screen.blit(double_img, doubleRect)
                    elif double_on:
                        screen.blit(double_on_img, doubleOnRect)
                    
                    textOverlays = zip([continueText,bombText_Item,shieldText,doubleText,selectItem,bombCoinText,coinShopText],
                                    [continuePos,bombItemPos,shieldPos,doublePos,selectItemPos,bombCoinPos,coinShopPos])
                    screen.blit(next, nextRect)
                    screen.blit(continue_img, continueRect)
                    screen.blit(bomb_img, bombRect)
                    
                    for txt, pos in textOverlays:
                        screen.blit(txt, pos)
                    pygame.display.flip()


     # Collision Detection
        # Aliens
        for alien in Alien.active:
            for bomb in bombs:
                if pygame.sprite.collide_circle(
                        bomb, alien) and alien in Alien.active:
                    alien.table()
                    Explosion.position(alien.rect.center)
                    missilesFired += 1
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
                    if soundFX:
                        alien_explode_sound.play()
            for missile in Missile.active:
                if pygame.sprite.collide_rect(
                        missile, alien) and alien in Alien.active:
                    alien.table()
                    missile.table()
                    Explosion.position(alien.rect.center)
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
                    if soundFX:
                        alien_explode_sound.play()
            if pygame.sprite.collide_rect(alien, ship):
                if ship.shieldUp:
                    alien.table()
                    Explosion.position(alien.rect.center)
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
                    missilesFired += 1
                    ship.shieldUp = False
                else:
                    # life 구현 부분
                    if ship.lives ==1:
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

        # PowerUps
        for powerup in powerups:
            if pygame.sprite.collide_circle(powerup, ship):
                if powerup.pType == 'bomb':
                    bombsHeld += 1
                elif powerup.pType == 'shield':
                    ship.shieldUp = True
                elif powerup.pType == 'doublemissile':
                    doublemissile = True
                powerup.kill()
            elif powerup.rect.top > powerup.area.bottom:
                powerup.kill()
        # coin Drop부분
        for coin in coingroup:
            if pygame.sprite.collide_circle(coin, ship):
                if coin.pType == 'coin':
                    coinsHeld +=1
                elif coin.pType =='coin2':
                    coinsHeld +=2
                coin.kill()
            elif coin.rect.top > coin.area.bottom:
                coin.kill()

     # Update Aliens
        if curTime <= 0 and aliensLeftThisWave > 0:
            Alien.position()
            curTime = alienPeriod
        elif curTime > 0:
            curTime -= 1

     # Update text overlays
        waveText = font.render("Wave: " + str(wave), 1, WHITE)
        leftText = font.render("Aliens Left: " + str(aliensLeftThisWave),
                               1, WHITE)
        scoreText = font.render("Score: " + str(score), 1, WHITE)
        bombText = font.render("Bombs: " + str(bombsHeld), 1, WHITE)
        coinText = font.render("Coins: "+ str(coinsHeld),1,WHITE)

        wavePos = waveText.get_rect(topleft=screen.get_rect().topleft)
        leftPos = leftText.get_rect(midtop=screen.get_rect().midtop)
        scorePos = scoreText.get_rect(topright=screen.get_rect().topright)
        bombPos = bombText.get_rect(bottomleft=screen.get_rect().bottomleft)
        coinPos = coinText.get_rect(bottomright=screen.get_rect().bottomright)

        text = [waveText, leftText, scoreText, bombText,coinText]
        textposition = [wavePos, leftPos, scorePos, bombPos,coinPos]

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
     # Detertmine when to move to next wave
        if aliensLeftThisWave <= 0:  
            if betweenWaveCount > 0:
                betweenWaveCount -= 1
                nextWaveText = font.render(
                    'Wave ' + str(wave + 1) + ' in', 1, WHITE)
                nextWaveNum = font.render(
                    str((betweenWaveCount // clockTime) + 1), 1, WHITE)
                shopText = font.render('Item Shop : Press I',1,WHITE)
                text.extend([nextWaveText, nextWaveNum,shopText])
                nextWavePos = nextWaveText.get_rect(
                    center=screen.get_rect().center)
                nextWaveNumPos = nextWaveNum.get_rect(
                    midtop=nextWavePos.midbottom)
                shopPos = shopText.get_rect(midtop=nextWaveNumPos.midbottom)
                textposition.extend([nextWavePos, nextWaveNumPos,shopPos])
                if wave % 4 == 0:
                    speedUpText = font.render('SPEED UP!', 1, RED)
                    speedUpPos = speedUpText.get_rect(
                        midtop=nextWaveNumPos.midbottom)
                    text.append(speedUpText)
                    textposition.append(speedUpPos)
            elif betweenWaveCount == 0:
                if wave % 4 == 0:
                    speed += 0.5
                    MasterSprite.speed = speed
                    ship.initializeKeys()
                    aliensThisWave = 10
                    aliensLeftThisWave = Alien.numOffScreen = aliensThisWave
                else:
                    aliensThisWave *= 2
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
                if showHiScores:
                    textOverlays = zip(highScoreTexts, highScorePos)
                elif showAchievement:
                    if int(kill_record) >= 1000 :
                        screen.blit(kill1000_img, kill1000Rect)
                        screen.blit(kill100_img, kill100Rect)
                        screen.blit(kill10_img, kill10Rect)
                    elif int(kill_record) >= 100 :
                        screen.blit(kill100_img, kill100Rect)
                        screen.blit(kill10_img, kill10Rect)
                    elif int(kill_record) >= 10 :
                        screen.blit(kill10_img, kill10Rect)
                    
                    if int(shoot_record) >= 1000 :
                        screen.blit(shoot1000_img, shoot1000Rect)
                        screen.blit(shoot100_img, shoot100Rect)
                        screen.blit(shoot10_img, shoot10Rect)
                    elif int(shoot_record) >= 100 :
                        screen.blit(shoot100_img, shoot100Rect)
                        screen.blit(shoot10_img, shoot10Rect)
                    elif int(shoot_record) >= 10 :
                        screen.blit(shoot10_img, shoot10Rect)

                    textOverlays = zip(achieveTexts, achievePos)
                else:
                    textOverlays = zip([restartText, hiScoreText, fxText,
                                        musicText, achievementText, quitText, selectText,
                                        fxOnText if soundFX else fxOffText,
                                        musicOnText if music else musicOffText],
                                    [restartPos, hiScorePos, fxPos,
                                        musicPos, achievementPos, quitPos, selectPos,
                                        fxOnPos if soundFX else fxOffPos,
                                        musicOnPos if music else musicOffPos])
                    screen.blit(pause, titleRect)
                for txt, pos in textOverlays:
                    screen.blit(txt, pos)
                pygame.display.flip()
        textOverlays = zip(text, textposition)

     # Update and draw all sprites and text
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, scr_size, scr_size))
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = scr_size*3
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()

        for txt, pos in textOverlays:
            screen.blit(txt, pos)
        # life 구현
        ship.draw_lives(screen,scr_size-80,scr_size/50)
        pygame.display.flip()

    accuracy = round(score / missilesFired, 4) if missilesFired > 0 else 0.0
    isHiScore = len(hiScores) < Database.numScores or score > hiScores[-1][1]
    if showLogin or showCreateaccount :
        isHiScore = False
    name = ''
    nameBuffer = []
    idBuffer = []
    password = ''
    pwBuffer = []
    is_input_id = True

    while True:
        clock.tick(clockTime)
        # login event handling
        if showLogin == True :
            for event in pygame.event.get():
                if is_input_id :
                    if (event.type == pygame.QUIT
                        or not showLogin
                        and event.type == pygame.KEYDOWN
                            and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    elif (event.type == pygame.KEYDOWN
                        and event.key in Keyboard.keys.keys()
                        and len(idBuffer) < 8):
                        idBuffer.append(Keyboard.keys[event.key])
                        id = ''.join(idBuffer)
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_BACKSPACE
                        and len(idBuffer) > 0):
                        idBuffer.pop()
                        id = ''.join(idBuffer)
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_RETURN
                        and len(id) > 0):
                        is_input_id = False
                else :
                    if (event.type == pygame.QUIT
                        or not showLogin
                        and event.type == pygame.KEYDOWN
                            and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    elif (event.type == pygame.KEYDOWN
                        and event.key in Keyboard.keys.keys()
                        and len(pwBuffer) < 3):
                        pwBuffer.append(Keyboard.keys[event.key])
                        password = ''.join(pwBuffer)
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_BACKSPACE
                        and len(pwBuffer) > 0):
                        pwBuffer.pop()
                        password = ''.join(pwBuffer)
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_RETURN
                        and len(password) > 0):
                        is_input_id, inMenu, ship.alive, showLogin = True, True, True, False
                        data = {"id": id, "password": password}
                        req = grequests.post(url + '/login/', json=data)
                        res = grequests.map([req])
                        if req.response == None : return scr_size, level_size, ''
                        print(res[0].content)
                        if res[0].content == b'"Login Successed"' :
                            print('login successed')
                            return scr_size, level_size, id
                        else :
                            print('login failed')
                            return scr_size, level_size, ''

        elif showCreateaccount == True :
            for event in pygame.event.get():
                if is_input_id :
                    if (event.type == pygame.QUIT
                        or not showCreateaccount
                        and event.type == pygame.KEYDOWN
                            and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    elif (event.type == pygame.KEYDOWN
                        and event.key in Keyboard.keys.keys()
                        and len(idBuffer) < 8):
                        idBuffer.append(Keyboard.keys[event.key])
                        id = ''.join(idBuffer)
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_BACKSPACE
                        and len(idBuffer) > 0):
                        idBuffer.pop()
                        id = ''.join(idBuffer)
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_RETURN
                        and len(id) > 0):
                        is_input_id = False

                else :
                    if (event.type == pygame.QUIT
                        or not showCreateaccount
                        and event.type == pygame.KEYDOWN
                            and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                    elif (event.type == pygame.KEYDOWN
                        and event.key in Keyboard.keys.keys()
                        and len(pwBuffer) < 3):
                        pwBuffer.append(Keyboard.keys[event.key])
                        password = ''.join(pwBuffer)
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_BACKSPACE
                        and len(pwBuffer) > 0):
                        pwBuffer.pop()
                        password = ''.join(pwBuffer)
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_RETURN
                        and len(password) > 0):
                        is_input_id, inMenu, ship.alive, showCreateaccount = True, True, True, False
                        data = {"id": id, "password": password}
                        req = grequests.post(url + "/create_account/", json=data)
                        res = grequests.map([req])
                        if req.response == None : return scr_size, level_size, ''
                        print(res[0].content)
                        if res[0].content == b'"Account created"' :
                            print('Account created')
                            return scr_size, level_size, ''
                        else :
                            print('Exist same ID')
                            return scr_size, level_size, ''


        # hiscore event handling
        elif id == '' :
            for event in pygame.event.get():
                if (event.type == pygame.QUIT
                    or not isHiScore
                    and event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                    and not isHiScore):
                    return scr_size, level_size
                elif (event.type == pygame.KEYDOWN
                    and event.key in Keyboard.keys.keys()
                    and len(nameBuffer) < 8):
                    nameBuffer.append(Keyboard.keys[event.key])
                    name = ''.join(nameBuffer)
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_BACKSPACE
                    and len(nameBuffer) > 0):
                    nameBuffer.pop()
                    name = ''.join(nameBuffer)
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                    and len(name) > 0):
                    Database.setScore(hiScores, (name, score, accuracy))
                    return scr_size, level_size, id

        else : # 로그인 상태 기록 저장(화면을 만들어야 함)
            data = {"id": id, "score": score, "accuracy": accuracy}
            req = grequests.post(url + '/save_record/', json=data)
            res = grequests.map([req])
            if req.response == None : return scr_size, level_size, ''
            print(res[0].content)
            data = {"id": id, "shoot": shoot_count, "kill": kill_count}
            req = grequests.post(url + '/record_achievement/', json=data)
            res = grequests.map([req])
            if req.response == None : return scr_size, level_size, ''
            print(res[0].content)
            return scr_size, level_size, id

        if isHiScore: # 로그인 상태일 때, 수정 필요
            hiScoreText = font.render('HIGH SCORE!', 1, RED)
            hiScorePos = hiScoreText.get_rect(
                midbottom=screen.get_rect().center)
            scoreText = font.render(str(score), 1, WHITE)
            scorePos = scoreText.get_rect(midtop=hiScorePos.midbottom)
            enterNameText = font.render('ENTER YOUR NAME:', 1, RED)
            enterNamePos = enterNameText.get_rect(midtop=scorePos.midbottom)
            nameText = font.render(name, 1, WHITE)
            namePos = nameText.get_rect(midtop=enterNamePos.midbottom)
            textOverlay = zip([hiScoreText, scoreText,
                               enterNameText, nameText],
                              [hiScorePos, scorePos,
                               enterNamePos, namePos])

        elif showLogin or showCreateaccount:
            idText = font.render('ID', 1, RED)
            idPos = idText.get_rect(
                midbottom=screen.get_rect().center)
            inputidText = font.render(id, 1, WHITE)
            inputidPos = inputidText.get_rect(midtop=idPos.midbottom)
            pwText = font.render('PASSWORD', 1, RED)
            pwPos = pwText.get_rect(midtop=inputidPos.midbottom)
            inputpwText = font.render(password, 1, WHITE)
            inputpwPos = inputpwText.get_rect(midtop=pwPos.midbottom)
            textOverlay = zip([idText, inputidText,
                               pwText, inputpwText],
                              [idPos, inputidPos,
                               pwPos, inputpwPos])

        elif id == '':
            gameOverText = font.render('GAME OVER', 1, WHITE)
            gameOverPos = gameOverText.get_rect(
                center=screen.get_rect().center)
            scoreText = font.render('SCORE: {}'.format(score), 1, WHITE)
            scorePos = scoreText.get_rect(midtop=gameOverPos.midbottom)
            textOverlay = zip([gameOverText, scoreText],
                              [gameOverPos, scorePos])

    # Update and draw all sprites
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, scr_size, scr_size))
        backgroundLoc -= speed
        if backgroundLoc - speed <= 0:
            backgroundLoc = scr_size*3
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()
        for txt, pos in textOverlay:
            screen.blit(txt, pos)
        pygame.display.flip()
