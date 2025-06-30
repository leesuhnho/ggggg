# camera.py - 동적 카메라 시스템

import pygame
import math
from config import *
from utils import *


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.shake_x = 0
        self.shake_y = 0
        self.shake_intensity = 0

    def update(self, player_pos, mouse_pos):
        """카메라 업데이트 - 플레이어와 마우스 위치 고려"""
        player_x, player_y = player_pos

        # 마우스 위치를 월드 좌표로 변환
        world_mouse_x = mouse_pos[0] + self.x
        world_mouse_y = mouse_pos[1] + self.y

        # 플레이어와 마우스 사이의 중점 계산
        offset_x = (world_mouse_x - player_x) * CAMERA_MOUSE_INFLUENCE
        offset_y = (world_mouse_y - player_y) * CAMERA_MOUSE_INFLUENCE

        # 오프셋 제한
        offset_x = clamp(offset_x, -CAMERA_MAX_OFFSET, CAMERA_MAX_OFFSET)
        offset_y = clamp(offset_y, -CAMERA_MAX_OFFSET, CAMERA_MAX_OFFSET)

        # 목표 카메라 위치 계산 (플레이어 중심 + 마우스 오프셋)
        self.target_x = player_x - SCREEN_WIDTH // 2 + offset_x
        self.target_y = player_y - SCREEN_HEIGHT // 2 + offset_y

        # 월드 경계 제한
        self.target_x = clamp(self.target_x, 0, WORLD_WIDTH - SCREEN_WIDTH)
        self.target_y = clamp(self.target_y, 0, WORLD_HEIGHT - SCREEN_HEIGHT + UI_HEIGHT)

        # 부드러운 카메라 이동
        self.x = lerp(self.x, self.target_x, CAMERA_SMOOTH)
        self.y = lerp(self.y, self.target_y, CAMERA_SMOOTH)

        # 화면 흔들림 업데이트
        if self.shake_intensity > 0:
            import random
            self.shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_intensity -= 0.5
        else:
            self.shake_x = 0
            self.shake_y = 0

    def add_shake(self, intensity):
        """화면 흔들림 추가"""
        self.shake_intensity = max(self.shake_intensity, intensity)

    def world_to_screen(self, world_x, world_y):
        """월드 좌표를 스크린 좌표로 변환"""
        screen_x = world_x - self.x + self.shake_x
        screen_y = world_y - self.y + self.shake_y
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x, screen_y):
        """스크린 좌표를 월드 좌표로 변환"""
        world_x = screen_x + self.x - self.shake_x
        world_y = screen_y + self.y - self.shake_y
        return (world_x, world_y)

    def is_visible(self, world_x, world_y, size=0):
        """객체가 화면에 보이는지 체크"""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        margin = size + 50  # 여유 마진

        return (-margin <= screen_x <= SCREEN_WIDTH + margin and
                -margin <= screen_y <= SCREEN_HEIGHT + margin)

    def get_visible_area(self):
        """현재 보이는 월드 영역 반환"""
        return {
            'left': self.x,
            'right': self.x + SCREEN_WIDTH,
            'top': self.y,
            'bottom': self.y + SCREEN_HEIGHT
        }