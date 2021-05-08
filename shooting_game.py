import pygame
import random
from collections import deque

from sprites import (MasterSprite, Ship, Alien, Missile, BombPowerup,
                     ShieldPowerup, DoublemissilePowerup, Explosion, Siney, Spikey, Fasty,
                     Roundy, Crawly)
from database import Database
from load import load_image, load_sound, load_music

if not pygame.mixer:
    print('Warning, sound disabled')
if not pygame.font:
    print('Warning, fonts disabled')

scr_x, scr_y = 500, 500

# BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK= ( 0,  0,  0)
WHITE= (255,255,255)
GREEN= ( 0,255,  0)


class Keyboard(object):
    keys = {pygame.K_a: 'A', pygame.K_b: 'B', pygame.K_c: 'C', pygame.K_d: 'D',
            pygame.K_e: 'E', pygame.K_f: 'F', pygame.K_g: 'G', pygame.K_h: 'H',
            pygame.K_i: 'I', pygame.K_j: 'J', pygame.K_k: 'K', pygame.K_l: 'L',
            pygame.K_m: 'M', pygame.K_n: 'N', pygame.K_o: 'O', pygame.K_p: 'P',
            pygame.K_q: 'Q', pygame.K_r: 'R', pygame.K_s: 'S', pygame.K_t: 'T',
            pygame.K_u: 'U', pygame.K_v: 'V', pygame.K_w: 'W', pygame.K_x: 'X',
            pygame.K_y: 'Y', pygame.K_z: 'Z'}


def main(xx, yy):
    scr_x, scr_y = xx, yy

    direction = {None: (0, 0), pygame.K_UP: (0, round(-scr_y*0.004)), pygame.K_DOWN: (0, round(scr_y*0.004)),
             pygame.K_LEFT: (round(-scr_x*0.004), 0), pygame.K_RIGHT: (round(scr_x*0.004), 0)}

    # Initialize everything
    pygame.mixer.pre_init(11025, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((scr_x, scr_y), pygame.RESIZABLE)
    pygame.display.set_caption('Shooting Game')
    pygame.mouse.set_visible(1)

# Create the background which will scroll and loop over a set of different
# size stars
    background = pygame.Surface((scr_x, scr_y*4))
    background = background.convert()
    # 수정 : 배경 색깔 고르기 white or red
    background.fill((0, 0, 0))
    # red = [255,0,0]
    # abc = input("what color??")
    # if abc =='red':
    #     background.fill(red)
    #     pygame.display.update()

    backgroundLoc = scr_y*3
    finalStars = deque()
    for y in range(0, scr_y*3, round(scr_y*0.06)):
        size = random.randint(round(scr_x*0.004), round(scr_x*0.01))
        x = random.randint(0, scr_x - size)
        if y <= scr_y:
            finalStars.appendleft((x, y + scr_y*3, size))
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
    doublemissile = False #doublemissile아이템이 지속되는 동안(5초) 미사일이 두배로 발사됨
    score = 0
    missilesFired = 0
    powerupTime = 10 * clockTime
    powerupTimeLeft = powerupTime
    betweenWaveTime = 3 * clockTime
    betweenWaveCount = betweenWaveTime
    betweenDoubleTime = 5 * clockTime
    betweenDoubleCount = betweenDoubleTime
    font = pygame.font.Font(None, round(scr_x*0.065))

    inMenu = True

    hiScores = Database.getScores()
    highScoreTexts = [font.render("NAME", 1, RED),
                      font.render("SCORE", 1, RED),
                      font.render("ACCURACY", 1, RED)]
    highScorePos = [highScoreTexts[0].get_rect(
                      topleft=screen.get_rect().inflate(-100, -100).topleft),
                    highScoreTexts[1].get_rect(
                      midtop=screen.get_rect().inflate(-100, -100).midtop),
                    highScoreTexts[2].get_rect(
                      topright=screen.get_rect().inflate(-100, -100).topright)]
    for hs in hiScores:
        highScoreTexts.extend([font.render(str(hs[x]), 1, WHITE)
                               for x in range(3)])
        highScorePos.extend([highScoreTexts[x].get_rect(
            topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])

    title, titleRect = load_image('title.png')
    pause,pauseRect = load_image('pause.png',WHITE)
    titleRect.midtop = screen.get_rect().inflate(0, -200).midtop
    pauseRect.midtop = screen.get_rect().inflate(0, -200).midtop

    startText = font.render('START GAME', 1, WHITE)
    startPos = startText.get_rect(midtop=titleRect.inflate(0, 100).midbottom)
    hiScoreText = font.render('HIGH SCORES', 1, WHITE)
    hiScorePos = hiScoreText.get_rect(topleft=startPos.bottomleft)
    fxText = font.render('SOUND FX ', 1, WHITE)
    fxPos = fxText.get_rect(topleft=hiScorePos.bottomleft)
    fxOnText = font.render('ON', 1, RED)
    fxOffText = font.render('OFF', 1, RED)
    fxOnPos = fxOnText.get_rect(topleft=fxPos.topright)
    fxOffPos = fxOffText.get_rect(topleft=fxPos.topright)
    musicText = font.render('MUSIC', 1, WHITE)
    musicPos = fxText.get_rect(topleft=fxPos.bottomleft)
    musicOnText = font.render('ON', 1, RED)
    musicOffText = font.render('OFF', 1, RED)
    musicOnPos = musicOnText.get_rect(topleft=musicPos.topright)
    musicOffPos = musicOffText.get_rect(topleft=musicPos.topright)
    quitText = font.render('QUIT', 1, WHITE)
    quitPos = quitText.get_rect(topleft=musicPos.bottomleft)
    selectText = font.render('> ', 1, WHITE)
    selectPos = selectText.get_rect(topright=startPos.topleft)
    menuDict = {1: startPos, 2: hiScorePos, 3: fxPos, 4: musicPos, 5: quitPos}
    selection = 1
    showHiScores = False
    soundFX = Database.getSound()
    music = Database.getSound(music=True)

    # pause 구현
    restartText = font.render('RESTART    ', 1,WHITE)
    restartPos = restartText.get_rect(midtop=titleRect.inflate(0, 100).midbottom)

    if music and pygame.mixer:
        pygame.mixer.music.play(loops=-1)

    while inMenu:
        scr_x , scr_y = pygame.display.get_surface().get_size()
        if xx != scr_x or yy != scr_y :
            return scr_x, scr_y
        clock.tick(clockTime)

        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, scr_x, scr_y))
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = scr_y*3

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                return
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_RETURN): # K_RETURN은 enter누르면
                if showHiScores:
                    showHiScores = False
                elif selection == 1:
                    screen = pygame.display.set_mode((scr_x, scr_y))
                    inMenu = False
                    ship.initializeKeys()
                elif selection == 2:
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
                elif selection == 5:
                    return
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_UP
                  and selection > 1
                  and not showHiScores):
                selection -= 1
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_DOWN
                  and selection < len(menuDict)
                  and not showHiScores):
                selection += 1

        selectPos = selectText.get_rect(topright=menuDict[selection].topleft)

        if showHiScores:
            textOverlays = zip(highScoreTexts, highScorePos)
        else:
            textOverlays = zip([startText, hiScoreText, fxText,
                                musicText, quitText, selectText,
                                fxOnText if soundFX else fxOffText,
                                musicOnText if music else musicOffText],
                               [startPos, hiScorePos, fxPos,
                                musicPos, quitPos, selectPos,
                                fxOnPos if soundFX else fxOffPos,
                                musicOnPos if music else musicOffPos])
            screen.blit(title, titleRect)
        for txt, pos in textOverlays:
            screen.blit(txt, pos)
        pygame.display.flip()

    while ship.alive:
        clock.tick(clockTime)

        if aliensLeftThisWave >= 20:
            powerupTimeLeft -= 1
        if powerupTimeLeft <= 0:
            powerupTimeLeft = powerupTime
            random.choice(powerupTypes)().add(powerups, allsprites)

        # Event Handling
        for event in pygame.event.get():
            if (event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE):
                return
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
                  #doublemissile 구현
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
                while inPmenu:
                    clock.tick(clockTime)

                    screen.blit(
                        background, (0, 0), area=pygame.Rect(
                            0, backgroundLoc, scr_x, scr_y))
                    backgroundLoc -= speed
                    if backgroundLoc - speed <= speed:
                        backgroundLoc = scr_y*3

                    for event in pygame.event.get():
                        if (event.type == pygame.QUIT):
                            return
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_RETURN): # K_RETURN은 enter누르면
                            if showHiScores:
                                showHiScores = False
                            elif selection == 1:
                                inPmenu = False
                                break
                                # ship.initializeKeys()
                            elif selection == 2:
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
                            elif selection == 5:
                                return
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_UP
                            and selection > 1
                            and not showHiScores):
                            selection -= 1
                        elif (event.type == pygame.KEYDOWN
                            and event.key == pygame.K_DOWN
                            and selection < len(menuDict)
                            and not showHiScores):
                            selection += 1

                    selectPos = selectText.get_rect(topright=menuDict[selection].topleft)

                    if showHiScores:
                        textOverlays = zip(highScoreTexts, highScorePos)
                    else:
                        textOverlays = zip([restartText, hiScoreText, fxText,
                                            musicText, quitText, selectText,
                                            fxOnText if soundFX else fxOffText,
                                            musicOnText if music else musicOffText],
                                        [restartPos, hiScorePos, fxPos,
                                            musicPos, quitPos, selectPos,
                                            fxOnPos if soundFX else fxOffPos,
                                            musicOnPos if music else musicOffPos])
                        screen.blit(pause, pauseRect)
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
                    score += 1
                    if soundFX:
                        alien_explode_sound.play()
            for missile in Missile.active:
                if pygame.sprite.collide_rect(
                        missile, alien) and alien in Alien.active:
                    alien.table()
                    missile.table()
                    Explosion.position(alien.rect.center)
                    aliensLeftThisWave -= 1
                    score += 1
                    if soundFX:
                        alien_explode_sound.play()
            if pygame.sprite.collide_rect(alien, ship):
                if ship.shieldUp:
                    alien.table()
                    Explosion.position(alien.rect.center)
                    aliensLeftThisWave -= 1
                    score += 1
                    missilesFired += 1
                    ship.shieldUp = False
                else:
                    ship.alive = False
                    ship.remove(allsprites)
                    Explosion.position(ship.rect.center)
                    if soundFX:
                        ship_explode_sound.play()

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

        wavePos = waveText.get_rect(topleft=screen.get_rect().topleft)
        leftPos = leftText.get_rect(midtop=screen.get_rect().midtop)
        scorePos = scoreText.get_rect(topright=screen.get_rect().topright)
        bombPos = bombText.get_rect(bottomleft=screen.get_rect().bottomleft)

        text = [waveText, leftText, scoreText, bombText]
        textposition = [wavePos, leftPos, scorePos, bombPos]

        #5초동안 doublemissile상태를 유지
        if doublemissile:
            if betweenDoubleCount > 0:
                betweenDoubleCount -= 1
            elif betweenDoubleCount == 0:
                doublemissile = False
                betweenDoubleCount = betweenDoubleTime

     # Detertmine when to move to next wave
        if aliensLeftThisWave <= 0:
            if betweenWaveCount > 0:
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

        textOverlays = zip(text, textposition)

     # Update and draw all sprites and text
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, scr_x, scr_y))
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = scr_y*3
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()
        for txt, pos in textOverlays:
            screen.blit(txt, pos)
        pygame.display.flip()

    accuracy = round(score / missilesFired, 4) if missilesFired > 0 else 0.0
    isHiScore = len(hiScores) < Database.numScores or score > hiScores[-1][1]
    name = ''
    nameBuffer = []

    while True:
        clock.tick(clockTime)

    # Event Handling
        for event in pygame.event.get():
            if (event.type == pygame.QUIT
                or not isHiScore
                and event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE):
                return False
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_RETURN
                  and not isHiScore):
                return True
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
                return True

        if isHiScore:
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
        else:
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
                0, backgroundLoc, scr_x, scr_y))
        backgroundLoc -= speed
        if backgroundLoc - speed <= 0:
            backgroundLoc = scr_y*3
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()
        for txt, pos in textOverlay:
            screen.blit(txt, pos)
        pygame.display.flip()



