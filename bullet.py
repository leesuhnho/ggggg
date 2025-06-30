# bullet.py - 총알 시스템 (업그레이드)

import pygame
import math
import random
from config import *
from utils import *


class Bullet:
    def __init__(self, start_x, start_y, vx, vy, damage, color, weapon_type):
        self.x = start_x
        self.y = start_y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.color = color
        self.weapon_type = weapon_type
        self.size = BULLET_SIZE
        self.lifetime = BULLET_LIFETIME
        self.trail = []

        # 무기별 특수 효과
        if weapon_type == 'SNIPER':
            self.size = 6  # 더 큰 총알
            self.glow_intensity = 255
        else:
            self.glow_intensity = 150

        # 총알 효과
        self.spark_particles = []

    def update(self):
        # 위치 업데이트
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        # 트레일 업데이트
        self.trail.append((self.x, self.y))
        trail_length = 12 if self.weapon_type == 'SNIPER' else 8
        if len(self.trail) > trail_length:
            self.trail.pop(0)

        # 글로우 효과 감소
        self.glow_intensity = max(50, self.glow_intensity - 2)

        # 스파크 파티클 생성 (저격총은 더 많이)
        spark_count = 2 if self.weapon_type == 'SNIPER' else 1
        if len(self.spark_particles) < spark_count * 3:
            for _ in range(spark_count):
                self.spark_particles.append({
                    'x': self.x + random.uniform(-2, 2),
                    'y': self.y + random.uniform(-2, 2),
                    'vx': random.uniform(-1, 1),
                    'vy': random.uniform(-1, 1),
                    'life': 15,
                    'size': random.uniform(1, 3)
                })

        # 스파크 파티클 업데이트
        for particle in self.spark_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.spark_particles.remove(particle)

        # 월드 경계 체크
        if (self.x < 0 or self.x > WORLD_WIDTH or
                self.y < 0 or self.y > WORLD_HEIGHT):
            self.lifetime = 0

    def draw(self, screen, camera):
        # 화면에 보이는지 체크
        if not camera.is_visible(self.x, self.y, self.size):
            return

        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # 트레일 그리기
        for i, (trail_x, trail_y) in enumerate(self.trail):
            trail_screen_x, trail_screen_y = camera.world_to_screen(trail_x, trail_y)
            alpha = int(255 * (i / len(self.trail)) * 0.7)
            if alpha > 0:
                trail_surface = pygame.Surface((self.size * 2, self.size * 2))
                trail_surface.set_alpha(alpha)
                trail_surface.fill(self.color)
                screen.blit(trail_surface, (trail_screen_x - self.size, trail_screen_y - self.size))

        # 글로우 효과
        glow_size = self.size * 8 if self.weapon_type == 'SNIPER' else self.size * 6
        glow_surface = pygame.Surface((glow_size, glow_size))
        glow_surface.set_alpha(self.glow_intensity // 4)
        glow_surface.fill(self.color)
        screen.blit(glow_surface, (screen_x - glow_size // 2, screen_y - glow_size // 2))

        # 메인 총알
        pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), self.size)
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.size - 1)

        # 저격총 특수 효과
        if self.weapon_type == 'SNIPER':
            pygame.draw.circle(screen, YELLOW, (int(screen_x), int(screen_y)), self.size - 2)

        # 스파크 파티클
        for particle in self.spark_particles:
            particle_screen_x, particle_screen_y = camera.world_to_screen(particle['x'], particle['y'])
            alpha = int(255 * (particle['life'] / 15))
            if alpha > 0:
                spark_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)))
                spark_surface.set_alpha(alpha)
                spark_surface.fill(YELLOW)
                screen.blit(spark_surface, (particle_screen_x - particle['size'],
                                            particle_screen_y - particle['size']))

    def is_alive(self):
        return self.lifetime > 0

    def get_position(self):
        return (self.x, self.y)

    def get_bounds(self):
        return (self.x - self.size, self.y - self.size,
                self.x + self.size, self.y + self.size)


class BulletManager:
    def __init__(self):
        self.bullets = []

    def add_bullet(self, start_x, start_y, vx, vy, damage, color, weapon_type):
        bullet = Bullet(start_x, start_y, vx, vy, damage, color, weapon_type)
        self.bullets.append(bullet)

    def update(self, enemies, obstacle_manager):
        # 총알 업데이트
        for bullet in self.bullets[:]:
            bullet.update()

            # 생존 체크
            if not bullet.is_alive():
                self.bullets.remove(bullet)
                continue

            # 장애물 충돌 체크
            bullet_rect = pygame.Rect(bullet.x - bullet.size, bullet.y - bullet.size,
                                      bullet.size * 2, bullet.size * 2)
            hit_obstacle = obstacle_manager.check_collision_rect(bullet_rect)
            if hit_obstacle:
                # 파괴 가능한 장애물에 데미지
                if hit_obstacle.destructible:
                    hit_obstacle.take_damage(bullet.damage // 2)  # 총알 데미지의 절반
                self.bullets.remove(bullet)
                continue

            # 적군과의 충돌 체크
            bullet_x, bullet_y = bullet.get_position()
            for enemy in enemies:
                if not enemy.is_dead:
                    enemy_dist = distance((bullet_x, bullet_y), (enemy.x, enemy.y))
                    if enemy_dist <= (bullet.size + enemy.size // 2):
                        # 히트!
                        enemy.take_damage(bullet.damage)
                        self._create_hit_effect(bullet_x, bullet_y, bullet.weapon_type)
                        self.bullets.remove(bullet)
                        break
        # 총알 업데이트
        for bullet in self.bullets[:]:
            bullet.update()

            # 생존 체크
            if not bullet.is_alive():
                self.bullets.remove(bullet)
                continue

            # 장애물 충돌 체크
            bullet_rect = pygame.Rect(bullet.x - bullet.size, bullet.y - bullet.size,
                                      bullet.size * 2, bullet.size * 2)
            hit_obstacle = obstacle_manager.check_collision_rect(bullet_rect)
            if hit_obstacle:
                # 파괴 가능한 장애물에 데미지
                if hit_obstacle.destructible:
                    hit_obstacle.take_damage(bullet.damage // 2)  # 총알 데미지의 절반
                self.bullets.remove(bullet)
                continue

            # 적군과의 충돌 체크
            bullet_x, bullet_y = bullet.get_position()
            for enemy in enemies:
                if not enemy.is_dead:
                    enemy_dist = distance((bullet_x, bullet_y), (enemy.x, enemy.y))
                    if enemy_dist <= (bullet.size + enemy.size // 2):
                        # 히트!
                        enemy.take_damage(bullet.damage)
                        self._create_hit_effect(bullet_x, bullet_y, bullet.weapon_type)
                        self.bullets.remove(bullet)
                        break

    def _create_hit_effect(self, x, y, weapon_type):
        """총알 히트 효과 생성"""
        # 무기별 다른 히트 효과
        if weapon_type == 'SNIPER':
            # 저격총은 더 강한 효과
            pass
        # 나중에 effects 시스템과 연동

    def draw(self, screen, camera):
        for bullet in self.bullets:
            bullet.draw(screen, camera)

    def get_bullets(self):
        return self.bullets
    def get_dfie:
        print("jefjef")
