import pygame
from pygame.locals import *
import sys
import math

SCREEN = Rect((0,0,400, 600))

class Paddle:
    def __init__(self):
        self.image = pygame.Surface((50,10))
        self.image.fill((255,255,255))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN.centerx, SCREEN.bottom - 50)

    def update(self):
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect.clamp_ip(SCREEN)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Ball:
    def __init__(self,pad):
        self.image = pygame.Surface((20,20))
        pygame.draw.circle(self.image, (255,255,255), (10,10), 10)
        self.rect = self.image.get_rect()
        self.pad = pad
        self.rect.centerx = self.pad.rect.centerx
        self.rect.bottom = self.pad.rect.top
        self.dx, self.dy = 3, -4
        self.status = "INIT"

    def start(self):
        self.status = "RUNNING"

    def update(self):
        if self.status == "INIT":
            self.rect.centerx = self.pad.rect.centerx
            self.rect.bottom = self.pad.rect.top
            return
        old_rect = self.rect.copy()
        self.rect.move_ip(self.dx,self.dy)
        if self.rect.colliderect(self.pad.rect):
            if self.pad.rect.left >= old_rect.right:
                self.rect.right = self.pad.rect.left
                self.dx = -self.dx
            elif self.pad.rect.right <= old_rect.left:
                self.rect.left = self.pad.rect.right
                self.dx = -self.dx
            elif self.pad.rect.top >= old_rect.bottom:
                self.rect.bottom = self.pad.rect.top
                x = self.rect.centerx - self.pad.rect.left
                y = - 100 * x / self.pad.rect.width + 135
                self.dx = 5 * math.cos(math.radians(y))
                self.dy = -5 * math.sin(math.radians(y))
            else:
                self.rect.top = self.pad.rect.bottom
                self.dy = -self.dy

        if self.rect.left < SCREEN.left or self.rect.right > SCREEN.right:
            self.dx = -self.dx
        if self.rect.top < SCREEN.top or self.rect.bottom > SCREEN.bottom:
            self.dy = -self.dy
        if self.rect.bottom >= SCREEN.bottom - 5:
            self.status = "INIT"
        self.rect.clamp_ip(SCREEN)

    def draw(self,screen):
        screen.blit(self.image, self.rect)

def main():
    """ 初期設定 """
    pygame.init()
    screen = pygame.display.set_mode(SCREEN.size)
    pygame.display.set_caption('SQUASH GAME')

    clock = pygame.time.Clock()

    """登場する人/物/背景の作成"""
    pad = Paddle()
    ball = Ball(pad)

    while True:
        """画面(screen)をクリア"""
        screen.fill((0,0,0))

        """ゲームに登場する人/物/背景の位置Update"""
        pad.update()
        ball.update()

        """画面(screen)上に登場する人/物/背景を描画"""
        pad.draw(screen)
        ball.draw(screen)

        """画面(screen)の実表示"""
        pygame.display.update()

        """イベント処理"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                ball.start()

        """描画スピードの調整(FPS)"""
        clock.tick(120)

if __name__ == "__main__":
    main()