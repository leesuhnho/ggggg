# item.py - 아이템 시스템

import pygame
import math
import random
from config import *
from utils import *


class HealthPack:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = HEALTH_PACK_SIZE
        self.heal_amount = HEALTH_PACK_HEAL_AMOUNT
        self.collected = False

        # 물리 속성
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-8, -4)  # 위쪽으로 초기 속도
        self.on_ground = False
        self.bounce_count = 0

        # 시각 효과
        self.glow_intensity = 255
        self.pulse_timer = 0
        self.particles = []

    def update(self, obstacle_manager):
        if self.collected:
            return

        # 물리 업데이트
        self._apply_physics(obstacle_manager)

        # 시각 효과 업데이트
        self._update_effects()

    def _apply_physics(self, obstacle_manager):
        # 중력 적용
        if not self.on_ground:
            self.vy += GRAVITY
            self.vy = min(self.vy, TERMINAL_VELOCITY)

        # 위치 업데이트
        new_x = self.x + self.vx
        new_y = self.y + self.vy

        # 지면 충돌 체크 (월드 바닥)
        if new_y + self.size >= WORLD_HEIGHT - 20:
            new_y = WORLD_HEIGHT - 20 - self.size
            if self.vy > 2:  # 충분한 속도일 때만 바운스
                self.vy = -self.vy * BOUNCE_DAMPING
                self.bounce_count += 1
            else:
                self.vy = 0
                self.on_ground = True

        # 장애물 충돌 체크
        item_rect = pygame.Rect(new_x, new_y, self.size, self.size)
        hit_obstacle = obstacle_manager.check_collision_rect(item_rect)

        if hit_obstacle:
            # 위에서 떨어진 경우
            if self.vy > 0:
                new_y = hit_obstacle.y - self.size
                self.vy = -self.vy * BOUNCE_DAMPING if self.vy > 2 else 0
                self.on_ground = True
            # 옆에서 부딪힌 경우
            else:
                self.vx = -self.vx * 0.5

        # 마찰 적용
        if self.on_ground:
            self.vx *= FRICTION

        # 위치 적용
        self.x = clamp(new_x, 0, WORLD_WIDTH - self.size)
        self.y = clamp(new_y, 0, WORLD_HEIGHT - self.size)

        # 정지 상태 체크
        if abs(self.vx) < 0.1 and self.on_ground:
            self.vx = 0

    def _update_effects(self):
        self.pulse_timer += 1

        # 글로우 펄스 효과
        pulse = math.sin(self.pulse_timer * 0.1) * 0.3 + 0.7
        self.glow_intensity = int(255 * pulse)

        # 치유 파티클 생성
        if self.pulse_timer % 20 == 0:
            self.particles.append({
                'x': self.x + self.size // 2 + random.uniform(-5, 5),
                'y': self.y + self.size // 2 + random.uniform(-5, 5),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-2, -0.5),
                'life': 40,
                'max_life': 40,
                'size': random.uniform(2, 4)
            })

        # 파티클 업데이트
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def check_pickup(self, player_x, player_y, player_size):
        """플레이어와의 픽업 체크"""
        if self.collected:
            return False

        dist = distance((self.x + self.size // 2, self.y + self.size // 2),
                        (player_x, player_y))

        if dist <= (self.size // 2 + player_size // 2 + 10):
            self.collected = True
            self._create_pickup_effect()
            return True
        return False

    def _create_pickup_effect(self):
        """픽업 시 파티클 효과"""
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': self.x + self.size // 2,
                'y': self.y + self.size // 2,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 30,
                'max_life': 30,
                'size': random.uniform(3, 6)
            })

    def draw(self, screen, camera):
        if self.collected and len(self.particles) == 0:
            return

        # 화면에 보이는지 체크
        if not camera.is_visible(self.x, self.y, self.size):
            return

        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # 파티클 그리기
        for particle in self.particles:
            if camera.is_visible(particle['x'], particle['y']):
                p_screen_x, p_screen_y = camera.world_to_screen(particle['x'], particle['y'])
                alpha = int(255 * (particle['life'] / particle['max_life']))
                if alpha > 0:
                    particle_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)))
                    particle_surface.set_alpha(alpha)
                    particle_surface.fill(GREEN)
                    screen.blit(particle_surface, (p_screen_x - particle['size'],
                                                   p_screen_y - particle['size']))

        if not self.collected:
            # 글로우 효과
            glow_surface = pygame.Surface((self.size * 3, self.size * 3))
            glow_surface.set_alpha(self.glow_intensity // 3)
            glow_surface.fill(GREEN)
            screen.blit(glow_surface, (screen_x - self.size, screen_y - self.size))

            # 메인 체력팩 (십자가 모양)
            # 배경 원
            pygame.draw.circle(screen, WHITE, (int(screen_x + self.size // 2),
                                               int(screen_y + self.size // 2)), self.size // 2)
            pygame.draw.circle(screen, GREEN, (int(screen_x + self.size // 2),
                                               int(screen_y + self.size // 2)), self.size // 2 - 2)

            # 십자가
            cross_size = self.size // 3
            # 세로선
            pygame.draw.rect(screen, WHITE,
                             (screen_x + self.size // 2 - 2, screen_y + cross_size,
                              4, cross_size))
            # 가로선
            pygame.draw.rect(screen, WHITE,
                             (screen_x + cross_size, screen_y + self.size // 2 - 2,
                              cross_size, 4))


class ItemManager:
    def __init__(self):
        self.health_packs = []
        self.spawn_timer = 0

    def update(self, obstacle_manager, player):
        # 체력팩 스폰
        self.spawn_timer += 1
        if self.spawn_timer >= HEALTH_PACK_SPAWN_RATE:
            if len(self.health_packs) < 5:  # 최대 5개
                self._spawn_health_pack(obstacle_manager)
            self.spawn_timer = 0

        # 체력팩 업데이트
        for health_pack in self.health_packs[:]:
            health_pack.update(obstacle_manager)

            # 플레이어 픽업 체크
            if health_pack.check_pickup(player.x, player.y, player.size):
                if player.hp < player.max_hp:
                    heal_amount = min(health_pack.heal_amount, player.max_hp - player.hp)
                    player.hp += heal_amount
                    # 픽업 효과는 health_pack에서 처리됨

            # 수집된 아이템 제거 (파티클 완료 후)
            if health_pack.collected and len(health_pack.particles) == 0:
                self.health_packs.remove(health_pack)

    def _spawn_health_pack(self, obstacle_manager):
        """체력팩 스폰"""
        attempts = 0
        while attempts < 20:
            # 하늘에서 떨어뜨리기
            x = random.randint(100, WORLD_WIDTH - 100)
            y = random.randint(50, 200)  # 위쪽 공중에서

            # 장애물과 겹치지 않는 위치 찾기
            if not obstacle_manager.check_collision_circle(x, y, HEALTH_PACK_SIZE):
                health_pack = HealthPack(x, y)
                self.health_packs.append(health_pack)
                break

            attempts += 1

    def draw(self, screen, camera):
        for health_pack in self.health_packs:
            health_pack.draw(screen, camera)

    def get_health_packs(self):
        return [hp for hp in self.health_packs if not hp.collected]