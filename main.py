# main.py - 메인 게임 루프 (킬 카운트 수정)

import pygame
import sys
from config import *
from player import Player
from enemy import EnemyManager
from effects import VisualEffects
from ui import UI
from bullet import BulletManager
from camera import Camera
from obstacle import ObstacleManager
from item import ItemManager
from level_system import LevelSystem
from decoration import DecorationManager


def main():
    # Pygame 초기화
    pygame.init()

    # 화면 설정
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Elite Combat Arena - Ultimate Edition")
    clock = pygame.time.Clock()

    # 우클릭 메뉴 비활성화
    import os
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'centered'

    # 게임 객체 생성
    player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
    enemy_manager = EnemyManager()
    bullet_manager = BulletManager()
    obstacle_manager = ObstacleManager()
    item_manager = ItemManager()
    level_system = LevelSystem()
    decoration_manager = DecorationManager()
    effects = VisualEffects()
    ui = UI()
    camera = Camera()

    # 게임 상태
    score = 0
    game_over = False

    print("=== Elite Combat Arena - Ultimate Edition ===")
    print("Controls:")
    print("WASD - Move")
    print("Right Click - Instant Blink (3s cooldown, limited range)")
    print("Left Click - Shoot")
    print("1,2,3 - Switch weapons (Pistol/Shotgun/Sniper)")
    print("F - Dash (10s cooldown)")
    print("Q - Explode (3s cooldown)")
    print("ESC - Quit")
    print("")
    print("Features:")
    print("- Physics-based items and environment")
    print("- Level system: Kill enemies to level up!")
    print("- Health packs drop randomly from the sky")
    print("- Enemies get stronger each level")
    print("- Strategic map with meaningful obstacles")
    print("============================================")

    # 게임 루프
    running = True
    while running:
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # 게임 재시작
                    player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
                    enemy_manager = EnemyManager()
                    bullet_manager = BulletManager()
                    obstacle_manager = ObstacleManager()
                    item_manager = ItemManager()
                    level_system = LevelSystem()
                    decoration_manager = DecorationManager()
                    score = 0
                    game_over = False
            # 우클릭 메뉴 방지
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # 우클릭
                    pass  # 아무것도 하지 않음으로 메뉴 방지

        if not game_over:
            # 입력 상태 확인
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            mouse_pos = pygame.mouse.get_pos()

            # 카메라 업데이트 (플레이어와 마우스 위치 고려)
            camera.update(player.get_position(), mouse_pos)

            # 게임 업데이트
            player.update(keys, mouse_buttons, mouse_pos, bullet_manager,
                          enemy_manager.get_enemies(), camera, obstacle_manager)
            enemy_manager.update(player.get_position(), camera, obstacle_manager, level_system)
            bullet_manager.update(enemy_manager.get_enemies(), obstacle_manager)
            obstacle_manager.update()
            item_manager.update(obstacle_manager, player)
            level_system.update()
            decoration_manager.update()
            effects.update()

            # 적군 처치 시 레벨 시스템 업데이트 (수정된 부분)
            for enemy in enemy_manager.enemies:  # 모든 적군 체크 (죽은 것 포함)
                if enemy.is_dead and not enemy.kill_counted:
                    level_system.add_kill()
                    score += 10 * level_system.level  # 레벨에 따른 점수 증가
                    enemy.kill_counted = True  # 중복 카운팅 방지
                    print(f"Enemy killed! Kills: {level_system.kills}/{level_system.kills_for_next_level}")

            # 플레이어 죽음 체크
            if player.is_dead():
                game_over = True

        # 화면 그리기
        screen.fill(BLACK)

        if not game_over:
            # 배경 효과 (월드 좌표)
            effects.draw_background_effect(screen)

            # 게임 객체 그리기 (카메라 적용)
            decoration_manager.draw(screen, camera)  # 장식을 가장 먼저
            obstacle_manager.draw(screen, camera)
            item_manager.draw(screen, camera)
            enemy_manager.draw(screen, camera)
            bullet_manager.draw(screen, camera)
            player.draw(screen, camera)

            # UI 그리기 (화면 좌표, 카메라 영향 없음)
            enemy_count = len(enemy_manager.get_enemies())
            ui.draw_player_hud(screen, player)
            ui.draw_level_progress(screen, level_system)  # 레벨 진행률 추가
            ui.draw_minimap(screen, player.get_position(), enemy_manager.get_enemies(), camera)
            ui.draw_skill_bar(screen, player)
            ui.draw_game_info(screen, enemy_count, score, level_system.level)
            ui.draw_fps(screen, clock)

            # 레벨업 애니메이션
            level_system.draw_level_up_effect(screen)
        else:
            # 게임 오버 화면
            ui.draw_game_over_screen(screen, score)

        # 화면 업데이트
        pygame.display.flip()
        clock.tick(FPS)

    print("Game ended. Thanks for playing Elite Combat Arena!")
    pygame.quit()
    sys.exit()
    #실험용 comit


if __name__ == "__main__":
    main()
