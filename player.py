# player.py - 플레이어 클래스 (완전 업그레이드 v2)

import pygame
import math
import random
from config import *
from utils import *
from weapon import WeaponManager


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.trail = []

        # 체력 시스템
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.invincible_time = 0  # 무적 시간 (피격 후)
        self.last_damage_time = 0

        # 점멸 관련 (즉시 실행)
        self.blink_cooldown = 0
        self.blink_max_cooldown = BLINK_COOLDOWN
        self.blink_particles = []
        self.afterimage_effects = []

        # 대시 관련
        self.dash_cooldown = 0
        self.dash_max_cooldown = DASH_COOLDOWN
        self.dash_duration = 0

        # 폭발 관련
        self.explosion_cooldown = 0
        self.explosion_max_cooldown = EXPLOSION_COOLDOWN
        self.explosion_effects = []

        # 무기 시스템
        self.weapon_manager = WeaponManager()

        # 마우스 입력 상태
        self.mouse_pressed = {'left': False, 'right': False}
        self.mouse_just_pressed = {'left': False, 'right': False}  # 추가
        self.keys_pressed = {}

        # 애니메이션 효과
        self.power_aura = 0
        self.combat_particles = []
        self.hit_flash = 0  # 피격 시 깜빡임

    def update(self, keys, mouse_buttons, mouse_pos, bullet_manager, enemies, camera, obstacle_manager):
        # 쿨다운 업데이트
        if self.blink_cooldown > 0:
            self.blink_cooldown -= 1
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
        if self.explosion_cooldown > 0:
            self.explosion_cooldown -= 1
        if self.invincible_time > 0:
            self.invincible_time -= 1
        if self.hit_flash > 0:
            self.hit_flash -= 1

        # 무적 시간 감소
        self.weapon_manager.update()

        # 대시 업데이트
        if self.dash_duration > 0:
            self.dash_duration -= 1

        # 스킬 및 공격 처리
        world_mouse_pos = camera.screen_to_world(mouse_pos[0], mouse_pos[1])
        self._handle_skills(keys, mouse_buttons, world_mouse_pos, bullet_manager, enemies, camera, obstacle_manager)

        # 기본 이동
        self._handle_movement(keys, obstacle_manager)

        # 월드 경계 체크
        self._check_boundaries()

        # 트레일 및 효과 업데이트
        self._update_effects()

        # 적군과의 충돌 체크 (데미지)
        self._check_enemy_collision(enemies)

    def _handle_skills(self, keys, mouse_buttons, world_mouse_pos, bullet_manager, enemies, camera, obstacle_manager):
        # 무기 변경 (1, 2, 3키)
        self.weapon_manager.handle_input(keys)

        # 마우스 입력 상태 업데이트
        self.mouse_just_pressed['left'] = mouse_buttons[0] and not self.mouse_pressed['left']
        self.mouse_just_pressed['right'] = mouse_buttons[2] and not self.mouse_pressed['right']

        # 총 발사 (마우스 좌클릭)
        if self.mouse_just_pressed['left']:
            if world_mouse_pos[1] < WORLD_HEIGHT - UI_HEIGHT:  # UI 영역 제외
                if self.weapon_manager.shoot(self.x, self.y, world_mouse_pos[0], world_mouse_pos[1], bullet_manager):
                    self._create_shoot_effect()
                    camera.add_shake(3)

        # 즉시 점멸 (마우스 우클릭)
        if self.mouse_just_pressed['right']:
            if self.blink_cooldown == 0:
                if world_mouse_pos[1] < WORLD_HEIGHT - UI_HEIGHT:  # UI 영역 제외
                    # 거리 제한 체크
                    target_dist = distance((self.x, self.y), world_mouse_pos)
                    if target_dist <= BLINK_RANGE:
                        # 장애물 체크 (점멸 목표지점)
                        if not obstacle_manager.check_collision_circle(world_mouse_pos[0], world_mouse_pos[1],
                                                                       self.size // 2):
                            self._execute_instant_blink(world_mouse_pos, camera)

        # 대시 (F키)
        if keys[pygame.K_f] and not self.keys_pressed.get(pygame.K_f, False):
            if self.dash_cooldown == 0 and self.dash_duration == 0:
                self.dash_duration = DASH_DURATION
                self.dash_cooldown = DASH_COOLDOWN
                self._create_dash_effect()

        # 폭발 (Q키)
        if keys[pygame.K_q] and not self.keys_pressed.get(pygame.K_q, False):
            if self.explosion_cooldown == 0:
                self._create_explosion(enemies, camera)
                self.explosion_cooldown = EXPLOSION_COOLDOWN

        # 입력 상태 업데이트
        current_keys = {}
        for key in [pygame.K_f, pygame.K_q]:
            current_keys[key] = keys[key]
        self.keys_pressed = current_keys

        self.mouse_pressed = {'left': mouse_buttons[0], 'right': mouse_buttons[2]}

    def _execute_instant_blink(self, target_pos, camera):
        """즉시 점멸 실행"""
        # 잔상 효과 생성
        for i in range(8):
            self.afterimage_effects.append({
                'x': self.x,
                'y': self.y,
                'alpha': 255 - (i * 25),
                'life': 25 - (i * 3),
                'size': self.size + (i * 2)
            })

        # 출발지 파티클 폭발
        self._create_blink_exit_effect()

        # 순간이동 실행
        self.x, self.y = target_pos

        # 도착지 파티클 폭발
        self._create_blink_arrival_effect()

        # 쿨다운 적용
        self.blink_cooldown = self.blink_max_cooldown

        # 화면 흔들림
        camera.add_shake(10)

    def _create_blink_exit_effect(self):
        """점멸 출발 효과"""
        for _ in range(PARTICLE_COUNT_HIGH):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)
            self.blink_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 40,
                'max_life': 40,
                'size': random.uniform(3, 6),
                'color': PURPLE
            })

    def _create_blink_arrival_effect(self):
        """점멸 도착 효과"""
        for _ in range(PARTICLE_COUNT_HIGH):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.blink_particles.append({
                'x': self.x + random.uniform(-20, 20),
                'y': self.y + random.uniform(-20, 20),
                'vx': math.cos(angle) * speed * 0.5,
                'vy': math.sin(angle) * speed * 0.5,
                'life': 35,
                'max_life': 35,
                'size': random.uniform(2, 5),
                'color': CYAN
            })

    def _create_shoot_effect(self):
        """총 발사 효과"""
        # 총구 화염 효과
        weapon_info = self.weapon_manager.get_current_weapon_info()

        # 무기별 다른 효과
        particle_count = 15 if weapon_info['name'] == 'Shotgun' else 8
        if weapon_info['name'] == 'Sniper':
            particle_count = 20

        for _ in range(particle_count):
            angle = random.uniform(-0.8, 0.8)
            speed = random.uniform(2, 6)
            self.combat_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 15,
                'max_life': 15,
                'size': random.uniform(2, 5),
                'color': weapon_info['color']
            })

    def _create_dash_effect(self):
        """대시 효과"""
        self.power_aura = 60

    def _handle_movement(self, keys, obstacle_manager):
        current_speed = self.speed
        if self.dash_duration > 0:
            current_speed *= PLAYER_DASH_MULTIPLIER

        # 이동 전 위치 저장
        old_x, old_y = self.x, self.y

        # WASD 이동
        new_x, new_y = old_x, old_y

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            new_y -= current_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            new_y += current_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            new_x -= current_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            new_x += current_speed

        # 장애물 충돌 체크
        if not obstacle_manager.check_collision_circle(new_x, new_y, self.size // 2):
            self.x, self.y = new_x, new_y
        else:
            # X축만 이동 시도
            if not obstacle_manager.check_collision_circle(new_x, old_y, self.size // 2):
                self.x = new_x
            # Y축만 이동 시도
            elif not obstacle_manager.check_collision_circle(old_x, new_y, self.size // 2):
                self.y = new_y

    def _check_boundaries(self):
        self.x = clamp(self.x, self.size // 2, WORLD_WIDTH - self.size // 2)
        self.y = clamp(self.y, self.size // 2, WORLD_HEIGHT - self.size // 2)

    def _check_enemy_collision(self, enemies):
        """적군과의 충돌 및 데미지 체크"""
        if self.invincible_time > 0:
            return

        for enemy in enemies:
            if not enemy.is_dead:
                enemy_dist = distance((self.x, self.y), (enemy.x, enemy.y))
                if enemy_dist <= (self.size // 2 + enemy.size // 2):
                    # 데미지 받음
                    self.take_damage(ENEMY_ATTACK_DAMAGE)
                    break

    def take_damage(self, damage):
        """플레이어 데미지 받기"""
        if self.invincible_time > 0:
            return

        self.hp -= damage
        self.hp = max(0, self.hp)
        self.invincible_time = 60  # 1초 무적
        self.hit_flash = 20

        # 피격 효과
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.combat_particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 20,
                'max_life': 20,
                'size': random.uniform(2, 4),
                'color': RED
            })

    def is_dead(self):
        return self.hp <= 0

    def _update_effects(self):
        """모든 효과 업데이트"""
        # 트레일 업데이트
        self.trail.append((self.x, self.y))
        trail_length = 25 if self.dash_duration > 0 else 15
        if len(self.trail) > trail_length:
            self.trail.pop(0)

        # 점멸 파티클 업데이트
        for particle in self.blink_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vx'] *= 0.96
            particle['vy'] *= 0.96

            if particle['life'] <= 0:
                self.blink_particles.remove(particle)

        # 잔상 효과 업데이트
        for afterimage in self.afterimage_effects[:]:
            afterimage['life'] -= 1
            afterimage['alpha'] -= 15
            if afterimage['life'] <= 0 or afterimage['alpha'] <= 0:
                self.afterimage_effects.remove(afterimage)

        # 전투 파티클 업데이트
        for particle in self.combat_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vx'] *= 0.98
            particle['vy'] *= 0.98
            if particle['life'] <= 0:
                self.combat_particles.remove(particle)

        # 폭발 효과 업데이트
        self._update_explosions()

        # 파워 오라 감소
        if self.power_aura > 0:
            self.power_aura -= 2

    def _create_explosion(self, enemies, camera):
        explosion = {
            'x': self.x,
            'y': self.y,
            'radius': 0,
            'max_radius': EXPLOSION_RADIUS,
            'duration': EXPLOSION_DURATION,
            'particles': create_explosion_particles((self.x, self.y), PARTICLE_COUNT_HIGH)
        }
        self.explosion_effects.append(explosion)

        # 적군에게 데미지
        for enemy in enemies:
            dist = distance((self.x, self.y), (enemy.x, enemy.y))
            if dist <= EXPLOSION_RADIUS:
                enemy.take_damage(EXPLOSION_DAMAGE)

        # 화면 흔들림
        camera.add_shake(15)

    def _update_explosions(self):
        for explosion in self.explosion_effects[:]:
            explosion['duration'] -= 1
            explosion['radius'] = (explosion['max_radius'] *
                                   (1 - explosion['duration'] / EXPLOSION_DURATION))

            # 파티클 업데이트
            for particle in explosion['particles'][:]:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= 1
                particle['vx'] *= 0.95
                particle['vy'] *= 0.95

                if particle['life'] <= 0:
                    explosion['particles'].remove(particle)

            if explosion['duration'] <= 0:
                self.explosion_effects.remove(explosion)

    def draw(self, screen, camera):
        # 화면에 보이는지 체크
        if not camera.is_visible(self.x, self.y, self.size):
            return

        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # 점멸 관련 효과 그리기
        self._draw_blink_effects(screen, camera)

        # 폭발 효과 그리기
        self._draw_explosions(screen, camera)

        # 전투 파티클 그리기
        self._draw_combat_particles(screen, camera)

        # 잔상 효과 그리기
        self._draw_afterimages(screen, camera)

        # 트레일 그리기
        self._draw_trail(screen, camera)

        # 플레이어 그리기
        self._draw_player(screen, camera)

        # 점멸 범위 표시
        self._draw_blink_range(screen, camera)

    def _draw_blink_effects(self, screen, camera):
        # 점멸 파티클
        for particle in self.blink_particles:
            if camera.is_visible(particle['x'], particle['y']):
                screen_x, screen_y = camera.world_to_screen(particle['x'], particle['y'])
                alpha = int(255 * (particle['life'] / particle['max_life']))
                if alpha > 0:
                    particle_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)))
                    particle_surface.set_alpha(alpha)
                    particle_surface.fill(particle['color'])
                    screen.blit(particle_surface, (screen_x - particle['size'], screen_y - particle['size']))

    def _draw_afterimages(self, screen, camera):
        for afterimage in self.afterimage_effects:
            if camera.is_visible(afterimage['x'], afterimage['y']):
                screen_x, screen_y = camera.world_to_screen(afterimage['x'], afterimage['y'])
                if afterimage['alpha'] > 0:
                    afterimage_surface = pygame.Surface((afterimage['size'], afterimage['size']))
                    afterimage_surface.set_alpha(afterimage['alpha'])
                    afterimage_surface.fill(PURPLE)
                    screen.blit(afterimage_surface,
                                (screen_x - afterimage['size'] // 2, screen_y - afterimage['size'] // 2))

    def _draw_combat_particles(self, screen, camera):
        for particle in self.combat_particles:
            if camera.is_visible(particle['x'], particle['y']):
                screen_x, screen_y = camera.world_to_screen(particle['x'], particle['y'])
                alpha = int(255 * (particle['life'] / particle['max_life']))
                if alpha > 0:
                    particle_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)))
                    particle_surface.set_alpha(alpha)
                    particle_surface.fill(particle['color'])
                    screen.blit(particle_surface, (screen_x - particle['size'], screen_y - particle['size']))

    def _draw_explosions(self, screen, camera):
        for explosion in self.explosion_effects:
            if camera.is_visible(explosion['x'], explosion['y'], explosion['radius']):
                screen_x, screen_y = camera.world_to_screen(explosion['x'], explosion['y'])

                # 폭발 원 그리기
                if explosion['radius'] > 0:
                    alpha = int(255 * (explosion['duration'] / EXPLOSION_DURATION))
                    draw_circle_outline(screen, ORANGE, (int(screen_x), int(screen_y)),
                                        int(explosion['radius']), 5, alpha)

                # 폭발 파티클 그리기
                for particle in explosion['particles']:
                    if camera.is_visible(particle['x'], particle['y']):
                        p_screen_x, p_screen_y = camera.world_to_screen(particle['x'], particle['y'])
                        alpha = int(255 * (particle['life'] / particle['max_life']))
                        if alpha > 0:
                            particle_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)))
                            particle_surface.set_alpha(alpha)
                            particle_surface.fill(ORANGE)
                            screen.blit(particle_surface, (p_screen_x - particle['size'],
                                                           p_screen_y - particle['size']))

    def _draw_trail(self, screen, camera):
        for i, (trail_x, trail_y) in enumerate(self.trail):
            if camera.is_visible(trail_x, trail_y):
                screen_x, screen_y = camera.world_to_screen(trail_x, trail_y)
                alpha = int(255 * (i / len(self.trail)) * 0.5)
                trail_color = RED if self.dash_duration > 0 else CYAN

                trail_surface = pygame.Surface((self.size, self.size))
                trail_surface.set_alpha(alpha)
                trail_surface.fill(trail_color)
                screen.blit(trail_surface, (screen_x - self.size // 2, screen_y - self.size // 2))

    def _draw_player(self, screen, camera):
        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # 피격 시 깜빡임 효과
        if self.hit_flash > 0 and self.hit_flash % 6 < 3:
            return  # 깜빡임으로 그리지 않음

        # 파워 오라 (대시 중)
        if self.power_aura > 0:
            aura_alpha = int(self.power_aura * 2)
            aura_surface = pygame.Surface((self.size + 30, self.size + 30))
            aura_surface.set_alpha(aura_alpha)
            aura_surface.fill(RED)
            screen.blit(aura_surface, (screen_x - self.size // 2 - 15, screen_y - self.size // 2 - 15))

        # 무적 상태 글로우
        if self.invincible_time > 0:
            invincible_surface = pygame.Surface((self.size + 15, self.size + 15))
            invincible_surface.set_alpha(100)
            invincible_surface.fill(BLUE)
            screen.blit(invincible_surface, (screen_x - self.size // 2 - 7, screen_y - self.size // 2 - 7))

        # 그림자
        shadow_offset = 4
        pygame.draw.rect(screen, DARK_BLUE,
                         (screen_x - self.size // 2 + shadow_offset,
                          screen_y - self.size // 2 + shadow_offset,
                          self.size, self.size))

        # 대시 글로우 효과
        if self.dash_duration > 0:
            glow_surface = pygame.Surface((self.size + 20, self.size + 20))
            glow_surface.set_alpha(150)
            glow_surface.fill(RED)
            screen.blit(glow_surface, (screen_x - self.size // 2 - 10, screen_y - self.size // 2 - 10))

        # 메인 플레이어
        player_color = RED if self.dash_duration > 0 else BLUE
        pygame.draw.rect(screen, player_color,
                         (screen_x - self.size // 2, screen_y - self.size // 2, self.size, self.size))

        # 하이라이트
        highlight_color = GOLD if self.dash_duration > 0 else CYAN
        pygame.draw.rect(screen, highlight_color,
                         (screen_x - self.size // 2 + 3, screen_y - self.size // 2 + 3,
                          self.size - 6, self.size - 6), 3)

    def _draw_blink_range(self, screen, camera):
        """점멸 범위 표시 (우클릭 중일 때만)"""
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[2] and self.blink_cooldown == 0:  # 우클릭 중
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
            mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = camera.screen_to_world(mouse_pos[0], mouse_pos[1])
            target_dist = distance((self.x, self.y), world_mouse_pos)

            # 범위 원 그리기
            range_alpha = 80
            if target_dist <= BLINK_RANGE:
                range_color = GREEN
            else:
                range_color = RED

            draw_circle_outline(screen, range_color, (int(screen_x), int(screen_y)),
                                BLINK_RANGE, 2, range_alpha)

            # 마우스까지의 선 그리기
            if world_mouse_pos[1] < WORLD_HEIGHT - UI_HEIGHT:
                line_alpha = 60 if target_dist <= BLINK_RANGE else 30
                line_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                line_surface.set_alpha(line_alpha)
                line_color = GREEN if target_dist <= BLINK_RANGE else RED
                pygame.draw.line(line_surface, line_color, (screen_x, screen_y), mouse_pos, 2)
                screen.blit(line_surface, (0, 0))

    def get_position(self):
        return (self.x, self.y)

    def get_hp_ratio(self):
        return self.hp / self.max_hp if self.max_hp > 0 else 0