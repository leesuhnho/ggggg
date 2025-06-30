# obstacle.py - 장애물 시스템 (완전 재설계)

import pygame
import random
import math
from config import *
from utils import *


class Obstacle:
    def __init__(self, x, y, width, height, obstacle_type="wall"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obstacle_type
        self.destructible = False
        self.hp = 0
        self.max_hp = 0

        # 장애물 타입별 설정
        if obstacle_type == "wall":
            self.color = GRAY
            self.destructible = False
        elif obstacle_type == "crate":
            self.color = (139, 69, 19)  # 갈색
            self.destructible = True
            self.hp = 50
            self.max_hp = 50
        elif obstacle_type == "metal":
            self.color = (169, 169, 169)  # 밝은 회색
            self.destructible = True
            self.hp = 100
            self.max_hp = 100
        elif obstacle_type == "pillar":
            self.color = (105, 105, 105)  # 어두운 회색
            self.destructible = False

        self.destroyed = False
        self.destruction_particles = []

    def get_rect(self):
        """충돌 검사용 사각형 반환"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def check_collision_with_rect(self, rect):
        """다른 사각형과의 충돌 체크"""
        return self.get_rect().colliderect(rect)

    def check_collision_with_circle(self, center_x, center_y, radius):
        """원과의 충돌 체크"""
        # 사각형과 원의 충돌 검사
        closest_x = max(self.x, min(center_x, self.x + self.width))
        closest_y = max(self.y, min(center_y, self.y + self.height))

        distance = math.sqrt((center_x - closest_x) ** 2 + (center_y - closest_y) ** 2)
        return distance <= radius

    def take_damage(self, damage):
        """데미지 받기 (파괴 가능한 장애물만)"""
        if not self.destructible or self.destroyed:
            return False

        self.hp -= damage
        if self.hp <= 0:
            self.destroyed = True
            self._create_destruction_effect()
            return True
        return False

    def _create_destruction_effect(self):
        """파괴 효과 생성"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        # 파괴 파티클 생성
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.destruction_particles.append({
                'x': center_x + random.uniform(-self.width // 4, self.width // 4),
                'y': center_y + random.uniform(-self.height // 4, self.height // 4),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 30,
                'max_life': 30,
                'size': random.uniform(2, 5)
            })

    def update(self):
        """업데이트 (파괴 파티클)"""
        for particle in self.destruction_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95

            if particle['life'] <= 0:
                self.destruction_particles.remove(particle)

    def draw(self, screen, camera):
        """장애물 그리기"""
        if self.destroyed and len(self.destruction_particles) == 0:
            return

        # 화면에 보이는지 체크
        if not camera.is_visible(self.x + self.width // 2, self.y + self.height // 2,
                                 max(self.width, self.height)):
            return

        screen_x, screen_y = camera.world_to_screen(self.x, self.y)

        # 파괴 파티클 그리기
        for particle in self.destruction_particles:
            if camera.is_visible(particle['x'], particle['y']):
                p_screen_x, p_screen_y = camera.world_to_screen(particle['x'], particle['y'])
                alpha = int(255 * (particle['life'] / particle['max_life']))
                if alpha > 0:
                    particle_surface = pygame.Surface((int(particle['size'] * 2), int(particle['size'] * 2)))
                    particle_surface.set_alpha(alpha)
                    particle_surface.fill(self.color)
                    screen.blit(particle_surface, (p_screen_x - particle['size'],
                                                   p_screen_y - particle['size']))

        if not self.destroyed:
            # 그림자
            shadow_offset = 4
            pygame.draw.rect(screen, (50, 50, 50),
                             (screen_x + shadow_offset, screen_y + shadow_offset,
                              self.width, self.height))

            # 메인 장애물
            pygame.draw.rect(screen, self.color,
                             (screen_x, screen_y, self.width, self.height))

            # 테두리 (타입별)
            border_color = WHITE
            if self.type == "crate":
                border_color = (101, 67, 33)  # 어두운 갈색
            elif self.type == "metal":
                border_color = (105, 105, 105)

            pygame.draw.rect(screen, border_color,
                             (screen_x, screen_y, self.width, self.height), 2)

            # HP 바 (파괴 가능한 장애물)
            if self.destructible and self.hp < self.max_hp:
                self._draw_hp_bar(screen, screen_x, screen_y)

    def _draw_hp_bar(self, screen, screen_x, screen_y):
        """HP 바 그리기"""
        bar_width = self.width
        bar_height = 4
        bar_x = screen_x
        bar_y = screen_y - 8

        # 배경 (빨간색)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))

        # HP 바 (노란색)
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, YELLOW,
                         (bar_x, bar_y, bar_width * hp_ratio, bar_height))


class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self._generate_meaningful_map()

    def _generate_meaningful_map(self):
        """의미있는 맵 구조 생성"""
        # 1. 외곽 경계벽 생성
        self._create_boundary_walls()

        # 2. 중앙 건물 복합체
        self._create_central_complex()

        # 3. 4개 구역에 서로 다른 구조물
        self._create_quadrant_structures()

        # 4. 연결 통로와 chokepoint
        self._create_corridors_and_chokepoints()

        # 5. 전술적 엄폐물
        self._create_tactical_cover()

    def _create_boundary_walls(self):
        """외곽 경계벽 - 두껍게"""
        wall_thickness = 30

        # 상단
        self.obstacles.append(Obstacle(0, 0, WORLD_WIDTH, wall_thickness, "wall"))
        # 하단
        self.obstacles.append(Obstacle(0, WORLD_HEIGHT - wall_thickness,
                                       WORLD_WIDTH, wall_thickness, "wall"))
        # 좌측
        self.obstacles.append(Obstacle(0, 0, wall_thickness, WORLD_HEIGHT, "wall"))
        # 우측
        self.obstacles.append(Obstacle(WORLD_WIDTH - wall_thickness, 0,
                                       wall_thickness, WORLD_HEIGHT, "wall"))

    def _create_central_complex(self):
        """중앙 건물 복합체 - 대칭적 구조"""
        center_x = WORLD_WIDTH // 2
        center_y = WORLD_HEIGHT // 2

        # 중앙 홀 (플레이어 스폰 공간 확보)
        hall_size = 200

        # 중앙 홀 주변 4개 건물
        building_size = 120
        gap = 100

        # 북서 건물
        self._create_building(center_x - gap - building_size,
                              center_y - gap - building_size, building_size)

        # 북동 건물
        self._create_building(center_x + gap,
                              center_y - gap - building_size, building_size)

        # 남서 건물
        self._create_building(center_x - gap - building_size,
                              center_y + gap, building_size)

        # 남동 건물
        self._create_building(center_x + gap,
                              center_y + gap, building_size)

    def _create_building(self, x, y, size):
        """개별 건물 생성"""
        # 외벽
        wall_thick = 15

        # 북벽 (입구 제외)
        self.obstacles.append(Obstacle(x, y, size // 3, wall_thick, "wall"))
        self.obstacles.append(Obstacle(x + size // 3 + 30, y, size // 3, wall_thick, "wall"))

        # 남벽
        self.obstacles.append(Obstacle(x, y + size - wall_thick, size, wall_thick, "wall"))

        # 서벽
        self.obstacles.append(Obstacle(x, y, wall_thick, size, "wall"))

        # 동벽 (입구 제외)
        self.obstacles.append(Obstacle(x + size - wall_thick, y, wall_thick, size // 2, "wall"))
        self.obstacles.append(Obstacle(x + size - wall_thick, y + size // 2 + 25,
                                       wall_thick, size // 2 - 25, "wall"))

        # 내부 구조물
        self.obstacles.append(Obstacle(x + 30, y + 30, 25, 25, "crate"))
        self.obstacles.append(Obstacle(x + size - 55, y + size - 55, 30, 30, "metal"))

    def _create_quadrant_structures(self):
        """4개 구역별 특별 구조물"""

        # 1사분면 (우상단) - 창고 지역
        self._create_warehouse_area(WORLD_WIDTH * 3 // 4, WORLD_HEIGHT * 1 // 4)

        # 2사분면 (좌상단) - 공장 지역
        self._create_factory_area(WORLD_WIDTH * 1 // 4, WORLD_HEIGHT * 1 // 4)

        # 3사분면 (좌하단) - 미로 지역
        self._create_maze_area(WORLD_WIDTH * 1 // 4, WORLD_HEIGHT * 3 // 4)

        # 4사분면 (우하단) - 개방 지역
        self._create_open_area(WORLD_WIDTH * 3 // 4, WORLD_HEIGHT * 3 // 4)

    def _create_warehouse_area(self, center_x, center_y):
        """창고 지역 - 큰 상자들과 통로"""
        # 대형 창고들
        for i in range(3):
            for j in range(2):
                x = center_x - 100 + i * 70
                y = center_y - 50 + j * 60
                self.obstacles.append(Obstacle(x, y, 50, 40, "crate"))

        # 스택된 상자들
        self.obstacles.append(Obstacle(center_x + 50, center_y - 30, 25, 25, "crate"))
        self.obstacles.append(Obstacle(center_x + 52, center_y - 32, 25, 25, "crate"))

    def _create_factory_area(self, center_x, center_y):
        """공장 지역 - 기계와 파이프라인"""
        # 생산 라인
        for i in range(4):
            x = center_x - 80 + i * 40
            y = center_y
            self.obstacles.append(Obstacle(x, y, 30, 15, "metal"))

        # 큰 기계
        self.obstacles.append(Obstacle(center_x - 50, center_y - 60, 80, 50, "metal"))

        # 보일러들
        for i in range(3):
            x = center_x - 30 + i * 30
            y = center_y + 40
            self.obstacles.append(Obstacle(x, y, 20, 35, "metal"))

    def _create_maze_area(self, center_x, center_y):
        """미로 지역 - 복잡한 벽 구조"""
        maze_patterns = [
            # 가로벽들
            (center_x - 80, center_y - 40, 60, 15),
            (center_x + 20, center_y - 40, 60, 15),
            (center_x - 60, center_y, 80, 15),
            (center_x + 40, center_y + 40, 60, 15),

            # 세로벽들
            (center_x - 40, center_y - 60, 15, 50),
            (center_x + 20, center_y - 20, 15, 60),
            (center_x + 60, center_y - 60, 15, 50),
        ]

        for x, y, w, h in maze_patterns:
            self.obstacles.append(Obstacle(x, y, w, h, "wall"))

    def _create_open_area(self, center_x, center_y):
        """개방 지역 - 소수의 전략적 엄폐물"""
        # 중앙 기둥
        self.obstacles.append(Obstacle(center_x - 15, center_y - 15, 30, 30, "pillar"))

        # 주변 작은 엄폐물들
        positions = [
            (center_x - 60, center_y - 60),
            (center_x + 40, center_y - 50),
            (center_x - 70, center_y + 30),
            (center_x + 50, center_y + 40)
        ]

        for x, y in positions:
            self.obstacles.append(Obstacle(x, y, 25, 25, "crate"))

    def _create_corridors_and_chokepoints(self):
        """연결 통로와 병목지점"""
        # 주요 십자로 (맵 중앙)
        center_x = WORLD_WIDTH // 2
        center_y = WORLD_HEIGHT // 2

        # 수평 주 통로 장애물 (부분적 차단)
        self.obstacles.append(Obstacle(center_x - 200, center_y - 100, 30, 40, "wall"))
        self.obstacles.append(Obstacle(center_x + 170, center_y + 60, 30, 40, "wall"))

        # 수직 주 통로 장애물
        self.obstacles.append(Obstacle(center_x - 100, center_y - 200, 40, 30, "wall"))
        self.obstacles.append(Obstacle(center_x + 60, center_y + 170, 40, 30, "wall"))

        # 병목지점 생성 - 전략적 위치
        chokepoints = [
            # 상단 병목
            (center_x - 30, 200, 15, 60),
            (center_x + 15, 200, 15, 60),

            # 하단 병목
            (center_x - 30, WORLD_HEIGHT - 260, 15, 60),
            (center_x + 15, WORLD_HEIGHT - 260, 15, 60),

            # 좌측 병목
            (200, center_y - 30, 60, 15),
            (200, center_y + 15, 60, 15),

            # 우측 병목
            (WORLD_WIDTH - 260, center_y - 30, 60, 15),
            (WORLD_WIDTH - 260, center_y + 15, 60, 15),
        ]

        for x, y, w, h in chokepoints:
            self.obstacles.append(Obstacle(x, y, w, h, "wall"))

    def _create_tactical_cover(self):
        """전술적 엄폐물 배치"""
        # 맵 전체에 전략적 엄폐물 배치
        cover_positions = [
            # 맵 경계 근처
            (100, 100, "pillar"),
            (WORLD_WIDTH - 130, 100, "pillar"),
            (100, WORLD_HEIGHT - 130, "pillar"),
            (WORLD_WIDTH - 130, WORLD_HEIGHT - 130, "pillar"),

            # 중간 지점들
            (WORLD_WIDTH // 4, 300, "crate"),
            (WORLD_WIDTH * 3 // 4, 300, "crate"),
            (WORLD_WIDTH // 4, WORLD_HEIGHT - 330, "crate"),
            (WORLD_WIDTH * 3 // 4, WORLD_HEIGHT - 330, "crate"),

            # 추가 전술 위치
            (500, 200, "metal"),
            (WORLD_WIDTH - 530, 200, "metal"),
            (500, WORLD_HEIGHT - 230, "metal"),
            (WORLD_WIDTH - 530, WORLD_HEIGHT - 230, "metal"),
        ]

        for x, y, obj_type in cover_positions:
            if obj_type == "pillar":
                self.obstacles.append(Obstacle(x, y, 25, 25, "pillar"))
            elif obj_type == "crate":
                self.obstacles.append(Obstacle(x, y, 35, 35, "crate"))
            elif obj_type == "metal":
                self.obstacles.append(Obstacle(x, y, 30, 45, "metal"))

    def update(self):
        """장애물 업데이트"""
        for obstacle in self.obstacles:
            obstacle.update()

    def check_collision_circle(self, x, y, radius):
        """원형 충돌 체크 (플레이어, 적군용)"""
        for obstacle in self.obstacles:
            if not obstacle.destroyed:
                if obstacle.check_collision_with_circle(x, y, radius):
                    return obstacle
        return None

    def check_collision_rect(self, rect):
        """사각형 충돌 체크 (총알용)"""
        for obstacle in self.obstacles:
            if not obstacle.destroyed:
                if obstacle.check_collision_with_rect(rect):
                    return obstacle
        return None

    def check_line_collision(self, start_x, start_y, end_x, end_y):
        """선분 충돌 체크 (AI 시야용) - 개선된 버전"""
        for obstacle in self.obstacles:
            if not obstacle.destroyed:
                if self._line_rect_collision(start_x, start_y, end_x, end_y, obstacle.get_rect()):
                    return True
        return False

    def _line_rect_collision(self, x1, y1, x2, y2, rect):
        """선분과 사각형의 충돌 검사 - 개선된 알고리즘"""
        # 선분의 양 끝점이 사각형 안에 있는지 체크
        if rect.collidepoint(x1, y1) or rect.collidepoint(x2, y2):
            return True

        # 선분이 사각형의 각 변과 교차하는지 체크
        # 간단한 바운딩 박스 체크로 최적화
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)

        # 바운딩 박스가 겹치지 않으면 충돌 없음
        if (max_x < rect.left or min_x > rect.right or
                max_y < rect.top or min_y > rect.bottom):
            return False

        # 더 정확한 선분-사각형 교차 검사가 필요하면 여기서 구현
        # 현재는 간단한 버전으로 처리
        return True

    def get_obstacles_in_area(self, x, y, width, height):
        """특정 영역의 장애물 반환"""
        area_rect = pygame.Rect(x, y, width, height)
        result = []

        for obstacle in self.obstacles:
            if not obstacle.destroyed:
                if obstacle.get_rect().colliderect(area_rect):
                    result.append(obstacle)

        return result

    def draw(self, screen, camera):
        """모든 장애물 그리기"""
        for obstacle in self.obstacles:
            obstacle.draw(screen, camera)

    def get_obstacles(self):
        """살아있는 장애물들 반환"""
        return [obs for obs in self.obstacles if not obs.destroyed]