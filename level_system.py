# level_system.py - 레벨 시스템

import pygame
from config import *


class LevelSystem:
    def __init__(self):
        self.level = 1
        self.kills = 0
        self.total_kills = 0
        self.kills_for_next_level = LEVEL_UP_KILLS
        self.level_up_animation = 0
        self.just_leveled_up = False

    def add_kill(self):
        """킬 수 추가"""
        self.kills += 1
        self.total_kills += 1

        # 레벨업 체크
        if self.kills >= self.kills_for_next_level:
            self._level_up()

    def _level_up(self):
        """레벨업 처리"""
        self.level += 1
        self.kills = 0
        self.kills_for_next_level = LEVEL_UP_KILLS + (self.level - 1) * 2  # 점점 더 많은 킬 필요
        self.level_up_animation = 180  # 3초간 애니메이션
        self.just_leveled_up = True

    def update(self):
        """레벨 시스템 업데이트"""
        if self.level_up_animation > 0:
            self.level_up_animation -= 1
        if self.just_leveled_up and self.level_up_animation <= 0:
            self.just_leveled_up = False

    def get_enemy_spawn_count(self):
        """현재 레벨에 따른 적군 스폰 수"""
        return ENEMY_SPAWN_BASE + (self.level - 1) * ENEMY_SPAWN_INCREASE

    def get_enemy_spawn_rate(self):
        """현재 레벨에 따른 적군 스폰 속도"""
        # 레벨이 높을수록 더 자주 스폰 (최소 60프레임)
        base_rate = ENEMY_SPAWN_RATE
        reduced_rate = max(60, base_rate - (self.level - 1) * 20)
        return reduced_rate

    def get_progress_ratio(self):
        """현재 레벨 진행률 (0.0 ~ 1.0)"""
        return self.kills / self.kills_for_next_level

    def draw_level_up_effect(self, screen):
        """레벨업 애니메이션"""
        if self.level_up_animation <= 0:
            return

        # 레벨업 텍스트
        alpha = min(255, self.level_up_animation * 3)
        scale = 1.0 + (180 - self.level_up_animation) * 0.01

        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(alpha // 4)
        overlay.fill((255, 215, 0))  # 골드 색상
        screen.blit(overlay, (0, 0))

        # 레벨업 텍스트
        font = pygame.font.Font(None, int(72 * scale))
        level_text = font.render(f"LEVEL {self.level}!", True, GOLD)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

        # 텍스트에 알파 적용
        level_surface = pygame.Surface(level_text.get_size())
        level_surface.set_alpha(alpha)
        level_surface.blit(level_text, (0, 0))
        screen.blit(level_surface, level_rect)

        # 추가 정보
        font2 = pygame.font.Font(None, int(36 * scale))
        info_text = font2.render(f"Enemies become stronger!", True, WHITE)
        info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

        info_surface = pygame.Surface(info_text.get_size())
        info_surface.set_alpha(alpha)
        info_surface.blit(info_text, (0, 0))
        screen.blit(info_surface, info_rect)