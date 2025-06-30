# utils.py - 유틸리티 함수들

import math
import pygame
import random

def distance(pos1, pos2):
    """두 점 사이의 거리를 계산"""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def normalize_vector(vector):
    """벡터를 정규화"""
    length = math.sqrt(vector[0]**2 + vector[1]**2)
    if length == 0:
        return (0, 0)
    return (vector[0] / length, vector[1] / length)

def lerp(start, end, t):
    """선형 보간"""
    return start + (end - start) * t

def clamp(value, min_val, max_val):
    """값을 범위 내로 제한"""
    return max(min_val, min(max_val, value))

def create_explosion_particles(center, count=20):
    """폭발 파티클 생성"""
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 7)
        particles.append({
            'x': center[0],
            'y': center[1],
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'life': 60,
            'max_life': 60,
            'size': random.uniform(2, 6)
        })
    return particles

def draw_circle_outline(surface, color, center, radius, width=3, alpha=255):
    """투명도가 적용된 원 테두리 그리기"""
    if alpha < 255:
        temp_surface = pygame.Surface((radius * 2 + width * 2, radius * 2 + width * 2))
        temp_surface.set_alpha(alpha)
        pygame.draw.circle(temp_surface, color, (radius + width, radius + width), radius, width)
        surface.blit(temp_surface, (center[0] - radius - width, center[1] - radius - width))
    else:
        pygame.draw.circle(surface, color, center, radius, width)