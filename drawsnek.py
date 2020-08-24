"""
Draw a snek
"""

__version__ = "0.1"

import sys
import time

from random import SystemRandom

random = SystemRandom()

from typing import Callable, Dict, List, Sequence

from twisted.internet.task import LoopingCall
from twisted.python.filepath import FilePath
from twisted.internet import reactor
from twisted.internet.threads import deferToThread

from attr import dataclass, Factory
import pygame
import pygame.locals

# https://opengameart.org/content/animated-snake
spriteSheet = pygame.image.load(
    FilePath(__file__).sibling("snake spritesheet calciumtrice.png").path
)


@dataclass
class Sprite:
    images: Sequence[pygame.Surface]
    x: int
    y: int
    index: int = 0

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


def spriteRow(y, height=16, scaleFactor=16):
    images = []
    for x in range(10):
        images.append(
            pygame.transform.scale(
                spriteSheet.subsurface(x * 32, y, 32, height),
                (32 * scaleFactor, height * scaleFactor),
            )
        )
    return images


@dataclass
class Engine:
    drawables: List[Sprite] = Factory(list)
    keyPressHandlers: Dict[int, Callable] = Factory(dict)

    def start(self):
        screen = pygame.display.set_mode(
            (640 * 2, 480 * 2), pygame.locals.SCALED | pygame.locals.FULLSCREEN, vsync=1
        )

        def handleEvents():
            for event in pygame.event.get():
                if event.type == pygame.locals.KEYUP:
                    handler = self.keyPressHandlers.get(event.key)
                    if handler:
                        handler()

        def drawScene():
            screen.fill((0, 0, 0))
            for drawable in self.drawables:
                drawable.draw(screen)
            return deferToThread(pygame.display.flip)

        LoopingCall(drawScene).start(1 / 62.0)
        LoopingCall(handleEvents).start(1 / 120.0)

    def handleKey(self, key) -> Callable:
        def decorator(decorated):
            self.keyPressHandlers[key] = decorated
            return decorated

        return decorator


def main():
    from twisted.logger import globalLogBeginner, textFileLogObserver

    globalLogBeginner.beginLoggingTo([textFileLogObserver(sys.stdout)])

    engine = Engine()

    @engine.handleKey(pygame.locals.K_s)
    def snek():
        animationIndex = random.randint(0, 4)
        images = spriteRow(16 + (32 * animationIndex))
        sprite = Sprite(images, random.randint(0, 400), random.randint(0, 400))
        moveSpeed = random.randint(50, 100)
        animateSpeed = random.randint(5, 35)
        LoopingCall.withCount(sprite.animate).start(1.0 / animateSpeed)
        LoopingCall.withCount(Mover(sprite).move).start(1.0 / moveSpeed)
        engine.drawables.append(sprite)

    @engine.handleKey(pygame.locals.K_q)
    def stop():
        reactor.stop()

    @engine.handleKey(pygame.locals.K_h)
    def hiccup():
        time.sleep(random.random())

    pygame.display.set_caption("Draw Snek")
    engine.start()
    reactor.run()


main()
