import pygame
import pygame.mixer
from pygame.locals import *
import sys
import random

#UFOの爆破サウンドを複数入れ込みたい

SCREEN = Rect((0,0,640,480))

def load_image(fname, size=None):
    tmp = pygame.image.load(fname)
    return tmp if size == None else pygame.transform.scale(tmp,size)

def load_sound(sound):
    return pygame.mixer.Sound(sound)

"""クラスの定義"""

class Background:
    """背景"""
    def __init__(self, majo):
        self.majo = majo
        self.sky_image = load_image("bg_natural_sky.jpg",SCREEN.size)
        self.mount_image = load_image("bg_natural_mount.png")
        self.mount_rect = self.mount_image.get_rect()
        self.ground_image = pygame.Surface((SCREEN.width, 20))
        self.ground_image.fill((0,128, 64))
        self.ground_rect = self.ground_image.get_rect()
        self.ground_rect.bottom = SCREEN.bottom
    def update(self):
        self.mount_image_x = (self.mount_rect.width - SCREEN.width) \
         / SCREEN.width * self.majo.rect.centerx

    def draw(self, screen):
        screen.blit(self.sky_image, SCREEN)
        screen.blit(self.mount_image, (-self.mount_image_x, -118))
        screen.blit(self.ground_image, self.ground_rect)

class Majo(pygame.sprite.Sprite):
    """魔女"""
    IMAGE_WIDTH, IMAGE_HEIGHT = (32, 32)
    LEFT, RIGHT = (1, 2)
    SPEED = 5
    IMAGE_NUMS = 3
    MINUS_LIFE = 1
    UFO_POINT = 10
    BOMB_POINT = 1

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = load_image("majo.png")
        self.image_dir = Majo.LEFT
        self.image_off = 0
        self.image = self.images.subsurface(
            (0,0, Majo.IMAGE_WIDTH, Majo.IMAGE_HEIGHT))
        self.rect = Rect(0,0, Majo.IMAGE_WIDTH, Majo.IMAGE_HEIGHT)
        self.rect.centerx = SCREEN.centerx
        self.rect.bottom = SCREEN.bottom - 20

    def move_left(self):
        self.rect.move_ip(-Majo.SPEED, 0)
        self.image_dir = Majo.LEFT
        self.move()

    def move_right(self):
        self.rect.move_ip(Majo.SPEED, 0)
        self.image_dir = Majo.RIGHT
        self.move()

    def move(self):
        self.rect.clamp_ip(SCREEN)
        self.image_off = (self.image_off + 1) % Majo.IMAGE_NUMS
        self.image = self.images.subsurface(
            self.image_off * Majo.IMAGE_WIDTH,
            self.image_dir * Majo.IMAGE_HEIGHT,
            Majo.IMAGE_WIDTH,
            Majo.IMAGE_HEIGHT
        )

    def update(self):
        pass

    # def draw(self,screen):
    #     screen.blit(self.image, self.rect)

class Beam(pygame.sprite.Sprite):
    """魔女のビーム"""
    SPEED = 5
    counter = 0
    EXP_IMAGE_WIDTH, EXP_IMAGE_HEIGHT = 120, 120
    EXP_IMAGE_OFFSET = 5
    EXP_ANIME_COUNT = 5
    def __init__(self,majo):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.majo = majo
        self.rect = self.image.get_rect()
        self.rect.centerx = self.majo.rect.centerx
        self.rect.bottom = self.majo.rect.top
        Beam.counter += 1
        Beam.sound.play()

    def update(self):
        self.rect.top -= Beam.SPEED
        if self.rect.top < SCREEN.top:
            Beam.counter -= 1
            self.kill()

class Ufo(pygame.sprite.Sprite):
    """UFO"""
    IMAGE_WIDTH, IMAGE_HEIGHT = 64, 28
    START = (SCREEN.width/ 4, 30)
    SPEED = 5
    LEFT, RIGHT =0,1
    BOMB_PROB = 0.01
    MINUS_POINT = 5
    #爆発アニメ
    EXP_IMAGE_WIDTH, EXP_IMAGE_HEIGHT = 320, 120
    EXP_IMAGE_OFFSET = 7
    EXP_ANIME_COUNT = 10
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = Ufo.images.subsurface(
            0,0,Ufo.IMAGE_WIDTH, Ufo.IMAGE_HEIGHT
        )
        self.rect = self.image.get_rect()
        self.rect.midtop = Ufo.START
        self.speed = Ufo.SPEED
        self.dir = Ufo.LEFT
        self.bomb_prob = Ufo.BOMB_PROB

    def update(self):
        self.rect.move_ip(self.speed, 0)
        if self.rect.left <= SCREEN.left or self.rect.right >= SCREEN.right:
            self.speed = -self.speed
        self.rect.clamp_ip(SCREEN)
        self.dir = Ufo.LEFT if self.speed > 0 else Ufo.RIGHT
        self.image = Ufo.images.subsurface(
            self.dir * Ufo.IMAGE_WIDTH, 0,
            Ufo.IMAGE_WIDTH, Ufo.IMAGE_HEIGHT
        )
        if Majo.stage.val > 3:
            self.bomb_prob = 0.03
        elif Majo.stage.val > 4:
            self.bomb_prob = 0.05
        if random.random() < self.bomb_prob:
            dx = 0 if Majo.stage.val <= 1 else \
                (random.random() * 2.0 - 1.0) * self.speed
            Bomb(self, dx)

        """UFOの爆破シーン"""
        if Ufo.score.val == 0:
            Explosion(
                Ufo.exp_images,
                self.rect.center,
                (Ufo.EXP_IMAGE_WIDTH, Ufo.EXP_IMAGE_HEIGHT),
                Ufo.EXP_IMAGE_OFFSET,
                Ufo.EXP_ANIME_COUNT,
                Ufo.exp_sound,
            )
            self.kill()
            return

class Explosion(pygame.sprite.Sprite):
    """爆発アニメ"""

    def __init__(self,
        images,
        start_pos,
        image_size,
        max_offset,
        max_anime_count,
        exp_sound):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.images = images
        self.images_rect = self.images.get_rect()
        self.max_offset = max_offset
        self.offset = 0
        self.max_anime_count = max_anime_count
        self.anime_count = 0
        self.sizex, self.sizey = image_size
        if self.images_rect.width > self.images_rect.height:
            #imagesは横長の画像
            self.image = self.images.subsurface(
                (self.offset * self.sizex,0, self.sizex, self.sizey)
            )
        else:
            self.image = self.images.subsurface(
                (0,self.offset * self.sizey, self.sizex, self.sizey)
            )
        self.rect =self.image.get_rect()
        self.rect.center = start_pos
        exp_sound.play()

    def update(self):
        self.anime_count = (self.anime_count + 1) % self.max_anime_count
        if self.anime_count == 0:
            self.offset += 1
            if self.offset == self.max_offset:
                self.offset = 0
                self.kill()
                return
        if self.images_rect.width > self.images_rect.height:
            #imagesは横長の画像
            self.image = self.images.subsurface(
                (self.offset * self.sizex, 0, self.sizex, self.sizey)
            )
        else:
            self.image = self.images.subsurface(
                (0, self.offset * self.sizey, self.sizex, self.sizey)
            )

class Bomb(pygame.sprite.Sprite):
    """UFOが落とす爆弾"""
    IMAGE_COLORS, IMAGE_OFFSET = 4, 3
    IMAGE_WIDTH,IMAGE_HEIGHT = 64, 112
    SPEED = 5
    #爆発アニメ
    EXP_IMAGE_WIDTH, EXP_IMAGE_HEIGHT = 120, 120
    EXP_IMAGE_OFFSET = 5
    EXP_ANIME_COUNT = 5
    def __init__(self,ufo, dx):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image_color = int(random.random() * Bomb.IMAGE_COLORS)
        self.image_off = 0
        self.image = Bomb.images.subsurface(
            self.image_off * Bomb.IMAGE_WIDTH,
            self.image_color * Bomb.IMAGE_HEIGHT,
            Bomb.IMAGE_WIDTH, Bomb.IMAGE_HEIGHT
        )
        self.speed = Bomb.SPEED
        self.rect = self.image.get_rect()
        self.rect.midtop = ufo.rect.midbottom
        self.dx = dx

    def update(self):
        if Majo.stage.val > 2:
            self.speed = random.randrange(1,20)
        self.rect.move_ip(self.dx, self.speed)
        if self.rect.bottom > SCREEN.bottom - 12:
            Explosion(
                Bomb.exp_images,
                self.rect.center,
                (Bomb.EXP_IMAGE_WIDTH, Bomb.EXP_IMAGE_HEIGHT),
                Bomb.EXP_IMAGE_OFFSET,
                Bomb.EXP_ANIME_COUNT,
                Bomb.exp_sound
            )
            self.kill()
            return
        self.image_off = (self.image_off + 1) % Bomb.IMAGE_OFFSET
        self.image = Bomb.images.subsurface(
            self.image_off * Bomb.IMAGE_WIDTH,
            self.image_color * Bomb.IMAGE_HEIGHT,
            Bomb.IMAGE_WIDTH, Bomb.IMAGE_HEIGHT
        )
class Point(pygame.sprite.Sprite):
    """マイナスポイントを表示"""
    FONT_SIZE = 32
    RED = (255, 0, 0)
    MAX_ANIME_COUNT = 50
    def __init__(self, point, start_pos):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.point = point
        self.font = pygame.font.SysFont(None, Point.FONT_SIZE)
        self.image = self.font.render(
            "-" + str(self.point), False, Point.RED)
        self.rect = self.image.get_rect()
        self.rect.center = start_pos
        self.anime_count = 0

    def update(self):
        self.anime_count += 1
        if self.anime_count ==Point.MAX_ANIME_COUNT:
            self.kill()
            return

class Counter:
    """カウンタ"""
    def __init__(self, initval, maxval = None):
        self.init_val = initval
        self._val = initval
        if maxval:
            self._maxval = maxval

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, val):
        self._val = val if val >=0  else 0

    def reset(self):
        self._val = self.init_val

    @property
    def maxval(self):
        return self._maxval

class Score(Counter,pygame.sprite.Sprite):
    """スコア用クラス"""
    FONT_SIZE = 28
    BLUE = (0,0,255)
    RED = (255,0,0)
    def __init__(self,
        initval = 0, #初期値
        maxval = None, #最大値
        pos = (0,0), #表示位置
        color = BLUE, #色指定
        font = None, #フォント指定(規定値: システム)
        form = "#", #表示形式指定
        pat = None  #表示パターン (pat..."●○"のように表示)
        ):
        Counter.__init__(self, initval, maxval)
        pygame.sprite.Sprite.__init__(self, self.containers)
        if font == None:
            self.font = pygame.font.SysFont(None, Score.FONT_SIZE)
        else:
            self.font = pygame.font.Font(font, 20)
        self.color = color
        self.pos = pos
        self.pat = pat
        if self.pat:
            self.form = form.replace("#","{}")
            text_img = self.form.format(self.pat[0] * self._val)
        else:
            self.form = form.replace("#", "{:0>5d}")
            text_img = self.form.format(self._val)
        self.image = self.font.render(text_img, False, self.color)
        self.rect = self.image.get_rect().move(self.pos)

    def update(self):
        if self.pat:
            text_img = self.form.format(self.pat[0] * self._val + self.pat[1] * (self._maxval - self._val))
        else:
            text_img = self.form.format(self._val)
        self.image = self.font.render(text_img, False, self.color)
        self.rect = self.image.get_rect().move(self.pos)

class HiScore(Score):
    """ハイスコア"""
    def __init__(self,
        score_obj, #スコアオブジェクト
        pos = (0,0), #表示形式
        form="#", #表示形式指定
        ):
        self.score_obj = score_obj
        Score.__init__(self, pos=pos, form=form)

    def update(self):
        self._val = max(self._val, self.score_obj.val)
        Score.update(self)

def collision_detection(majo, ufo, beam_g, bomb_g):
    """BeamとUFOとの衝突判定"""
    beam_collided = pygame.sprite.spritecollide(ufo, beam_g, True)
    if beam_collided:
        Explosion(
            Beam.exp_images,
            beam_collided[0].rect.center,
            (Beam.EXP_IMAGE_WIDTH, Beam.EXP_IMAGE_HEIGHT),
            Beam.EXP_IMAGE_OFFSET,
            Beam.EXP_ANIME_COUNT,
            Beam.exp_sound
        )
        if Beam.counter > 0:
            Beam.counter -= 1
        Point(Ufo.MINUS_POINT, ufo.rect.center)
        Ufo.score.val -= Ufo.MINUS_POINT
        Majo.score.val += Majo.UFO_POINT

    """Beamと爆弾との衝突判定"""
    group_collided = pygame.sprite.groupcollide(bomb_g, beam_g, True, True)
        #[ bomb1: [beam1, beam2], bomb2[beam3, beam4]] のような辞書型のオブジェクトを想定(実際はおそらく1対1になるはず)
    if group_collided:
        for bomb, beams in group_collided.items():
            for beam in beams:
                Explosion(
                    Beam.exp_images,
                    bomb.rect.center,
                    (Beam.EXP_IMAGE_WIDTH, Beam.EXP_IMAGE_HEIGHT),
                    Beam.EXP_IMAGE_OFFSET,
                    Beam.EXP_ANIME_COUNT,
                    Beam.exp_sound
                )
        if Beam.counter > 0:
            Beam.counter -= 1
        Majo.score.val += Majo.BOMB_POINT

    """爆弾と魔女の衝突判定"""
    bomb_collided = pygame.sprite.spritecollide(majo, bomb_g, True)
    if bomb_collided:
        Explosion(
            Majo.exp_images,
            (majo.rect.centerx, majo.rect.centery - 20),
            (Bomb.EXP_IMAGE_WIDTH, Bomb.EXP_IMAGE_HEIGHT),
            Bomb.EXP_IMAGE_OFFSET,
            Bomb.EXP_ANIME_COUNT,
            Majo.exp_sound
        )
        Majo.life.val -= Majo.MINUS_LIFE
        Point(Majo.MINUS_LIFE, majo.rect.center)
        if Majo.life.val == 0:
            majo.kill()

def main():
    """ 初期設定 """
    #画面の初期設定
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    pygame.display.set_caption('SHOOTING GAME')

    INIT,PLAY,CLEAR, GAMEOVER = 1, 2, 3, 4
    game_status = INIT
    #時間管理
    clock = pygame.time.Clock()

    """Sprite登録"""
    group = pygame.sprite.RenderUpdates()
    bomb_g = pygame.sprite.Group()
    beam_g = pygame.sprite.Group()
    Majo.containers = group
    Beam.containers = group, beam_g
    Ufo.containers = group
    Bomb.containers = group, bomb_g
    Explosion.containers = group
    Point.containers = group
    Score.containers = group

    """登場する人/物/背景の作成"""
    Beam.image = load_image("majo_beam.png")
    Beam.sound = load_sound("se_maoudamashii_battle07.ogg")
    Ufo.images = load_image("all_ufo3.png",(128,28))
    Ufo.exp_images = load_image("pipo-btleffect012.png", (320, 960))
    Ufo.exp_sound = load_sound("se_maoudamashii_se_syber08.ogg")
    Bomb.images = load_image("ufo_bomb.png")
    Bomb.exp_images = load_image("pipo-btleffect009.png")
    Bomb.exp_sound = load_sound("se_maoudamashii_magical10.ogg")
    Beam.exp_images = load_image("pipo-btleffect003.png")
    Beam.exp_sound = load_sound("se_maoudamashii_explosion06.ogg")
    Majo.life = Score(
        initval = 3,
        maxval = 3,
        pos = (SCREEN.right - 130, 5),
        color = Score.RED,
        font ="ipaexg.ttf",
        form = "残り： #",
        pat ="●○"
    )
    Majo.score = Score(pos=(230, 5), form ="SCORE: #")
    Majo.hi_score = HiScore(Majo.score, pos=(370, 5), form="(HIGH #)")
    Majo.stage = Score(initval =1, pos=(10,5), form="ST: #")
    Ufo.score = Score(initval = 15, pos=(110, 5), form="UFO: #")
    Majo.exp_images = load_image("pipo-btleffect017.png")
    Majo.exp_sound = load_sound("se_maoudamashii_magical26.ogg")
    Majo.exp_sound.set_volume(0.7)
    title_msg = {
        INIT: load_image("opening-logo.png"),
        GAMEOVER: load_image("GAMEOVER.png"),
        CLEAR: load_image("GameClear.png"),
    }
    opening_sound = load_sound("bgm_maoudamashii_healing13.ogg")
    opening_sound.set_volume(0.5)
    opening_sound.play(-1)
    play_sound = load_sound("bgm_maoudamashii_cyber37.ogg")
    play_sound.set_volume(0.4)
    majo = Majo()
    bg_img = Background(majo)
    #ufo = Ufo()
    while True:
        """画面(screen)をクリア"""
        screen.fill((0,0,0))

        """ゲームに登場する人/物/背景の位置Update"""
        bg_img.update()
        group.update()

        """画面(screen)上に登場する人/物/背景を描画"""
        bg_img.draw(screen)
        group.draw(screen)
        if game_status != PLAY:
            screen.blit(title_msg[game_status], (100, 150))

        """衝突判定"""
        if game_status == PLAY:
            collision_detection(majo, ufo, beam_g, bomb_g)

        """画面(screen)の実表示"""
        pygame.display.update()
        """ゲームステータスの変更"""
        if game_status == PLAY and Majo.life.val == 0:
            game_status = GAMEOVER
            play_sound.stop()
            opening_sound.play(-1)
        if game_status == PLAY and Ufo.score.val == 0:
            game_status = CLEAR
            play_sound.stop()
            opening_sound.play(-1)
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE and game_status == PLAY:
                    if Beam.counter < 2:
                        Beam(majo)
                elif event.key == K_SPACE and game_status == INIT:
                    game_status = PLAY
                    ufo = Ufo()
                    opening_sound.stop()
                    play_sound.play(-1)
                elif event.key == K_c and game_status == CLEAR:
                    game_status = PLAY
                    ufo.kill()
                    ufo = Ufo()
                    Ufo.score.reset()
                    Majo.stage.val += 1
                    opening_sound.stop()
                    play_sound.play(-1)
                elif event.key == K_r and game_status == GAMEOVER:
                    game_status = PLAY
                    ufo.kill()
                    majo.kill()
                    ufo = Ufo()
                    majo = Majo()
                    Ufo.score.reset()
                    Majo.life.reset()
                    opening_sound.stop()
                    play_sound.play(-1)
                    bg_img = Background(majo)
                    Majo.score.reset()
                    Majo.stage.reset()
        pressed_keys = pygame.key.get_pressed()
        """押されているキーに応じて画像を移動"""
        if pressed_keys[K_LEFT]:
            majo.move_left()
        elif pressed_keys[K_RIGHT]:
            majo.move_right()

        """描画スピードの調整(FPS)"""
        clock.tick(60)

if __name__ == "__main__":
    main()