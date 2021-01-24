import pygame
from pygame.locals import *
import sys

def main():
    """ 初期設定 """
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    SCREEN = screen.get_rect()
    pygame.display.set_caption("Hello World")
    clock = pygame.time.Clock()

    """登場する人/物/背景の作成"""
    circle_surface = pygame.Surface((20,20))
    circle_surface.set_colorkey((0,0,0))
    circle_rect = circle_surface.get_rect()
    circle_rect.topleft = (300,150)
    dx, dy = 5, 4
    pygame.draw.circle(circle_surface, (255,255,255), (10,10), 10)
    rectangle_surface = pygame.Surface((100,60))
    pygame.draw.rect(rectangle_surface, (255,0,0),(0,0,100,60))
    line_surface =pygame.Surface((100, 50))
    line_surface.set_colorkey((0,0,0))
    pygame.draw.line(line_surface, (0, 255, 0), (0,0), (100,50))
    while True:
        """画面(screen)をクリア"""
        screen.fill((0,0,0))
        """ゲームに登場する人/物/背景の位置Update"""
        circle_rect.move_ip(dx, dy)
        if circle_rect.left < SCREEN.left or circle_rect.right > SCREEN.right:
            dx = -dx
        if circle_rect.top < SCREEN.top or circle_rect.bottom > SCREEN.bottom:
            dy = -dy
        circle_rect.clamp_ip(SCREEN)

        """画面(screen)上に登場する人/物/背景を描画"""
        screen.blit(rectangle_surface,(150,150))
        screen.blit(circle_surface,circle_rect.topleft)
        screen.blit(line_surface,(250,250))
        """画面(screen)の実表示"""
        pygame.display.update()

        """イベント処理"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        """描画スピードの調整(FPS)"""
        clock.tick(60)

if __name__ == "__main__":
    main()