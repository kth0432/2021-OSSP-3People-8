from os import kill
import pygame
import random
from collections import deque
import sys
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

url = "http://osspcshooting.shop"

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
        speed = scr_size*0.004
        background = scr_size*4
        backgroundLoc = scr_size*3
        star_seq = round(scr_size*0.06)
        star_s = round(scr_size*0.004)
        star_l = round(scr_size*0.01)
        font_eng = round(scr_size*0.065)
        font_kor =  round(scr_size*0.045)
        toppos = scr_size*0.2
        coinnextx = scr_size*0.005
        coinnexty = scr_size*0.004
        ratio = scr_size*0.002
        middletoppos = scr_size*0.35
        topendpos = scr_size*0.15
        middlepos = scr_size*0.5
        cointoppos = scr_size*0.25
        coinpos = scr_size*0.7
        coinxonepos = scr_size*0.2
        coinxtwopos = scr_size*0.4
        coinxthreepos = scr_size*0.6
        coinxfourpos = scr_size*0.8
        coinypose = scr_size*0.8
        achievement = scr_size/3000
        achievementpos = scr_size*0.25
        hi_achievement = scr_size*0.0001
        hi_achievementx = scr_size*0.3
        hi_achievementx2 = scr_size*0.35
        hi_achievementy = scr_size*0.16
        hi_achievementy_seq = scr_size*0.043
        selectitemposx = scr_size*0.2
        selectitemposy = scr_size*0.5
        button1pos_1 = round(scr_size*0.08)
        button2pos_1 = round(scr_size*0.44)
        button3pos_1 = round(scr_size*0.75)
        buttonpos_2 = round(scr_size*0.9)
        buttonpos_3 = round(scr_size*0.25)
        buttonpos_4 = round(scr_size*0.1)
        button1pos_1_ad = round(scr_size*0.07)
        button2pos_1_ad = round(scr_size*0.43)
        button3pos_1_ad = round(scr_size*0.74)
        button_ad = round(scr_size*0.896)
        lifex = scr_size * 0.82
        lifey = scr_size * 0.04

    def achievement_posx(i) :
        return 1 + i%3
    def achievement_posy(i) :
        return 2 + (i+1)//3

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

    def achievement_blit(screen, shoot_record, kill_record) :
        for i in range(len(shoot_imgset)) :
            if int(shoot_record) >= shoot_progress[i] :
                screen.blit(shoot_img[i], shoot_rect[i])
            if int(kill_record) >= kill_progress[i] :
                screen.blit(kill_img[i], kill_rect[i])
        return screen

    def remove_id_overlap(hiScores) :
        # 중복 아이디 제거
        hiScores = sorted(hiScores, key=lambda h: h[1])
        for i in range(len(hiScores)-1):
            score_id = hiScores[i][0]
            for j in range(i+1, len(hiScores)):
                if score_id == hiScores[j][0]:
                    hiScores[i][2] = "delete"
        hiScores = [x for x in hiScores if x[2] != "delete"]
        hiScores = sorted(hiScores, key=lambda h: h[1], reverse=True)
        return hiScores


    def get_hiscores(highScoreTexts, highScorePos) :
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
        hiScores = remove_id_overlap(hiScores)
        if language == 'ENG' :
            highScoreTexts = [font.render("NAME", 1, RED), font.render("SCORE", 1, RED), font.render("ACCURACY", 1, RED)]
        else :
            highScoreTexts = [font2.render("이름", 1, RED), font2.render("점수", 1, RED), font2.render("정확도", 1, RED)]
        for hs in hiScores:
            highScoreTexts.extend([font.render(str(hs[x]), 1, WHITE) for x in range(3)])
            highScorePos.extend([highScoreTexts[x].get_rect(
            topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])
        showHiScores = True

        req = grequests.get(url + '/get_achievementlist/')
        res = grequests.map([req])
        achievement = res[0].content.decode()[1:-1].split(',')
        achievement_set = []
        for i in range(len(achievement)) :
            if i % 3 == 0 : achievement_id = str(achievement[i][2:-1])
            elif i % 3 == 1 : achievement_shoot = int(achievement[i][:])
            elif i % 3 == 2 :
                achievement_kill = int(achievement[i][:-1])
                achievement_set.append([achievement_id, achievement_shoot, achievement_kill])

        for score in hiScores :
            for id in achievement_set :
                if score[0] == id[0] :
                    score.append(id[1])
                    score.append(id[2])
        print(hiScores)

        hi_achievement_img = []
        hi_achievement_rect = []
        for i in range(len(hiScores)) :
            for j in range(len(shoot_imgset)-1, -1, -1) :
                if len(hiScores[i]) > 3 and hiScores[i][3] >= shoot_progress[j] :
                    img, rec = load_image(shoot_imgset[j])
                    img = pygame.transform.scale(img, (round(img.get_width()*size.hi_achievement), round(img.get_height()*size.hi_achievement)))
                    rec = pygame.Rect(0, 0, img.get_width(), img.get_height())
                    rec.centerx = size.hi_achievementx
                    rec.centery = size.hi_achievementy + size.hi_achievementy_seq * i
                    hi_achievement_img.append(img)
                    hi_achievement_rect.append(rec)
                    break

        for i in range(len(hiScores)) :
            for j in range(len(kill_imgset)-1, -1, -1) :
                if len(hiScores[i]) > 3 and hiScores[i][4] >= kill_progress[j] :
                    img, rec = load_image(kill_imgset[j])
                    img = pygame.transform.scale(img, (round(img.get_width()*size.hi_achievement), round(img.get_height()*size.hi_achievement)))
                    rec = pygame.Rect(0, 0, img.get_width(), img.get_height())
                    rec.centerx = size.hi_achievementx2
                    rec.centery = size.hi_achievementy + size.hi_achievementy_seq * i
                    hi_achievement_img.append(img)
                    hi_achievement_rect.append(rec)
                    break

        return highScoreTexts, highScorePos, showHiScores, hi_achievement_img, hi_achievement_rect

    def background_update(screen, background, backgroundLoc) :
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, scr_size, scr_size))
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

    def set_achievetext(shoot_record, kill_record, achieveTexts) :

        for i in range(len(shoot_progress)) :
            if int(shoot_record) < shoot_progress[i] :
                achieveTexts[3] = font.render(shoot_record + " / " + str(shoot_progress[i]), 1, WHITE)
                break

        for i in range(len(kill_progress)) :
            if int(kill_record) < kill_progress[i] :
                achieveTexts[5] = font.render(kill_record + " / " + str(kill_progress[i]), 1, WHITE)
                break

        return achieveTexts

    def ingame_text_update(language) :
        if language == "ENG" :
            return [font.render("Wave: " + str(wave), 1, WHITE),
                    font.render("Remaining Aliens: " + str(aliensLeftThisWave), 1, WHITE),
                    font.render("Score: " + str(score), 1, WHITE),
                    font.render("Bombs: " + str(bombsHeld), 1, WHITE),
                    font.render("Coins: "+ str(coinsHeld), 1, WHITE)]

        else :
            return [font2.render("웨이브: " + str(wave), 1, WHITE),
                    font2.render("적 남은 수: " + str(aliensLeftThisWave), 1, WHITE),
                    font2.render("점수: " + str(score), 1, WHITE),
                    font2.render("폭탄: " + str(bombsHeld), 1, WHITE),
                    font2.render("코인: "+ str(coinsHeld), 1, WHITE)]

    def get_achieve_record(id) :
        data = {"id": id, "shoot": 0, "kill": 0}
        req = grequests.post(url + '/get_achievement/', json=data)
        res = grequests.map([req])
        _ , shoot_record, kill_record = res[0].content.decode()[1:-1].split(',')

        return shoot_record, kill_record

    shoot_progress = [10, 100, 1000]
    kill_progress = [10, 100, 1000]
    id_len = 8
    pw_len = 3

    direction = {None: (0, 0), pygame.K_UP: (0, -size.speed), pygame.K_DOWN: (0, size.speed),
             pygame.K_LEFT: (-size.speed, 0), pygame.K_RIGHT: (size.speed, 0)}

    # Initialize everything
    pygame.mixer.pre_init(11025, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((scr_size, scr_size), pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
    pygame.display.set_caption('Shooting Game')
    pygame.mouse.set_visible(True)

# Create the background which will scroll and loop over a set of different
# size stars
    background = pygame.Surface((scr_size, size.background))
    background = background.convert()
    background.fill(BLACK)

    backgroundLoc = size.backgroundLoc
    finalStars = deque()
    for y in range(0, size.backgroundLoc, size.star_seq):
        starsize = random.randint(size.star_s, size.star_l)
        x = random.randint(0, scr_size - starsize)
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

    aliennum = 20 # 아이템 나오는 alien 숫자(aliennum 이상 남은 경우)
    setaliennum = 10 # 4웨이브마다 초기 웨이브 수
    speedup = 0.5 # 4웨이브마다 speed += speedup
    aliennumup = 2 # 4웨이브 주기로 alienthiswave = int(alienthiswave * aliennumup)

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
    font = pygame.font.Font(None, size.font_eng)
    font2 = pygame.font.SysFont('hy견고딕', size.font_kor)
    inMenu = True

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

    title, titleRect = load_image('title.png')
    title = pygame.transform.scale(title, (round(title.get_width()*size.ratio), round(title.get_height()*size.ratio)))
    titleRect = pygame.Rect(0, 0, title.get_width(), title.get_height())
    pause,pauseRect = load_image('pause.png',WHITE)
    pause = pygame.transform.scale(pause, (round(pause.get_width()*size.ratio), round(pause.get_height()*size.ratio)))
    pauseRect = pygame.Rect(0, 0, pause.get_width(), pause.get_height())
    titleRect.midtop = screen.get_rect().inflate(0, -size.middletoppos).midtop
    pauseRect.midtop = screen.get_rect().inflate(0, -size.middletoppos).midtop

    text_eng_set = [font.render('START GAME', 1, WHITE),
                    font.render('LOGIN', 1, WHITE),
                    font.render('HIGH SCORES', 1, WHITE),
                    font.render('CREATE ACCOUNT', 1, WHITE),
                    font.render('SOUND FX ', 1, WHITE),
                    font.render('ON', 1, RED),
                    font.render('OFF', 1, RED),
                    font.render('MUSIC', 1, WHITE),
                    font.render('ACHIEVEMENTS', 1, WHITE),
                    font.render('ON', 1, RED),
                    font.render('OFF', 1, RED),
                    font.render('QUIT', 1, WHITE),
                    font.render('RESTART', 1, WHITE),
                    font.render('LANGUAGE', 1, WHITE),
                    font.render('LOGOUT', 1, WHITE),
                    [font.render("ACHIEVEMENT NAME", 1, RED), font.render("Progress", 1, RED),
                    font.render("shoot", 1, WHITE), font.render("0", 1, WHITE),
                    font.render("kill", 1, WHITE), font.render("0", 1, WHITE)],
                    font.render('ID', 1, RED),
                    font.render('PASSWORD', 1, RED),
                    font.render('GAME OVER', 1, WHITE),
                    font.render('SPEED UP!', 1, RED)]

    text_kor_set = [font2.render('게임 시작', 1, WHITE),
                    font2.render('로그인', 1, WHITE),
                    font2.render('최고 점수', 1, WHITE),
                    font2.render('계정 생성', 1, WHITE),
                    font2.render('효과음        ', 1, WHITE),
                    font2.render('켜짐      ', 1, RED),
                    font2.render('꺼짐', 1, RED),
                    font2.render('음악', 1, WHITE),
                    font2.render('업적', 1, WHITE),
                    font2.render('켜짐', 1, RED),
                    font2.render('꺼짐', 1, RED),
                    font2.render('종료', 1, WHITE),
                    font2.render('다시 시작', 1, WHITE),
                    font2.render('언어', 1, WHITE),
                    font2.render('로그아웃', 1, WHITE),
                    [font2.render("업적 이름", 1, RED), font2.render("진행률", 1, RED),
                    font2.render("미사일", 1, WHITE), font.render("0", 1, WHITE),
                    font2.render("처치", 1, WHITE), font.render("0", 1, WHITE)],
                    font2.render('아이디', 1, RED),
                    font2.render('비밀번호', 1, RED),
                    font2.render('게임 종료', 1, WHITE),
                    font2.render('스피드 업!', 1, RED)]

    startText, loginText, hiScoreText, createaccountText, fxText, fxOnText, fxOffText, musicText, achievementText, musicOnText, musicOffText, quitText, restartText, languageText, logoutText, achieveTexts, idText, pwText, gameOverText, speedUpText = set_language(language)
    ### 언어 설정 끝

    gameOverPos = gameOverText.get_rect(center=screen.get_rect().center)

    startPos = startText.get_rect(midtop=titleRect.inflate(0, size.topendpos).midbottom)
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

    achievePos = [achieveTexts[0].get_rect(
                    topleft=screen.get_rect().inflate(-size.toppos, -size.toppos).topleft),
                  achieveTexts[1].get_rect(
                    topright=screen.get_rect().inflate(-size.toppos, -size.toppos).topright)]
    for i in range(4) :
        achievePos.append(achieveTexts[i].get_rect(topleft=achievePos[i].bottomleft))

    # Coin shop 준비
    next,nextRect = load_image('next.png',WHITE)
    next = pygame.transform.scale(next, (round(next.get_width()*size.coinnextx), round(next.get_height()*size.coinnexty)))
    nextRect = pygame.Rect(0, 0, next.get_width(), next.get_height())
    nextRect.centerx = size.middlepos
    nextRect.centery = size.cointoppos

    continue_img,continueRect = load_image('continue.png',WHITE)
    continue_img = pygame.transform.scale(continue_img, (round(continue_img.get_width()*size.ratio), round(continue_img.get_height()*size.ratio)))
    continueRect = pygame.Rect(0, 0, continue_img.get_width(), continue_img.get_height())
    continueRect.centerx = size.coinxonepos
    continueRect.centery = size.coinpos

    bomb_img,bombRect = load_image('bomb_click.png')
    bomb_img = pygame.transform.scale(bomb_img, (round(bomb_img.get_width()*size.ratio), round(bomb_img.get_height()*size.ratio)))
    bombRect = pygame.Rect(0, 0, bomb_img.get_width(), bomb_img.get_height())
    bombRect.centerx = size.coinxtwopos
    bombRect.centery = size.coinpos

    shield_img,shieldRect = load_image('shield_click.png')
    shield_img = pygame.transform.scale(shield_img, (round(shield_img.get_width()*size.ratio), round(shield_img.get_height()*size.ratio)))
    shieldRect = pygame.Rect(0, 0, shield_img.get_width(), shield_img.get_height())
    shieldRect.centerx = size.coinxthreepos
    shieldRect.centery = size.coinpos
    # ---
    shield_on_img,shieldOnRect = load_image('ship_shield.png')
    shield_on_img = pygame.transform.scale(shield_on_img, (round(shield_on_img.get_width()*size.ratio), round(shield_on_img.get_height()*size.ratio)))
    shieldOnRect = pygame.Rect(0, 0, shield_on_img.get_width(), shield_on_img.get_height())
    shieldOnRect.centerx = size.coinxthreepos
    shieldOnRect.centery = size.coinpos

    double_img,doubleRect = load_image('doublemissile_powerup.png')
    double_img = pygame.transform.scale(double_img, (round(double_img.get_width()*size.ratio), round(double_img.get_height()*size.ratio)))
    doubleRect = pygame.Rect(0, 0, double_img.get_width(), double_img.get_height())
    doubleRect.centerx = size.coinxfourpos
    doubleRect.centery = size.coinpos
    # ---
    double_on_img,doubleOnRect = load_image('doublemissile_click.png')
    double_on_img = pygame.transform.scale(double_on_img, (round(double_on_img.get_width()*size.ratio), round(double_on_img.get_height()*size.ratio)))
    doubleOnRect = pygame.Rect(0, 0, double_on_img.get_width(), double_on_img.get_height())
    doubleOnRect.centerx = size.coinxfourpos
    doubleOnRect.centery = size.coinpos

    continueText = font.render('Continue',1,WHITE)
    continuePos = pygame.Rect(0,0,continueText.get_width(), continueText.get_height())
    continuePos.centerx = size.coinxonepos
    continuePos.centery = size.coinypose

    bombText_Item = font.render('Bomb',1,WHITE)
    bombItemPos = pygame.Rect(0,0,bombText_Item.get_width(), bombText_Item.get_height())
    bombItemPos.centerx = size.coinxtwopos
    bombItemPos.centery = size.coinypose

    shieldText = font.render('Shield',1,WHITE)
    shieldPos = pygame.Rect(0,0,shieldText.get_width(), shieldText.get_height())
    shieldPos.centerx = size.coinxthreepos
    shieldPos.centery = size.coinypose

    doubleText = font.render('Double',1,WHITE)
    doublePos = pygame.Rect(0,0,doubleText.get_width(), doubleText.get_height())
    doublePos.centerx = size.coinxfourpos
    doublePos.centery = size.coinypose

    selectItem = font.render('^',1,WHITE)
    selectItemPos = pygame.Rect(0,0,selectItem.get_width(), selectItem.get_height())
    selectItemPos.centerx = size.coinxonepos
    selectItemPos.centery = size.coinypose

    ###########

    # 업적 이미지 생성
    shoot_img = []
    shoot_rect = []
    kill_img = []
    kill_rect = []
    shoot_imgset = ['shoot_10.png', 'shoot_100.png', 'shoot_1000.png']
    kill_imgset = ['kill_10.png', 'kill_100.png', 'kill_1000.png']

    for i in range(len(shoot_imgset)) :
        img, rec = load_image(shoot_imgset[i])
        shoot_img.append(img)
        shoot_rect.append(rec)
        shoot_img[i] = pygame.transform.scale(shoot_img[i], (round(shoot_img[i].get_width()*size.achievement), round(shoot_img[i].get_height()*size.achievement)))
        shoot_rect[i] = pygame.Rect(0, 0, shoot_img[i].get_width(), shoot_img[i].get_height())
        shoot_rect[i].centerx = size.achievementpos * achievement_posx(i)
        shoot_rect[i].centery = size.achievementpos * achievement_posy(i)

    for i in range(len(kill_imgset)) :
        img, rec = load_image(kill_imgset[i])
        kill_img.append(img)
        kill_rect.append(rec)
        kill_img[i] = pygame.transform.scale(kill_img[i], (round(kill_img[i].get_width()*size.achievement), round(kill_img[i].get_height()*size.achievement)))
        kill_rect[i] = pygame.Rect(0, 0, kill_img[i].get_width(), kill_img[i].get_height())
        kill_rect[i].centerx = size.achievementpos * achievement_posx(i)
        kill_rect[i].centery = size.achievementpos + size.achievementpos * achievement_posy(i)

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
    modeImg_one = pygame.transform.scale(modeImg_one, (round(modeImg_one.get_width()*size.ratio), round(modeImg_one.get_height()*size.ratio)))
    modeImg_two = pygame.image.load("data/mode2.png")
    modeImg_two = pygame.transform.scale(modeImg_two, (round(modeImg_two.get_width()*size.ratio), round(modeImg_two.get_height()*size.ratio)))
    quitImg = pygame.image.load("data/quiticon.png")
    quitImg = pygame.transform.scale(quitImg, (round(quitImg.get_width()*size.ratio), round(quitImg.get_height()*size.ratio)))
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
        scr_x , scr_y = pygame.display.get_surface().get_size()
        if scr_size != scr_x or scr_size != scr_y :
            return min(scr_x, scr_y), level_size, id, language    # 메뉴화면에서만 창 사이즈 크기 확인하고, 변경되면 main 재시작
        clock.tick(clockTime)

        screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)

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
                    hiScores_local = remove_id_overlap(hiScores_local)
                    if language == 'ENG' :
                        highScoreTexts = [font.render("NAME", 1, RED), font.render("SCORE", 1, RED), font.render("ACCURACY", 1, RED)]
                    else :
                        highScoreTexts = [font2.render("이름", 1, RED), font2.render("점수", 1, RED), font2.render("정확도", 1, RED)]
                    for hs in hiScores_local:
                        highScoreTexts.extend([font.render(str(hs[x]), 1, WHITE) for x in range(3)])
                        highScorePos.extend([highScoreTexts[x].get_rect(
                        topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])
                    showHiScores = True
                elif selection == 2 and id != '' :
                    highScoreTexts, highScorePos, showHiScores, hi_achievement_img, hi_achievement_rect = get_hiscores(highScoreTexts, highScorePos)
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
                    shoot_record, kill_record = get_achieve_record(id)
                    achieveTexts = set_achievetext(shoot_record, kill_record, achieveTexts)
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
                    if req.response == None : return scr_size, level_size, '', language
                    print(res[0].content)
                elif selection == 8 and id == '' and language == "KOR":
                    language = "ENG"
                elif selection == 7 and id != '' and language == "KOR":
                    language = "ENG"

                    data = {"id": id, "language": "ENG"}
                    req = grequests.post(url + '/record_language/', json=data)
                    res = grequests.map([req])
                    if req.response == None : return scr_size, level_size, '', language
                    print(res[0].content)
                elif selection == 8 and id != '' :
                    return scr_size, level_size, '', language

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
            if id != '' :
                for i in range(len(hi_achievement_img)) :
                    screen.blit(hi_achievement_img[i], hi_achievement_rect[i])
        elif showAchievement:
            screen = achievement_blit(screen, shoot_record, kill_record)

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
        startText, loginText, hiScoreText, createaccountText, fxText, fxOnText, fxOffText, musicText, achievementText, musicOnText, musicOffText, quitText, restartText, languageText, logoutText, achieveTexts, idText, pwText, gameOverText, speedUpText = set_language(language)

        for txt, pos in textOverlays:
            screen.blit(txt, pos)

        #버튼 구현
        modeButton_one = Button(screen,modeImg_one,size.button1pos_1,size.buttonpos_2,size.buttonpos_3,size.buttonpos_4,clickmodeImg_one,size.button1pos_1_ad,size.button_ad,'mode_one') # 버튼 클릭시 실행하고 싶은 파일을 'mode_one'에 써주면 된다.
        modeButton_two = Button(screen,modeImg_two,size.button2pos_1,size.buttonpos_2,size.buttonpos_3,size.buttonpos_4,clickmodeImg_two,size.button2pos_1_ad,size.button_ad,'mode_two')
        quitButton = Button(screen,quitImg,size.button3pos_1,size.buttonpos_2,size.buttonpos_3,size.buttonpos_4,clickQuitImg,size.button3pos_1_ad,size.button_ad,'quitgame')

        if modeButton_one.lvl_size == -1 :
            return scr_size, mode1_lvl_size, id, language
        if modeButton_two.lvl_size == -2 :
            return scr_size, mode2_lvl_size, id, language

        pygame.display.flip()
        #여기까지 버튼 구현size.button_ad

    while ship.alive:
        clock.tick(clockTime)

        if aliensLeftThisWave >= aliennum:
            powerupTimeLeft -= 1
            coinTimeLeft -=1
        if powerupTimeLeft <= 0:
            powerupTimeLeft = powerupTime
            random.choice(powerupTypes)().add(powerups, allsprites)
        if coinTimeLeft <= 0:
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
                    screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)

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
                            elif selection == 2 and id != '' :
                                highScoreTexts, highScorePos, showHiScores, hi_achievement_img, hi_achievement_rect = get_hiscores(highScoreTexts, highScorePos)
                            elif selection == 2 and id == '' :
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

                    if showHiScores :
                        textOverlays = zip(highScoreTexts, highScorePos)
                        if id != '' :
                            for i in range(len(hi_achievement_img)) :
                                screen.blit(hi_achievement_img[i], hi_achievement_rect[i])

                    elif showAchievement:
                        shoot_record, kill_record = get_achieve_record(id)
                        achieveTexts = set_achievetext(shoot_record, kill_record, achieveTexts)
                        screen = achievement_blit(screen, shoot_record, kill_record)
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
                        screen.blit(pause, pauseRect)
                    for txt, pos in textOverlays:
                        screen.blit(txt, pos)
                    pygame.display.flip()
            # 코인 구매 구현
            elif (event.type == pygame.KEYDOWN and event.key == pygame.K_i and aliensLeftThisWave <=0 and betweenWaveCount > 0):
                inCoin = True
                ItemDict = {1: continuePos, 2: bombItemPos, 3: shieldPos, 4: doublePos}
                shield_limit = 0
                double_limit = 0
                selectItemPos = pygame.Rect(0,0,selectItem.get_width(), selectItem.get_height())
                selectItemPos.centerx = size.selectitemposx
                selectItemPos.centery = size.selectitemposy
                shield_on = False
                double_on = False
                while inCoin:
                    clock.tick(clockTime)
                    bombCoinText = font.render("Bombs: " + str(bombsHeld), 1, WHITE)
                    coinShopText = font.render("Coins: "+ str(coinsHeld),1,WHITE)
                    bombCoinPos = bombCoinText.get_rect(bottomleft=screen.get_rect().bottomleft)
                    coinShopPos = coinShopText.get_rect(bottomright=screen.get_rect().bottomright)
                    screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)

                    for event in pygame.event.get():
                        if (event.type == pygame.QUIT):
                            pygame.quit()
                            sys.exit()
                        elif (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                            if selection == 1:
                                inCoin = False
                                break
                            elif selection == 2:
                                if coinsHeld > 0:
                                    bombsHeld += 1
                                    coinsHeld -= 1
                                else:
                                    continue
                            elif selection == 3:
                                if (coinsHeld > 0 and shield_limit == 0) :
                                    ship.shieldUp = True
                                    shield_on = True
                                    coinsHeld -= 1
                                    shield_limit += 1
                                else:
                                    continue
                            elif selection == 4 :
                                if (coinsHeld > 0 and double_limit == 0) :
                                    coinsHeld -= 1
                                    doublemissile = True
                                    double_on = True
                                    double_limit += 1
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
                    aliensLeftThisWave, kill_count, score = kill_alien(alien, aliensLeftThisWave, kill_count, score)
                    if soundFX:
                        alien_explode_sound.play()
            for missile in Missile.active:
                if pygame.sprite.collide_rect(
                        missile, alien) and alien in Alien.active:
                    alien.table()
                    missile.table()
                    Explosion.position(alien.rect.center)
                    aliensLeftThisWave, kill_count, score = kill_alien(alien, aliensLeftThisWave, kill_count, score)
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
        waveText, leftText, scoreText, bombText, coinText = ingame_text_update(language)

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
                if language == 'ENG' :
                    nextWaveText = font.render('Wave ' + str(wave + 1) + ' in', 1, WHITE)
                else :
                    nextWaveText = font2.render(str(wave + 1) + ' 웨이브 남은 시간', 1, WHITE)
                nextWaveNum = font.render(
                    str((betweenWaveCount // clockTime) + 1), 1, WHITE)
                if language == 'ENG' :
                    shopText = font.render('Item Shop : Press I',1,WHITE)
                else :
                    shopText = font2.render('아이템 상점 : I를 누르세요',1,WHITE)
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
                        midtop=shopPos.midbottom)
                    text.append(speedUpText)
                    textposition.append(speedUpPos)
            elif betweenWaveCount == 0:
                if wave % 4 == 0:
                    speed += speedup
                    MasterSprite.speed = speed
                    ship.initializeKeys()
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
                if showHiScores:
                    textOverlays = zip(highScoreTexts, highScorePos)
                    for i in range(len(hi_achievement_img)) :
                        screen.blit(hi_achievement_img[i], hi_achievement_rect[i])
                elif showAchievement:
                    screen = achievement_blit(screen, shoot_record, kill_record)

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
        screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()

        for txt, pos in textOverlays:
            screen.blit(txt, pos)
        # life 구현
        ship.draw_lives(screen, size.lifex, size.lifey)
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
                        and len(idBuffer) < id_len):
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
                        and len(pwBuffer) < pw_len):
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
                        if req.response == None : return scr_size, level_size, '', language
                        if res[0].content == b'"Login Success"' :
                            data = {"id": id, "language": ''}
                            req = grequests.post(url + '/get_language/', json=data)
                            res = grequests.map([req])
                            if req.response == None : return scr_size, level_size, '', language
                            language = str(res[0].content.decode()[1:-1])
                            print('login success')
                            return scr_size, level_size, id, language
                        else :
                            print('login fail')
                            return scr_size, level_size, '', language

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
                        and len(idBuffer) < id_len):
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
                        and len(pwBuffer) < pw_len):
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
                        if req.response == None : return scr_size, level_size, '', language
                        print(res[0].content)
                        if res[0].content == b'"Account created"' :
                            print('Account created')
                            return scr_size, level_size, '', language
                        else :
                            print('Exist same ID')
                            return scr_size, level_size, '', language


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
                    return scr_size, level_size, id, language
                elif (event.type == pygame.KEYDOWN
                    and event.key in Keyboard.keys.keys()
                    and len(nameBuffer) < id_len):
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
                    return scr_size, level_size, id, language

        else : # 로그인 상태 기록 저장(화면을 만들어야 함)
            data = {"id": id, "score": score, "accuracy": accuracy}
            req = grequests.post(url + '/save_record/', json=data)
            res = grequests.map([req])
            if req.response == None : return scr_size, level_size, '', language
            print(res[0].content)
            data = {"id": id, "shoot": shoot_count, "kill": kill_count}
            req = grequests.post(url + '/record_achievement/', json=data)
            res = grequests.map([req])
            if req.response == None : return scr_size, level_size, '', language
            print(res[0].content)
            return scr_size, level_size, id, language

        if isHiScore: # 로그인 상태일 때, 수정 필요
            hiScorePos = hiScoreText.get_rect(midbottom=screen.get_rect().center)
            scoreText = font.render(str(score), 1, WHITE)
            scorePos = scoreText.get_rect(midtop=hiScorePos.midbottom)
            if language == 'ENG' :
                enterNameText = font.render('ENTER YOUR NAME:', 1, RED)
            else :
                enterNameText = font2.render('이름을 입력하세요:', 1, RED)
            enterNamePos = enterNameText.get_rect(midtop=scorePos.midbottom)
            nameText = font.render(name, 1, WHITE)
            namePos = nameText.get_rect(midtop=enterNamePos.midbottom)
            textOverlay = zip([hiScoreText, scoreText,
                               enterNameText, nameText],
                              [hiScorePos, scorePos,
                               enterNamePos, namePos])

        elif showLogin or showCreateaccount:
            idPos = idText.get_rect(midbottom=screen.get_rect().center)
            inputidText = font.render(id, 1, WHITE)
            inputidPos = inputidText.get_rect(midtop=idPos.midbottom)
            pwPos = pwText.get_rect(midtop=inputidPos.midbottom)
            inputpwText = font.render(password, 1, WHITE)
            inputpwPos = inputpwText.get_rect(midtop=pwPos.midbottom)
            textOverlay = zip([idText, inputidText,
                               pwText, inputpwText],
                              [idPos, inputidPos,
                               pwPos, inputpwPos])

        elif id == '':
            if language == 'ENG' :
                scoreText = font.render('SCORE: {}'.format(score), 1, WHITE)
            else :
                scoreText = font2.render('점수: {}'.format(score), 1, WHITE)
            scorePos = scoreText.get_rect(midtop=gameOverPos.midbottom)
            textOverlay = zip([gameOverText, scoreText],
                              [gameOverPos, scorePos])

    # Update and draw all sprites
        screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()
        for txt, pos in textOverlay:
            screen.blit(txt, pos)
        pygame.display.flip()
