# weapon.py - 무기 시스템

import pygame
import math
import random
from config import *
from utils import *


class WeaponManager:
    def __init__(self):
        self.current_weapon = 'PISTOL'
        self.weapons = WEAPON_TYPES.copy()
        self.cooldowns = {weapon: 0 for weapon in self.weapons}

    def update(self):
        """쿨다운 업데이트"""
        for weapon in self.cooldowns:
            if self.cooldowns[weapon] > 0:
                self.cooldowns[weapon] -= 1

    def switch_weapon(self, weapon_key):
        """무기 변경"""
        if weapon_key in self.weapons:
            self.current_weapon = weapon_key

    def can_shoot(self):
        """현재 무기로 발사 가능한지 체크"""
        return self.cooldowns[self.current_weapon] <= 0

    def shoot(self, start_x, start_y, target_x, target_y, bullet_manager):
        """무기 발사"""
        if not self.can_shoot():
            return False

        weapon = self.weapons[self.current_weapon]

        # 쿨다운 적용
        self.cooldowns[self.current_weapon] = weapon['cooldown']

        # 기본 방향 계산
        dx = target_x - start_x
        dy = target_y - start_y
        base_angle = math.atan2(dy, dx)

        # 무기별 총알 생성
        for i in range(weapon['bullets']):
            # 퍼짐 계산 (샷건용)
            if weapon['bullets'] > 1:
                spread_offset = (i - (weapon['bullets'] - 1) / 2) * weapon['spread']
                bullet_angle = base_angle + spread_offset
            else:
                bullet_angle = base_angle

            # 총알 속도 계산
            bullet_vx = math.cos(bullet_angle) * weapon['speed']
            bullet_vy = math.sin(bullet_angle) * weapon['speed']

            # 총알 생성
            bullet_manager.add_bullet(
                start_x, start_y,
                bullet_vx, bullet_vy,
                weapon['damage'],
                weapon['color'],
                self.current_weapon
            )

        return True

    def get_current_weapon_info(self):
        """현재 무기 정보 반환"""
        weapon = self.weapons[self.current_weapon]
        cooldown = self.cooldowns[self.current_weapon]
        return {
            'name': weapon['name'],
            'damage': weapon['damage'],
            'cooldown': cooldown,
            'max_cooldown': weapon['cooldown'],
            'color': weapon['color'],
            'ready': cooldown <= 0
        }

    def handle_input(self, keys):
        """키 입력 처리"""
        if keys[pygame.K_1]:
            self.switch_weapon('PISTOL')
        elif keys[pygame.K_2]:
            self.switch_weapon('SHOTGUN')
        elif keys[pygame.K_3]:
            self.switch_weapon('SNIPER')