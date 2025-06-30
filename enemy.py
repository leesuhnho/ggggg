# enemy.py - 적군 AI 클래스 (수정된 버전)

import pygame
import math
import random
from config import *
from utils import *


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = ENEMY_SIZE
        self.speed = ENEMY_SPEED
        self.hp = ENEMY_HP
        self.max_hp = ENEMY_HP
        self.target_x = x
        self.target_y = y
        self.state = "patrol"  # patrol, chase, attack, smart_move
        self.chase_range = ENEMY_SIGHT_RANGE
        self.attack_range = ENEMY_ATTACK_RANGE
        self.patrol_timer = 0
        self.attack_cooldown = 0
        self.trail = []
        self.death_animation = 0
        self.is_dead = False

        # 향상된 AI
        self.last_player_pos = None
        self.search_timer = 0
        self.dodge_timer = 0
        self.stuck_timer = 0
        self.last_position = (x, y)
        self.smart_move_timer = 0
        self.aggression_level = random.uniform(0.5, 1.5)  # 개체별 공격성

        # 공격 시스템
        self.can_attack = True
        self.attack_damage = ENEMY_ATTACK_DAMAGE
        self.attack_particles = []

        # 레벨 스케일링
        self.level_multiplier = 1.0

        # 킬 카운트 처리를 위한 플래그
        self.kill_counted = False

    def _apply_level_scaling(self, level):
        """레벨에 따른 적군 강화"""
        self.level_multiplier = 1.0 + (level - 1) * 0.2  # 레벨당 20% 증가

        # 체력 증가
        self.hp = int(ENEMY_HP * self.level_multiplier)
        self.max_hp = self.hp

        # 속도 증가 (최대 2배)
        self.speed = min(ENEMY_SPEED * 2, ENEMY_SPEED * self.level_multiplier)

        # 공격력 증가
        self.attack_damage = int(ENEMY_ATTACK_DAMAGE * self.level_multiplier)

        # 공격성 증가
        self.aggression_level = min(2.0, self.aggression_level * self.level_multiplier)

    def update(self, player_pos, other_enemies, camera, obstacle_manager):
        if self.is_dead:
            self.death_animation += 1
            return

        player_x, player_y = player_pos
        distance_to_player = distance((self.x, self.y), (player_x, player_y))

        # AI 상태 결정 (향상된 로직)
        self._update_ai_state(player_pos, distance_to_player, other_enemies, obstacle_manager)

        # 상태별 행동
        if self.state == "patrol":
            self._patrol()
        elif self.state == "chase":
            self._chase(player_x, player_y, other_enemies, obstacle_manager)
        elif self.state == "attack":
            self._attack(player_pos)
        elif self.state == "smart_move":
            self._smart_move(player_x, player_y, other_enemies, obstacle_manager)

        # 이동 실행 (장애물 고려)
        self._move_towards_target(obstacle_manager)

        # 월드 경계 체크
        self._check_boundaries()

        # 트레일 업데이트
        self._update_trail()

        # 쿨다운 업데이트
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.dodge_timer > 0:
            self.dodge_timer -= 1
        if self.search_timer > 0:
            self.search_timer -= 1
        if self.smart_move_timer > 0:
            self.smart_move_timer -= 1

        # 공격 파티클 업데이트
        self._update_attack_particles()

        # 스택 체크
        self._check_stuck()

    def _update_ai_state(self, player_pos, distance_to_player, other_enemies, obstacle_manager):
        """향상된 AI 상태 결정"""
        player_x, player_y = player_pos

        # 플레이어가 시야 내에 있고 장애물에 가리지 않았는가?
        can_see_player = (distance_to_player <= self.chase_range and
                          not obstacle_manager.check_line_collision(self.x, self.y, player_x, player_y))

        if can_see_player:
            self.last_player_pos = player_pos
            self.search_timer = 120  # 2초간 기억

            if distance_to_player <= self.attack_range:
                self.state = "attack"
            else:
                # 스마트 이동 확률 체크
                if (random.random() < ENEMY_SMART_MOVE_CHANCE * self.aggression_level and
                        self.smart_move_timer <= 0):
                    self.state = "smart_move"
                    self.smart_move_timer = 60
                else:
                    self.state = "chase"
        elif self.search_timer > 0 and self.last_player_pos:
            # 마지막 위치로 이동
            self.state = "chase"
            player_x, player_y = self.last_player_pos
        else:
            self.state = "patrol"
            self.last_player_pos = None

    def _patrol(self):
        """순찰 행동"""
        self.patrol_timer += 1
        if self.patrol_timer >= 180:  # 3초마다 새로운 목표
            self.patrol_timer = 0
            # 현재 위치 근처로 랜덤 이동
            angle = random.uniform(0, 2 * math.pi)
            distance_patrol = random.uniform(50, 120)
            self.target_x = self.x + math.cos(angle) * distance_patrol
            self.target_y = self.y + math.sin(angle) * distance_patrol

    def _chase(self, player_x, player_y, other_enemies, obstacle_manager):
        """추격 행동 (향상된)"""
        # 기본 추격
        self.target_x = player_x
        self.target_y = player_y

        # 다른 적군과 겹치지 않도록 회피
        self._avoid_crowding(other_enemies)

    def _smart_move(self, player_x, player_y, other_enemies, obstacle_manager):
        """스마트 이동 (측면 공격, 포위 등)"""
        # 플레이어 주변으로 측면 이동
        angle_to_player = math.atan2(player_y - self.y, player_x - self.x)

        # 좌우 중 하나를 선택해서 측면 공격
        side_offset = math.pi / 2 if random.random() > 0.5 else -math.pi / 2
        flank_angle = angle_to_player + side_offset

        flank_distance = 60
        self.target_x = player_x + math.cos(flank_angle) * flank_distance
        self.target_y = player_y + math.sin(flank_angle) * flank_distance

        # 다른 적군과 겹치지 않도록
        self._avoid_crowding(other_enemies)

    def _avoid_crowding(self, other_enemies):
        """다른 적군과 겹치지 않도록 회피"""
        for other in other_enemies:
            if other != self and not other.is_dead:
                dist = distance((self.x, self.y), (other.x, other.y))
                if dist < 40:  # 너무 가까우면
                    # 반대 방향으로 이동
                    away_x = self.x - other.x
                    away_y = self.y - other.y
                    away_dist = math.sqrt(away_x ** 2 + away_y ** 2)
                    if away_dist > 0:
                        self.target_x += (away_x / away_dist) * 30
                        self.target_y += (away_y / away_dist) * 30

    def _attack(self, player_pos):
        """공격 행동"""
        player_x, player_y = player_pos

        # 플레이어를 향해 약간 이동
        self.target_x = player_x
        self.target_y = player_y

        # 공격 실행
        if self.attack_cooldown == 0 and self.can_attack:
            self._execute_attack(player_pos)
            self.attack_cooldown = 90  # 1.5초 쿨다운

    def _execute_attack(self, player_pos):
        """실제 공격 실행"""
        player_x, player_y = player_pos

        # 공격 파티클 생성
        for _ in range(8):
            angle = math.atan2(player_y - self.y, player_x - self.x)
            angle += random.uniform(-0.3, 0.3)
            speed = random.uniform(3, 6)

            self.attack_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 20,
                'max_life': 20,
                'size': random.uniform(2, 4)
            })

    def _move_towards_target(self, obstacle_manager):
        """목표를 향해 이동 (장애물 회피)"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance_to_target = math.sqrt(dx ** 2 + dy ** 2)

        if distance_to_target > 8:  # 목표에 충분히 가까우면 멈춤
            # 정규화된 방향 벡터
            move_x = (dx / distance_to_target) * self.speed * self.aggression_level
            move_y = (dy / distance_to_target) * self.speed * self.aggression_level

            new_x = self.x + move_x
            new_y = self.y + move_y

            # 장애물 충돌 체크
            if not obstacle_manager.check_collision_circle(new_x, new_y, self.size // 2):
                self.x, self.y = new_x, new_y
            else:
                # 장애물 회피 시도
                self._try_obstacle_avoidance(obstacle_manager, move_x, move_y)

    def _try_obstacle_avoidance(self, obstacle_manager, move_x, move_y):
        """장애물 회피 시도"""
        # X축만 이동 시도
        new_x = self.x + move_x
        if not obstacle_manager.check_collision_circle(new_x, self.y, self.size // 2):
            self.x = new_x
            return

        # Y축만 이동 시도
        new_y = self.y + move_y
        if not obstacle_manager.check_collision_circle(self.x, new_y, self.size // 2):
            self.y = new_y
            return

        # 대각선 회피 시도
        avoidance_angles = [math.pi / 4, -math.pi / 4, 3 * math.pi / 4, -3 * math.pi / 4]
        for angle in avoidance_angles:
            avoid_x = self.x + math.cos(angle) * self.speed
            avoid_y = self.y + math.sin(angle) * self.speed

            if not obstacle_manager.check_collision_circle(avoid_x, avoid_y, self.size // 2):
                self.x, self.y = avoid_x, avoid_y
                break

    def _check_boundaries(self):
        self.x = clamp(self.x, self.size // 2, WORLD_WIDTH - self.size // 2)
        self.y = clamp(self.y, self.size // 2, WORLD_HEIGHT - self.size // 2)

        # 경계에 닿으면 목표 위치 재설정
        if (self.x <= self.size // 2 or self.x >= WORLD_WIDTH - self.size // 2 or
                self.y <= self.size // 2 or self.y >= WORLD_HEIGHT - self.size // 2):
            self.target_x = WORLD_WIDTH // 2
            self.target_y = WORLD_HEIGHT // 2

    def _check_stuck(self):
        """스택 체크 및 해결"""
        current_pos = (self.x, self.y)
        if distance(current_pos, self.last_position) < 2:
            self.stuck_timer += 1
            if self.stuck_timer > 60:  # 1초 이상 스택
                # 랜덤 방향으로 이동
                angle = random.uniform(0, 2 * math.pi)
                self.target_x = self.x + math.cos(angle) * 50
                self.target_y = self.y + math.sin(angle) * 50
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0

        self.last_position = current_pos

    def _update_trail(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

    def _update_attack_particles(self):
        """공격 파티클 업데이트"""
        for particle in self.attack_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95

            if particle['life'] <= 0:
                self.attack_particles.remove(particle)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            if not self.is_dead:  # 첫 번째 죽음에만 처리
                self.is_dead = True
                self.hp = 0
                # 죽을 때 더 공격적으로 변함 (주변 적군에게 영향)
                self.aggression_level = min(2.0, self.aggression_level + 0.3)

    def draw(self, screen, camera):
        # 화면에 보이는지 체크
        if not camera.is_visible(self.x, self.y, self.size):
            return

        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        if self.is_dead:
            self._draw_death_effect(screen, screen_x, screen_y)
            return

        # 공격 파티클 그리기
        self._draw_attack_particles(screen, camera)

        # 트레일 그리기
        for i, (trail_x, trail_y) in enumerate(self.trail):
            if camera.is_visible(trail_x, trail_y):
                trail_screen_x, trail_screen_y = camera.world_to_screen(trail_x, trail_y)
                alpha = int(255 * (i / len(self.trail)) * 0.4)
                trail_color = RED  # 빨간색으로 통일

                trail_surface = pygame.Surface((self.size, self.size))
                trail_surface.set_alpha(alpha)
                trail_surface.fill(trail_color)
                screen.blit(trail_surface, (trail_screen_x - self.size // 2,
                                            trail_screen_y - self.size // 2))

        # 그림자
        shadow_offset = 3
        pygame.draw.rect(screen, (50, 50, 50),
                         (screen_x - self.size // 2 + shadow_offset,
                          screen_y - self.size // 2 + shadow_offset,
                          self.size, self.size))

        # 상태별 글로우 효과
        if self.state == "attack":
            glow_surface = pygame.Surface((self.size + 15, self.size + 15))
            glow_surface.set_alpha(120)
            glow_surface.fill(RED)
            screen.blit(glow_surface, (screen_x - self.size // 2 - 7,
                                       screen_y - self.size // 2 - 7))
        elif self.state == "smart_move":
            glow_surface = pygame.Surface((self.size + 10, self.size + 10))
            glow_surface.set_alpha(80)
            glow_surface.fill(ORANGE)
            screen.blit(glow_surface, (screen_x - self.size // 2 - 5,
                                       screen_y - self.size // 2 - 5))

        # 메인 적군 - 항상 빨간 네모
        pygame.draw.rect(screen, RED,
                         (screen_x - self.size // 2,
                          screen_y - self.size // 2,
                          self.size, self.size))

        # 공격성 레벨에 따른 테두리
        border_thickness = int(self.aggression_level * 2)
        if border_thickness > 1:
            pygame.draw.rect(screen, DARK_RED,
                             (screen_x - self.size // 2,
                              screen_y - self.size // 2,
                              self.size, self.size), border_thickness)

        # HP 바 그리기
        self._draw_hp_bar(screen, screen_x, screen_y)

    def _draw_attack_particles(self, screen, camera):
        """공격 파티클 그리기"""
        for particle in self.attack_particles:
            if camera.is_visible(particle['x'], particle['y']):
                screen_x, screen_y = camera.world_to_screen(particle['x'], particle['y'])
                alpha = int(255 * (particle['life'] / particle['max_life']))
                if alpha > 0:
                    particle_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)))
                    particle_surface.set_alpha(alpha)
                    particle_surface.fill(RED)
                    screen.blit(particle_surface, (screen_x - particle['size'],
                                                   screen_y - particle['size']))

    def _draw_hp_bar(self, screen, screen_x, screen_y):
        if self.hp < self.max_hp:  # HP가 풀이 아닐 때만 표시
            bar_width = self.size
            bar_height = 4
            bar_x = screen_x - bar_width // 2
            bar_y = screen_y - self.size // 2 - 8

            # 배경 (빨간색)
            pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))

            # HP 바 (초록색)
            hp_ratio = self.hp / self.max_hp
            pygame.draw.rect(screen, GREEN,
                             (bar_x, bar_y, bar_width * hp_ratio, bar_height))

    def _draw_death_effect(self, screen, screen_x, screen_y):
        # 죽음 애니메이션
        alpha = max(0, 255 - self.death_animation * 8)
        size_multiplier = 1 + (self.death_animation * 0.1)

        if alpha > 0:
            death_surface = pygame.Surface((int(self.size * size_multiplier),
                                            int(self.size * size_multiplier)))
            death_surface.set_alpha(alpha)
            death_surface.fill(DARK_RED)

            screen.blit(death_surface,
                        (screen_x - (self.size * size_multiplier) // 2,
                         screen_y - (self.size * size_multiplier) // 2))


class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.spawn_timer = 0
        self.max_enemies = 8  # 더 많은 적군

    def update(self, player_pos, camera, obstacle_manager, level_system):
        # 적군 스폰 (레벨에 따른 조정)
        self.spawn_timer += 1
        alive_enemies = [e for e in self.enemies if not e.is_dead]

        spawn_rate = level_system.get_enemy_spawn_rate()
        max_enemies = level_system.get_enemy_spawn_count()

        if (self.spawn_timer >= spawn_rate and
                len(alive_enemies) < max_enemies):
            self._spawn_enemy_outside_view(camera, obstacle_manager, level_system.level)
            self.spawn_timer = 0

        # 적군 업데이트
        for enemy in self.enemies[:]:
            enemy.update(player_pos, alive_enemies, camera, obstacle_manager)

            # 죽은 적군 제거 (애니메이션 완료 후)
            if enemy.is_dead and enemy.death_animation > 40:
                self.enemies.remove(enemy)

    def _spawn_enemy_outside_view(self, camera, obstacle_manager, current_level):
        """화면 밖에서 적군 스폰 (레벨에 따른 강화)"""
        visible_area = camera.get_visible_area()
        margin = 100

        attempts = 0
        while attempts < 20:  # 최대 20번 시도
            # 4개 방향 중 랜덤 선택
            side = random.randint(0, 3)
            if side == 0:  # 위쪽
                x = random.randint(int(max(0, visible_area['left'] - margin)),
                                   int(min(WORLD_WIDTH, visible_area['right'] + margin)))
                y = int(max(0, visible_area['top'] - margin))
            elif side == 1:  # 아래쪽
                x = random.randint(int(max(0, visible_area['left'] - margin)),
                                   int(min(WORLD_WIDTH, visible_area['right'] + margin)))
                y = int(min(WORLD_HEIGHT, visible_area['bottom'] + margin))
            elif side == 2:  # 왼쪽
                x = int(max(0, visible_area['left'] - margin))
                y = random.randint(int(max(0, visible_area['top'] - margin)),
                                   int(min(WORLD_HEIGHT, visible_area['bottom'] + margin)))
            else:  # 오른쪽
                x = int(min(WORLD_WIDTH, visible_area['right'] + margin))
                y = random.randint(int(max(0, visible_area['top'] - margin)),
                                   int(min(WORLD_HEIGHT, visible_area['bottom'] + margin)))

            # 월드 경계 체크
            x = clamp(x, ENEMY_SIZE, WORLD_WIDTH - ENEMY_SIZE)
            y = clamp(y, ENEMY_SIZE, WORLD_HEIGHT - ENEMY_SIZE)

            # 장애물과 겹치지 않는지 체크
            if not obstacle_manager.check_collision_circle(x, y, ENEMY_SIZE // 2):
                enemy = Enemy(x, y)
                # 레벨에 따른 적군 강화
                enemy._apply_level_scaling(current_level)
                self.enemies.append(enemy)
                break

            attempts += 1

    def draw(self, screen, camera):
        for enemy in self.enemies:
            enemy.draw(screen, camera)

    def get_enemies(self):
        return [e for e in self.enemies if not e.is_dead]