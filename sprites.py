import pygame
import random
import math
from load import load_image


freq = 1 / 20
siney_move = 3
roundy_move = 2
explosion_linger = 12
spikey_slope = range(-3, 4)
spikey_interval = 4
spikey_period = range(10, 41)
fasty_movefunc = 3

user_size, level_size, scr_size = 200, 2, 400
main_lvl_size = 2

class size :
    update = scr_size*0.008
    radius = scr_size*0.04
    middle = scr_size // 2
    speed = scr_size*0.002
    masterspritespeed = scr_size*0.004
    lives = scr_size*0.06
    crawly = scr_size*0.006

    ratio_user = user_size*0.002
    explosion_linger = user_size*0.006
    x_background = scr_size*2
    right = x_background*0.6

def get_size(user, level) :
    global user_size, level_size, scr_size
    user_size, level_size = user, level
    scr_size = round(user_size * level_size)

    size.update = scr_size*0.008
    size.radius = scr_size*0.04
    size.middle = scr_size // 2
    size.speed = scr_size*0.002
    size.masterspritespeed = scr_size*0.004
    size.lives = scr_size*0.06
    size.crawly = scr_size*0.006

    size.ratio_user = user_size*0.002
    size.explosion_linger = user_size*0.006
    size.x_background = scr_size*2
    size.right = size.x_background*0.6


class MasterSprite(pygame.sprite.Sprite):
    allsprites = None
    speed = None


class Explosion(MasterSprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('explosion.png', -1)
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width()*size.ratio_user), round(self.image.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.linger = round(MasterSprite.speed * size.explosion_linger)

    @classmethod
    def position(cls, loc):
        if len(cls.pool) > 0:
            explosion = cls.pool.sprites()[0]
            explosion.add(cls.active, cls.allsprites)
            explosion.remove(cls.pool)
            explosion.rect.center = loc
            explosion.linger = explosion_linger


    def update(self):
        self.linger -= 1
        if self.linger <= 0:
            self.remove(self.allsprites, self.active)
            self.add(self.pool)


class Missile(MasterSprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('missile.png', -1)
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width()*size.ratio_user), round(self.image.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

    @classmethod
    def position(cls, loc):
        if len(cls.pool) > 0:
            missile = cls.pool.sprites()[0]
            missile.add(cls.allsprites, cls.active)
            missile.remove(cls.pool)
            missile.rect.midbottom = loc

    def table(self):
        self.add(self.pool)
        self.remove(self.allsprites, self.active)

    def update(self):
        newpos = self.rect.move(0, -size.update)
        self.rect = newpos
        if self.rect.top < self.area.top:
            self.table()


class Bomb(pygame.sprite.Sprite):
    def __init__(self, ship):
        super().__init__()
        self.image = None
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.radius = size.radius
        self.radiusIncrement = size.update
        self.rect = ship.rect

    def update(self):
        self.radius += self.radiusIncrement
        pygame.draw.circle(
            pygame.display.get_surface(),
            pygame.Color(0, 0, 255, 128),
            self.rect.center, self.radius, 3)
        if (self.rect.center[1] - self.radius <= self.area.top
            and self.rect.center[1] + self.radius >= self.area.bottom
            and self.rect.center[0] - self.radius <= self.area.left
                and self.rect.center[0] + self.radius >= self.area.right):
            self.kill()


class Powerup(MasterSprite):
    def __init__(self, kindof):
        super().__init__()
        self.image, self.rect = load_image(kindof + '_powerup.png', -1)
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width()*size.ratio_user), round(self.image.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.original = self.image
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.midtop = (random.randint(
                            self.area.left + self.rect.width // 2,
                            self.area.right - self.rect.width // 2),
                            self.area.top)
        self.angle = 0

    def update(self):
        center = self.rect.center
        self.angle = (self.angle + 2) % 360
        rotate = pygame.transform.rotate
        self.image = rotate(self.original, self.angle)
        self.rect = self.image.get_rect(
            center=(
                center[0],
                center[1] +
                MasterSprite.speed * size.speed))


class BombPowerup(Powerup):
    def __init__(self):
        super().__init__('bomb')
        self.pType = 'bomb'

class DistPowerup(Powerup):
    def __init__(self):
        super().__init__('dist')
        self.pType = 'dist'

class ShieldPowerup(Powerup):
    def __init__(self):
        super().__init__('shield')
        self.pType = 'shield'

class DoublemissilePowerup(Powerup):
    def __init__(self):
        super().__init__('doublemissile')
        self.pType = 'doublemissile'

class CoinPowerup(Powerup):
    def __init__(self):
        super().__init__('coin')
        self.pType = 'coin'
class CoinTwoPowerup(Powerup):
    def __init__(self):
        super().__init__('coin2')
        self.pType = 'coin2'

class TeamshieldPowerup(Powerup):
    def __init__(self):
        super().__init__('teamshield')
        self.pType = 'teamshield'

class Ship(MasterSprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('ship.png', -1)
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width()*size.ratio_user), round(self.image.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.original = self.image
        self.shield, self.rect = load_image('ship_shield.png', -1)
        self.shield = pygame.transform.scale(self.shield, (round(self.shield.get_width()*size.ratio_user), round(self.shield.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.shield.get_width(), self.shield.get_height())
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.rect.midbottom = (size.middle, scr_size)
        self.radius = max(self.rect.width, self.rect.height)
        self.alive = True
        self.shieldUp = False
        self.vert = 0
        self.horiz = 0
        self.lives = 3

    def initializeKeys(self):
        keyState = pygame.key.get_pressed()
        self.vert = 0
        self.horiz = 0
        if keyState[pygame.K_w]:
            self.vert -= MasterSprite.speed * size.masterspritespeed
        if keyState[pygame.K_a]:
            self.horiz -= MasterSprite.speed * size.masterspritespeed
        if keyState[pygame.K_s]:
            self.vert += MasterSprite.speed * size.masterspritespeed
        if keyState[pygame.K_d]:
            self.horiz += MasterSprite.speed * size.masterspritespeed

    def update(self):
        newpos = self.rect.move((self.horiz, self.vert))
        newhoriz = self.rect.move((self.horiz, 0))
        newvert = self.rect.move((0, self.vert))

        if not (newpos.left <= self.area.left
                or newpos.top <= self.area.top
                or newpos.right >= self.area.right
                or newpos.bottom >= self.area.bottom):
            self.rect = newpos
        elif not (newhoriz.left <= self.area.left
                  or newhoriz.right >= self.area.right):
            self.rect = newhoriz
        elif not (newvert.top <= self.area.top
                  or newvert.bottom >= self.area.bottom):
            self.rect = newvert

        if self.shieldUp and self.image != self.shield:
            self.image = self.shield

        if not self.shieldUp and self.image != self.original:
            self.image = self.original

    def bomb(self):
        return Bomb(self)

    ## life 구현부분
    def draw_lives(self, surface, x, y):
        for i in range(self.lives):
            self.img_rect = self.image.get_rect()
            self.img_rect.x = x + size.lives * i
            self.img_rect.y = y
            surface.blit(self.image, self.img_rect)


class Ship2(MasterSprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('ship.png', -1)
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width()*size.ratio_user), round(self.image.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.original = self.image
        self.shield, self.rect = load_image('ship_shield.png', -1)
        self.shield = pygame.transform.scale(self.shield, (round(self.shield.get_width()*size.ratio_user), round(self.shield.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.shield.get_width(), self.shield.get_height())
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.rect.midbottom = (scr_size * 0.5, scr_size)
        self.radius = max(self.rect.width, self.rect.height)
        self.alive = True
        self.shieldUp = False
        self.vert = 0
        self.horiz = 0
        self.lives = 3

    def initializeKeys(self):
        self.vert = 0
        self.horiz = 0

    def update(self):
        newpos = self.rect.move((self.horiz, self.vert))
        newhoriz = self.rect.move((self.horiz, 0))
        newvert = self.rect.move((0, self.vert))

        if not (newpos.left <= self.area.left
                or newpos.top <= self.area.top
                or newpos.right >= scr_size
                or newpos.bottom >= self.area.bottom):
            self.rect = newpos
        elif not (newhoriz.left <= self.area.left
                  or newhoriz.right >= scr_size):
            self.rect = newhoriz
        elif not (newvert.top <= self.area.top
                  or newvert.bottom >= self.area.bottom):
            self.rect = newvert

        if self.shieldUp and self.image != self.shield:
            self.image = self.shield


        if not self.shieldUp and self.image != self.original:
            self.image = self.original

    def bomb(self):
        return Bomb(self)

    ## life 구현부분
    def draw_lives(self, surface, x, y):
        for i in range(self.lives):
            self.img_rect = self.image.get_rect()
            self.img_rect.x = x + size.lives * i
            self.img_rect.y = y + size.lives
            surface.blit(self.image, self.img_rect)


class Ship3(MasterSprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('ship2.png', -1)
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width()*size.ratio_user), round(self.image.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.original = self.image
        self.shield, self.rect = load_image('ship_shield.png', -1)
        self.shield = pygame.transform.scale(self.shield, (round(self.shield.get_width()*size.ratio_user), round(self.shield.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.shield.get_width(), self.shield.get_height())
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.rect.midbottom = (scr_size * 1.5, scr_size)
        self.radius = max(self.rect.width, self.rect.height)
        self.alive = True
        self.shieldUp = False
        self.vert = 0
        self.horiz = 0
        self.lives = 3

    def initializeKeys(self):
        self.vert = 0
        self.horiz = 0

    def update(self):
        newpos = self.rect.move((self.horiz, self.vert))
        newhoriz = self.rect.move((self.horiz, 0))
        newvert = self.rect.move((0, self.vert))

        if not (newpos.left <= scr_size
                or newpos.top <= self.area.top
                or newpos.right >= self.area.right
                or newpos.bottom >= self.area.bottom):
            self.rect = newpos
        elif not (newhoriz.left <= scr_size
                  or newhoriz.right >= self.area.right):
            self.rect = newhoriz
        elif not (newvert.top <= self.area.top
                  or newvert.bottom >= self.area.bottom):
            self.rect = newvert

        if self.shieldUp and self.image != self.shield:
            self.image = self.shield

        if not self.shieldUp and self.image != self.original:
            self.image = self.original

    def bomb(self):
        return Bomb(self)

    ## life 구현부분
    def draw_lives(self, surface, x, y):
        for i in range(self.lives):
            self.img_rect = self.image.get_rect()
            self.img_rect.x = scr_size + x + size.lives * i
            self.img_rect.y = y + size.lives
            surface.blit(self.image, self.img_rect)

class Ship4(MasterSprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('ship.png', -1)
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width()*size.ratio_user), round(self.image.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.original = self.image
        self.shield, self.rect = load_image('ship_shield.png', -1)
        self.shield = pygame.transform.scale(self.shield, (round(self.shield.get_width()*size.ratio_user), round(self.shield.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.shield.get_width(), self.shield.get_height())
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.rect.midbottom = (scr_size * 0.5, scr_size)
        self.radius = max(self.rect.width, self.rect.height)
        self.alive = True
        self.shieldUp = False
        self.vert = 0
        self.horiz = 0
        self.lives = 3

    def initializeKeys(self):
        self.vert = 0
        self.horiz = 0

    def update(self):
        newpos = self.rect.move((self.horiz, self.vert))
        newhoriz = self.rect.move((self.horiz, 0))
        newvert = self.rect.move((0, self.vert))

        if not (newpos.left <= self.area.left
                or newpos.top <= self.area.top
                or newpos.right >= self.area.right
                or newpos.bottom >= self.area.bottom):
            self.rect = newpos
        elif not (newhoriz.left <= self.area.left
                  or newhoriz.right >= self.area.right) :
            self.rect = newhoriz
        elif not (newvert.top <= self.area.top
                  or newvert.bottom >= self.area.bottom):
            self.rect = newvert

        if self.shieldUp and self.image != self.shield:
            self.image = self.shield


        if not self.shieldUp and self.image != self.original:
            self.image = self.original

    def bomb(self):
        return Bomb(self)

    ## life 구현부분
    def draw_lives(self, surface, x, y):
        for i in range(self.lives):
            self.img_rect = self.image.get_rect()
            self.img_rect.x = x + size.lives * i
            self.img_rect.y = y + size.lives
            surface.blit(self.image, self.img_rect)


class Ship5(MasterSprite):
    def __init__(self):
        super().__init__()
        self.image, self.rect = load_image('ship2.png', -1)
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width()*size.ratio_user), round(self.image.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.original = self.image
        self.shield, self.rect = load_image('ship2_shield.png', -1)
        self.shield = pygame.transform.scale(self.shield, (round(self.shield.get_width()*size.ratio_user), round(self.shield.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.shield.get_width(), self.shield.get_height())
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.rect.midbottom = (scr_size * 1.5, scr_size)
        self.radius = max(self.rect.width, self.rect.height)
        self.alive = True
        self.shieldUp = False
        self.vert = 0
        self.horiz = 0
        self.lives = 3

    def initializeKeys(self):
        self.vert = 0
        self.horiz = 0

    def update(self):
        newpos = self.rect.move((self.horiz, self.vert))
        newhoriz = self.rect.move((self.horiz, 0))
        newvert = self.rect.move((0, self.vert))

        if not (newpos.left <= self.area.left
                or newpos.top <= self.area.top
                or newpos.right >= self.area.right
                or newpos.bottom >= self.area.bottom):
            self.rect = newpos
        elif not (newhoriz.left <= self.area.left
                  or newhoriz.right >= self.area.right):
            self.rect = newhoriz
        elif not (newvert.top <= self.area.top
                  or newvert.bottom >= self.area.bottom):
            self.rect = newvert

        if self.shieldUp and self.image != self.shield:
            self.image = self.shield

        if not self.shieldUp and self.image != self.original:
            self.image = self.original

    def bomb(self):
        return Bomb(self)

    ## life 구현부분
    def draw_lives(self, surface, x, y):
        for i in range(self.lives):
            self.img_rect = self.image.get_rect()
            self.img_rect.x = scr_size + x + size.lives * i
            self.img_rect.y = y + size.lives
            surface.blit(self.image, self.img_rect)

class Alien(MasterSprite):
    pool = pygame.sprite.Group()
    active = pygame.sprite.Group()

    def __init__(self, color):
        super().__init__()
        self.image, self.rect = load_image('space_invader_' + color + '.png', -1)
        self.image = pygame.transform.scale(self.image, (round(self.image.get_width()*size.ratio_user), round(self.image.get_height()*size.ratio_user)))
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.initialRect = self.rect
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.loc = 0
        self.radius = min(self.rect.width // 2, self.rect.height // 2)

    @classmethod
    def position(cls):
        if len(cls.pool) > 0 and cls.numOffScreen > 0:
            alien = random.choice(cls.pool.sprites())
            if isinstance(alien, Crawly):
                alien.rect.midbottom = (random.choice(
                    (alien.area.left, alien.area.right)),
                    random.randint(
                    (alien.area.bottom * 3) // 4,
                    alien.area.bottom))
            else:
                alien.rect.midtop = (random.randint(
                    alien.area.left
                    + alien.rect.width // 2,
                    alien.area.right
                    - alien.rect.width // 2),
                    alien.area.top)
            alien.initialRect = alien.rect
            alien.loc = 0
            alien.add(cls.allsprites, cls.active)
            alien.remove(cls.pool)
            Alien.numOffScreen -= 1

    def update(self):
        horiz, vert = self.moveFunc()
        if level_size != main_lvl_size:
            if horiz + self.initialRect.x > size.x_background:
                horiz -= size.x_background + self.rect.width
            elif horiz + self.initialRect.x < 0 - self.rect.width:
                horiz += scr_size + self.rect.width
        else :
            if horiz + self.initialRect.x > scr_size:
                horiz -= scr_size + self.rect.width
            elif horiz + self.initialRect.x < 0 - self.rect.width:
                horiz += scr_size + self.rect.width
        self.rect = self.initialRect.move((horiz, self.loc + vert))
        self.loc = self.loc + MasterSprite.speed * size.speed
        if self.rect.top > self.area.bottom:
            self.table()
            Alien.numOffScreen += 1

    def table(self):
        self.kill()
        self.add(self.pool)


class Siney(Alien):
    def __init__(self):
        super().__init__('green')
        self.amp = random.randint(self.rect.width, siney_move * self.rect.width)
        self.freq = freq
        self.moveFunc = lambda: (self.amp * math.sin(self.loc * self.freq), 0)
        self.pType = 'green'

class Roundy(Alien):
    def __init__(self):
        super().__init__('red')
        self.amp = random.randint(self.rect.width, roundy_move * self.rect.width)
        self.freq = freq
        self.moveFunc = lambda: (
            self.amp *
            math.sin(
                self.loc *
                self.freq),
            self.amp *
            math.cos(
                self.loc *
                self.freq))
        self.pType = 'red'

class Spikey(Alien):
    def __init__(self):
        super().__init__('orange')
        self.slope = random.choice(list(x for x in spikey_slope if x != 0))
        self.period = random.choice(list(spikey_interval * x for x in spikey_period))
        self.moveFunc = lambda: (self.slope * (self.loc % self.period)
                                 if self.loc % self.period < self.period // 2
                                 else self.slope * self.period // 2
                                 - self.slope * ((self.loc % self.period)
                                 - self.period // 2), 0)
        self.pType = 'orange'


class Fasty(Alien):
    def __init__(self):
        super().__init__('white')
        self.moveFunc = lambda: (0, fasty_movefunc * self.loc)
        self.pType = 'white'


class Crawly(Alien):
    def __init__(self):
        super().__init__('yellow')
        self.moveFunc = lambda: (self.loc, 0)
        self.pType = 'yellow'

    def update(self):
        horiz, vert = self.moveFunc()
        horiz = (-horiz if self.initialRect.center[0] == self.area.right
                 else horiz)
        if (horiz + self.initialRect.left > self.area.right
                or horiz + self.initialRect.right < self.area.left):
            self.table()
            Alien.numOffScreen += 1
        self.rect = self.initialRect.move((horiz, vert))
        self.loc = self.loc + MasterSprite.speed * size.crawly
