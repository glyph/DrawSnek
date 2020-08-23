"""
Draw a snek
"""

__version__ = "0.1"

import sys

from typing import Sequence

from twisted.internet.task import LoopingCall
from twisted.python.filepath import FilePath
from twisted.internet import reactor
from twisted.internet.threads import deferToThread

from attr import dataclass
import pygame
import pygame.locals

# https://opengameart.org/content/animated-snake
spriteSheet = pygame.image.load(
    FilePath(__file__).sibling("snake spritesheet calciumtrice.png").path
)


@dataclass
class Sprite:
    images: Sequence[pygame.Surface]
    index: int
    x: int
    y: int

    def draw(self, surface):
        img = self.images[self.index]
        surface.blit(img, (self.x, self.y))

    def animate(self, frameCount):
        self.index += frameCount
        self.index %= len(self.images)


@dataclass
class Mover(object):
    sprite: Sprite
    dx: int = 1
    dy: int = 1
    maxX: int = ((640 * 2) - (16 * 32))
    minX: int = 0
    maxY: int = ((480 * 2) - (16 * 16))
    minY: int = 0

    def move(self, frameCount):
        self.sprite.x += frameCount * self.dx
        self.sprite.y += frameCount * self.dy
        if self.sprite.x > self.maxX:
            self.dx *= -1
            self.sprite.x = max(
                self.minX, (self.sprite.x - (self.sprite.x - self.maxX))
            )
        if self.sprite.x < self.minX:
            self.dx *= -1
            self.sprite.x = min(self.maxX, (self.minX + (self.minX - self.sprite.x)))
        if self.sprite.y > self.maxY:
            self.dy *= -1
            self.sprite.y = max(
                self.minY, (self.sprite.y - (self.sprite.y - self.maxY))
            )
        if self.sprite.y < self.minY:
            self.dy *= -1
            self.sprite.y = min(self.maxY, (self.minY + (self.minY - self.sprite.y)))


def spriteRow(y, height, scaleFactor=16):
    images = []
    for x in range(10):
        images.append(
            pygame.transform.scale(
                spriteSheet.subsurface(x * 32, y, 32, height),
                (32 * scaleFactor, height * scaleFactor),
            )
        )
    return images


def main():
    from twisted.logger import globalLogBeginner, textFileLogObserver

    globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])
    screen = pygame.display.set_mode((640 * 2, 480 * 2), pygame.locals.SCALED, vsync=1)
    sprites = [
        Sprite(spriteRow(16, 16), 0, 100, 0),
        Sprite(spriteRow((32 * 3) + 16, 16), 0, 50, 50),
        Sprite(spriteRow((32 * 1) + 16, 16), 0, 50, 50),
    ]

    def drawScene():
        pygame.event.get()
        screen.fill((0, 0, 0))
        for each in sprites:
            each.draw(screen)
        return deferToThread(pygame.display.flip)
        # return deferToThread()

    def animateSprite(oneSprite, moveSpeed, animateSpeed):
        LoopingCall.withCount(oneSprite.animate).start(1.0 / animateSpeed)
        LoopingCall.withCount(Mover(oneSprite).move).start(1.0 / moveSpeed)

    LoopingCall(drawScene).start(1 / 62.0)
    for eachSprite, (eachMoveSpeed, eachAnimSpeed) in zip(
        sprites, [(100, 15), (30, 20), (60, 10)]
    ):
        animateSprite(eachSprite, eachMoveSpeed, eachAnimSpeed)

    pygame.display.set_caption("Draw Snek")
    print(pygame.display.Info())
    reactor.run()


main()
