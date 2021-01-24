import pygame
from pygame.locals import *
import sys

"""クラスの定義"""

def main():
    """ 初期設定 """
    pygame.init()
    clock = pygame.time.Clock()

    """登場する人/物/背景の作成"""

    while True:
        """画面(screen)をクリア"""

        """ゲームに登場する人/物/背景の位置Update"""

        """画面(screen)上に登場する人/物/背景を描画"""

        """画面(screen)の実表示"""

        """イベント処理"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        """描画スピードの調整(FPS)"""
        clock.tick(60)

if __name__ == "__main__":
    main()
