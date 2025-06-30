# decoration.py - 맵 장식 시스템

import pygame
import random
import math
from config import *


class Decoration:
    def __init__(self, x, y, decoration_type):
        self.x = x
        self.y = y
        self.type = decoration_type
        self.animation_timer = 0

        # 타입별 설정
        if decoration_type == "lamp":
            self.width = 20
            self.height = 40
            self.color = (200, 200, 100)
            self.glow_color = YELLOW
            self.animated = True
        elif decoration_type == "pipe":
            self.width = random.choice([15, 25])
            self.height = random.randint(60, 120)
            self.color = (100, 100, 100)
            self.glow_color = None
            self.animated = False
        elif decoration_type == "vent":
            self.width = 40
            self.height = 30
            self.color = DARK_GRAY
            self.glow_color = None
            self.animated = True
        elif decoration_type == "machinery":
            self.width = random.randint(30, 60)
            self.height = random.randint(30, 50)
            self.color = (80, 80, 80)
            self.glow_color = GREEN
            self.animated = True
        elif decoration_type == "debris":
            self.width = random.randint(15, 25)
            self.height = random.randint(10, 20)
            self.color = (60, 60, 60)
            self.glow_color = None
            self.animated = False

    def update(self):
        if self.animated:
            self.animation_timer += 1

    def draw(self, screen, camera):
        # 화면에 보이는지 체크
        if not camera.is_visible(self.x, self.y, max(self.width, self.height)):
            return

        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # 타입별 그리기
        if self.type == "lamp":
            self._draw_lamp(screen, screen_x, screen_y)
        elif self.type == "pipe":
            self._draw_pipe(screen, screen_x, screen_y)
        elif self.type == "vent":
            self._draw_vent(screen, screen_x, screen_y)
        elif self.type == "machinery":
            self._draw_machinery(screen, screen_x, screen_y)
        elif self.type == "debris":
            self._draw_debris(screen, screen_x, screen_y)

    def _draw_lamp(self, screen, screen_x, screen_y):
        # 기둥
        pygame.draw.rect(screen, DARK_GRAY, (screen_x + 8, screen_y, 4, self.height))

        # 램프 머리
        lamp_intensity = 0.7 + 0.3 * math.sin(self.animation_timer * 0.1)
        lamp_color = tuple(int(c * lamp_intensity) for c in self.color)
        pygame.draw.circle(screen, lamp_color,
                           (screen_x + 10, screen_y + 10), 8)

        # 글로우 효과
        if self.glow_color:
            glow_surface = pygame.Surface((40, 40))
            glow_surface.set_alpha(int(100 * lamp_intensity))
            glow_surface.fill(self.glow_color)
            screen.blit(glow_surface, (screen_x - 10, screen_y - 10))

    def _draw_pipe(self, screen, screen_x, screen_y):
        # 메인 파이프
        pygame.draw.rect(screen, self.color,
                         (screen_x, screen_y, self.width, self.height))

        # 파이프 디테일
        pygame.draw.rect(screen, (120, 120, 120),
                         (screen_x + 2, screen_y, self.width - 4, self.height), 2)

        # 연결부
        for i in range(0, self.height, 20):
            pygame.draw.rect(screen, (140, 140, 140),
                             (screen_x - 2, screen_y + i, self.width + 4, 4))

    def _draw_vent(self, screen, screen_x, screen_y):
        # 베이스
        pygame.draw.rect(screen, self.color,
                         (screen_x, screen_y, self.width, self.height))

        # 통풍구 슬롯
        slot_count = 6
        for i in range(slot_count):
            slot_y = screen_y + 5 + i * 3
            pygame.draw.line(screen, BLACK,
                             (screen_x + 5, slot_y), (screen_x + self.width - 5, slot_y), 2)

        # 애니메이션 효과 (증기)
        if self.animation_timer % 60 < 30:
            steam_alpha = 50
            steam_surface = pygame.Surface((self.width - 10, 15))
            steam_surface.set_alpha(steam_alpha)
            steam_surface.fill(WHITE)
            screen.blit(steam_surface, (screen_x + 5, screen_y - 10))

    def _draw_machinery(self, screen, screen_x, screen_y):
        # 메인 기계
        pygame.draw.rect(screen, self.color,
                         (screen_x, screen_y, self.width, self.height))

        # 컨트롤 패널
        panel_size = min(self.width, self.height) // 3
        pygame.draw.rect(screen, (40, 40, 40),
                         (screen_x + 5, screen_y + 5, panel_size, panel_size))

        # LED 표시등 (깜빡임)
        if self.animation_timer % 60 < 30:
            led_color = self.glow_color
        else:
            led_color = (50, 50, 50)

        pygame.draw.circle(screen, led_color,
                           (screen_x + 8, screen_y + 8), 3)

    def _draw_debris(self, screen, screen_x, screen_y):
        # 잔해 더미
        pygame.draw.rect(screen, self.color,
                         (screen_x, screen_y, self.width, self.height))

        # 작은 조각들
        for _ in range(3):
            piece_x = screen_x + random.randint(0, self.width - 5)
            piece_y = screen_y + random.randint(0, self.height - 5)
            pygame.draw.rect(screen, (80, 80, 80), (piece_x, piece_y, 3, 3))


class DecorationManager:
    def __init__(self):
        self.decorations = []
        self._generate_decorations()

    def _generate_decorations(self):
        """장식 요소 생성"""
        decoration_types = ["lamp", "pipe", "vent", "machinery", "debris"]

        for _ in range(DECORATION_COUNT):
            attempts = 0
            while attempts < 20:
                x = random.randint(50, WORLD_WIDTH - 50)
                y = random.randint(50, WORLD_HEIGHT - 100)

                # 중앙 스폰 지역 피하기
                spawn_zone_x = WORLD_WIDTH // 2 - 300
                spawn_zone_y = WORLD_HEIGHT // 2 - 300

                if not (spawn_zone_x <= x <= spawn_zone_x + 600 and
                        spawn_zone_y <= y <= spawn_zone_y + 600):
                    decoration_type = random.choice(decoration_types)
                    decoration = Decoration(x, y, decoration_type)
                    self.decorations.append(decoration)
                    break

                attempts += 1

    def update(self):
        for decoration in self.decorations:
            decoration.update()

    def draw(self, screen, camera):
        for decoration in self.decorations:
            decoration.draw(screen, camera)