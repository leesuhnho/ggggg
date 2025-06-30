# ui.py - UI 시스템 (수정된 버전)

import pygame
import math
from config import *


class UI:
    def __init__(self):
        # 폰트 설정
        self.title_font = pygame.font.Font(None, 48)
        self.skill_font = pygame.font.Font(None, 28)
        self.cooldown_font = pygame.font.Font(None, 22)
        self.info_font = pygame.font.Font(None, 24)
        self.weapon_font = pygame.font.Font(None, 36)

    def draw_player_hud(self, screen, player):
        """플레이어 HUD (체력바, 무기 정보 등)"""
        # 체력바 (좌상단)
        self._draw_health_bar(screen, player)

        # 현재 무기 (우상단)
        self._draw_weapon_info(screen, player)

    def _draw_health_bar(self, screen, player):
        """체력바 그리기"""
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 20

        # 배경
        bg_surface = pygame.Surface((bar_width + 10, bar_height + 30))
        bg_surface.set_alpha(200)
        bg_surface.fill((20, 20, 40))
        screen.blit(bg_surface, (bar_x - 5, bar_y - 5))

        # HP 텍스트
        hp_text = self.info_font.render(f"HP: {int(player.hp)}/{int(player.max_hp)}", True, WHITE)
        screen.blit(hp_text, (bar_x, bar_y - 25))

        # HP 바 배경 (빨간색)
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))

        # HP 바 (초록색 -> 노란색 -> 빨간색)
        hp_ratio = player.get_hp_ratio()
        current_width = int(bar_width * hp_ratio)

        if hp_ratio > 0.6:
            hp_color = GREEN
        elif hp_ratio > 0.3:
            hp_color = YELLOW
        else:
            hp_color = RED

        if current_width > 0:
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, current_width, bar_height))

        # 테두리
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

        # 무적 상태 표시
        if player.invincible_time > 0:
            invincible_text = self.cooldown_font.render("INVINCIBLE", True, CYAN)
            screen.blit(invincible_text, (bar_x, bar_y + bar_height + 5))

    def _draw_weapon_info(self, screen, player):
        """현재 무기 정보"""
        weapon_info = player.weapon_manager.get_current_weapon_info()

        # 배경 - FPS와 겹치지 않게 위치 조정
        info_width = 200
        info_height = 80
        info_x = SCREEN_WIDTH - info_width - 20
        info_y = 20  # 기존과 동일

        bg_surface = pygame.Surface((info_width, info_height))
        bg_surface.set_alpha(200)
        bg_surface.fill((20, 20, 40))
        screen.blit(bg_surface, (info_x, info_y))

        # 테두리 (무기 색상)
        border_color = weapon_info['color'] if weapon_info['ready'] else GRAY
        pygame.draw.rect(screen, border_color, (info_x, info_y, info_width, info_height), 3)

        # 무기 이름
        weapon_text = self.weapon_font.render(weapon_info['name'], True, weapon_info['color'])
        screen.blit(weapon_text, (info_x + 10, info_y + 10))

        # 데미지 정보
        damage_text = self.cooldown_font.render(f"DMG: {weapon_info['damage']}", True, WHITE)
        screen.blit(damage_text, (info_x + 10, info_y + 45))

        # 쿨다운 상태
        if weapon_info['cooldown'] > 0:
            cooldown_sec = (weapon_info['cooldown'] // 60) + 1
            status_text = self.cooldown_font.render(f"Reload: {cooldown_sec}s", True, RED)
        else:
            status_text = self.cooldown_font.render("READY", True, GREEN)
        screen.blit(status_text, (info_x + 100, info_y + 45))

        # 무기 변경 힌트
        hint_text = self.cooldown_font.render("1,2,3 to switch", True, GRAY)
        screen.blit(hint_text, (info_x + 10, info_y + 65))

    def draw_level_progress(self, screen, level_system):
        """레벨 진행률 바 (상단 중앙)"""
        bar_width = 300
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 20

        # 배경
        bg_surface = pygame.Surface((bar_width + 20, bar_height + 40))
        bg_surface.set_alpha(200)
        bg_surface.fill((20, 20, 40))
        screen.blit(bg_surface, (bar_x - 10, bar_y - 10))

        # 레벨 텍스트
        level_text = self.info_font.render(f"LEVEL {level_system.level}", True, GOLD)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y - 25))
        screen.blit(level_text, level_rect)

        # 진행률 바 배경
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))

        # 진행률 바
        progress = level_system.get_progress_ratio()
        progress_width = int(bar_width * progress)

        if progress_width > 0:
            pygame.draw.rect(screen, GOLD, (bar_x, bar_y, progress_width, bar_height))

        # 테두리
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)

        # 킬 수 텍스트
        kill_text = self.cooldown_font.render(
            f"{level_system.kills}/{level_system.kills_for_next_level} kills",
            True, WHITE)
        kill_rect = kill_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height + 15))
        screen.blit(kill_text, kill_rect)

    def draw_minimap(self, screen, player_pos, enemies, camera):
        """미니맵 (우하단) - 위치 수정"""
        minimap_x = SCREEN_WIDTH - MINIMAP_SIZE - 20
        # FPS 표시와 겹치지 않게 위치 조정
        minimap_y = SCREEN_HEIGHT - MINIMAP_SIZE - 60  # 기존 -20에서 -60으로 변경

        # 배경
        minimap_surface = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
        minimap_surface.set_alpha(200)
        minimap_surface.fill((10, 10, 20))

        # 월드 경계
        pygame.draw.rect(minimap_surface, WHITE,
                         (0, 0, MINIMAP_SIZE, MINIMAP_SIZE), 2)

        # 플레이어 위치
        player_minimap_x = int((player_pos[0] / WORLD_WIDTH) * MINIMAP_SIZE)
        player_minimap_y = int((player_pos[1] / WORLD_HEIGHT) * MINIMAP_SIZE)
        pygame.draw.circle(minimap_surface, BLUE,
                           (player_minimap_x, player_minimap_y), 3)

        # 적군 위치 - 빨간 네모로 표시
        for enemy in enemies:
            if not enemy.is_dead:
                enemy_minimap_x = int((enemy.x / WORLD_WIDTH) * MINIMAP_SIZE)
                enemy_minimap_y = int((enemy.y / WORLD_HEIGHT) * MINIMAP_SIZE)

                # 빨간 네모로 표시 (크기 4x4)
                enemy_rect = pygame.Rect(enemy_minimap_x - 2, enemy_minimap_y - 2, 4, 4)
                pygame.draw.rect(minimap_surface, RED, enemy_rect)

        # 카메라 시야 영역
        visible_area = camera.get_visible_area()
        view_x = int((visible_area['left'] / WORLD_WIDTH) * MINIMAP_SIZE)
        view_y = int((visible_area['top'] / WORLD_HEIGHT) * MINIMAP_SIZE)
        view_w = int((SCREEN_WIDTH / WORLD_WIDTH) * MINIMAP_SIZE)
        view_h = int((SCREEN_HEIGHT / WORLD_HEIGHT) * MINIMAP_SIZE)

        pygame.draw.rect(minimap_surface, CYAN, (view_x, view_y, view_w, view_h), 1)

        screen.blit(minimap_surface, (minimap_x, minimap_y))

        # 미니맵 라벨
        minimap_label = self.cooldown_font.render("MAP", True, WHITE)
        screen.blit(minimap_label, (minimap_x, minimap_y - 25))

    def draw_skill_bar(self, screen, player):
        """스킬바 (하단)"""
        # UI 배경
        ui_y = SCREEN_HEIGHT - UI_HEIGHT
        ui_surface = pygame.Surface((SCREEN_WIDTH, UI_HEIGHT))
        ui_surface.set_alpha(220)

        # 그라디언트 배경
        for y in range(UI_HEIGHT):
            alpha = int(80 - (y * 0.5))
            color = (15, 15, 35)
            pygame.draw.line(ui_surface, color, (0, y), (SCREEN_WIDTH, y))

        screen.blit(ui_surface, (0, ui_y))

        # 테두리
        pygame.draw.line(screen, CYAN, (0, ui_y), (SCREEN_WIDTH, ui_y), 2)

        # 제목
        title_text = self.title_font.render("COMBAT SKILLS", True, GOLD)
        screen.blit(title_text, (20, ui_y + 10))

        # 스킬 박스들
        skill_boxes = [
            {
                "key": "R-CLICK",
                "name": "BLINK",
                "description": "Instant teleport",
                "cooldown": player.blink_cooldown,
                "max_cooldown": player.blink_max_cooldown,
                "color": PURPLE,
                "x": 50
            },
            {
                "key": "F",
                "name": "DASH",
                "description": "Speed boost",
                "cooldown": player.dash_cooldown,
                "max_cooldown": player.dash_max_cooldown,
                "color": RED,
                "x": 280
            },
            {
                "key": "Q",
                "name": "EXPLODE",
                "description": "Area damage",
                "cooldown": player.explosion_cooldown,
                "max_cooldown": player.explosion_max_cooldown,
                "color": ORANGE,
                "x": 510
            },
            {
                "key": "L-CLICK",
                "name": "SHOOT",
                "description": "Fire weapon",
                "cooldown": 0,
                "max_cooldown": 1,
                "color": CYAN,
                "x": 740
            }
        ]

        for skill in skill_boxes:
            self._draw_skill_box(screen, skill, ui_y)

    def _draw_skill_box(self, screen, skill, ui_y):
        x = skill["x"]
        y = ui_y + 55
        box_width = 180
        box_height = 65

        # 스킬 박스 배경
        is_ready = skill["cooldown"] == 0
        box_color = (40, 40, 80) if is_ready else (60, 30, 30)
        border_color = skill["color"] if is_ready else (100, 100, 100)

        # 메인 박스
        pygame.draw.rect(screen, box_color, (x, y, box_width, box_height), 0)
        pygame.draw.rect(screen, border_color, (x, y, box_width, box_height), 2)

        # 쿨다운 오버레이
        if skill["cooldown"] > 0:
            cooldown_ratio = skill["cooldown"] / skill["max_cooldown"]
            overlay_height = int(box_height * cooldown_ratio)

            overlay_surface = pygame.Surface((box_width, overlay_height))
            overlay_surface.set_alpha(120)
            overlay_surface.fill((80, 20, 20))
            screen.blit(overlay_surface, (x, y + box_height - overlay_height))

        # 키 텍스트 (큰 글씨)
        key_text = self.skill_font.render(skill["key"], True, skill["color"])
        screen.blit(key_text, (x + 8, y + 8))

        # 스킬 이름
        name_text = self.cooldown_font.render(skill["name"], True, WHITE)
        screen.blit(name_text, (x + 8, y + 32))

        # 설명
        desc_text = self.cooldown_font.render(skill["description"], True, (180, 180, 180))
        screen.blit(desc_text, (x + 8, y + 48))

        # 상태 표시
        if skill["cooldown"] > 0:
            cooldown_sec = (skill["cooldown"] // 60) + 1
            status_text = self.cooldown_font.render(f"{cooldown_sec}s", True, RED)
            screen.blit(status_text, (x + box_width - 35, y + 8))
        else:
            status_text = self.cooldown_font.render("RDY", True, GREEN)
            screen.blit(status_text, (x + box_width - 35, y + 8))

    def draw_game_info(self, screen, enemy_count, score=0, level=1):
        """게임 정보 (좌하단)"""
        info_x = 20
        info_y = SCREEN_HEIGHT - 120

        # 배경
        info_bg = pygame.Surface((280, 90))
        info_bg.set_alpha(150)
        info_bg.fill((20, 20, 40))
        screen.blit(info_bg, (info_x, info_y))

        # 게임 정보
        controls_text = self.info_font.render("WASD: Move | L-Click: Shoot", True, WHITE)
        screen.blit(controls_text, (info_x + 5, info_y + 5))

        controls_text2 = self.info_font.render("1,2,3: Weapons | ESC: Quit", True, WHITE)
        screen.blit(controls_text2, (info_x + 5, info_y + 25))

        # 적군 수와 레벨 정보
        enemy_text = self.info_font.render(f"Enemies: {enemy_count} | Level: {level}", True, RED)
        screen.blit(enemy_text, (info_x + 5, info_y + 45))

        # 점수
        score_text = self.info_font.render(f"Score: {score}", True, GOLD)
        screen.blit(score_text, (info_x + 5, info_y + 65))

    def draw_fps(self, screen, clock):
        """FPS 표시 (우하단) - 위치 수정"""
        fps = int(clock.get_fps())
        fps_text = self.cooldown_font.render(f"FPS: {fps}", True, WHITE)
        fps_rect = fps_text.get_rect()
        # 미니맵과 겹치지 않게 위치 조정
        fps_rect.bottomright = (SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10)

        # 반투명 배경
        bg_surface = pygame.Surface((fps_rect.width + 10, fps_rect.height + 6))
        bg_surface.set_alpha(150)
        bg_surface.fill((0, 0, 0))
        screen.blit(bg_surface, (fps_rect.x - 5, fps_rect.y - 3))

        screen.blit(fps_text, fps_rect)

    def draw_game_over_screen(self, screen, final_score):
        """게임 오버 화면"""
        # 반투명 오버레이
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # 게임 오버 텍스트
        game_over_text = self.title_font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(game_over_text, game_over_rect)

        # 점수
        score_text = self.skill_font.render(f"Final Score: {final_score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_text, score_rect)

        # 재시작 안내
        restart_text = self.info_font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(restart_text, restart_rect)