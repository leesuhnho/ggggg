# effects.py - 시각 효과 클래스

import pygame
import math
import random
from config import *


class VisualEffects:
    def __init__(self):
        self.particles = []
        self.time = 0
        self.floating_particles = []

    def update(self):
        self.time += 1

        # 배경 파티클 생성 (더 적게, 더 자연스럽게)
        if self.time % 40 == 0:  # 생성 빈도 감소
            self.particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT - UI_HEIGHT),
                'life': 300,  # 더 긴 수명
                'max_life': 300,
                'size': random.randint(1, 3),
                'speed': random.uniform(0.2, 0.8),  # 더 느린 속도
                'direction': random.uniform(0, 2 * math.pi),
                'twinkle': random.randint(0, 60)
            })

        # 떠다니는 파티클 생성
        if self.time % 80 == 0:
            self.floating_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': SCREEN_HEIGHT - UI_HEIGHT,
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-1, -0.3),
                'life': 400,
                'max_life': 400,
                'size': random.randint(2, 5)
            })

        # 파티클 업데이트
        self._update_particles()
        self._update_floating_particles()

    def _update_particles(self):
        self.particles = [p for p in self.particles if p['life'] > 0]
        for particle in self.particles:
            particle['life'] -= 1
            particle['x'] += math.cos(particle['direction']) * particle['speed']
            particle['y'] += math.sin(particle['direction']) * particle['speed']
            particle['twinkle'] = (particle['twinkle'] + 1) % 120

    def _update_floating_particles(self):
        self.floating_particles = [p for p in self.floating_particles if p['life'] > 0]
        for particle in self.floating_particles:
            particle['life'] -= 1
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] -= 0.01  # 중력 효과

    def draw_background_effect(self, screen):
        # 부드러운 그라디언트 배경 (그리드 라인 제거)
        for y in range(SCREEN_HEIGHT - UI_HEIGHT):
            # 더 부드러운 웨이브 효과
            wave1 = math.sin(self.time * 0.005 + y * 0.002) * 15
            wave2 = math.cos(self.time * 0.008 + y * 0.001) * 10

            # 더 어두운 베이스 색상
            base_r = 8 + int(wave1)
            base_g = 12 + int(wave2)
            base_b = 30 + int(wave1 + wave2)

            color = (max(0, min(255, base_r)),
                     max(0, min(255, base_g)),
                     max(0, min(255, base_b)))
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

        # 배경 파티클 (별처럼 반짝이는 효과)
        self._draw_background_particles(screen)

        # 떠다니는 파티클
        self._draw_floating_particles(screen)

    def _draw_background_particles(self, screen):
        for particle in self.particles:
            alpha_base = int(255 * (particle['life'] / particle['max_life']) * 0.6)

            # 깜빡이는 효과
            twinkle_alpha = math.sin(particle['twinkle'] * 0.1) * 0.5 + 0.5
            alpha = int(alpha_base * twinkle_alpha)

            if alpha > 0:
                # 다양한 색상의 파티클
                life_ratio = particle['life'] / particle['max_life']
                if life_ratio > 0.7:
                    color = WHITE
                elif life_ratio > 0.4:
                    color = CYAN
                else:
                    color = BLUE

                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
                particle_surface.set_alpha(alpha)
                particle_surface.fill(color)
                screen.blit(particle_surface, (particle['x'] - particle['size'],
                                               particle['y'] - particle['size']))

    def _draw_floating_particles(self, screen):
        for particle in self.floating_particles:
            alpha = int(255 * (particle['life'] / particle['max_life']) * 0.4)
            if alpha > 0:
                # 위로 떠오르는 파티클 (먼지나 에너지 효과)
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
                particle_surface.set_alpha(alpha)

                # 생명에 따른 색상 변화
                life_ratio = particle['life'] / particle['max_life']
                color_r = int(100 * life_ratio)
                color_g = int(150 * life_ratio)
                color_b = int(255 * life_ratio)

                particle_surface.fill((color_r, color_g, color_b))
                screen.blit(particle_surface, (particle['x'] - particle['size'],
                                               particle['y'] - particle['size']))

    def add_impact_effect(self, x, y, color=WHITE, intensity=1.0):
        """충격 효과 추가 (폭발이나 충돌 시 사용)"""
        count = int(10 * intensity)
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6) * intensity
            self.particles.append({
                'x': x,
                'y': y,
                'life': 60,
                'max_life': 60,
                'size': random.randint(2, 4),
                'speed': speed,
                'direction': angle,
                'twinkle': 0,
                'color': color
            })