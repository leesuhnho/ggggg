# config.py - 게임 설정 상수들 (대폭 업그레이드)

# 화면 설정
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# 맵 설정 (훨씬 큰 월드)
WORLD_WIDTH = 3000
WORLD_HEIGHT = 2000

# 색상 정의
BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
DARK_BLUE = (20, 80, 150)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)
PURPLE = (128, 0, 255)
GOLD = (255, 215, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
ORANGE = (255, 165, 0)
DARK_RED = (139, 0, 0)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# 플레이어 설정
PLAYER_SIZE = 35
PLAYER_SPEED = 4
PLAYER_DASH_MULTIPLIER = 2.5
PLAYER_MAX_HP = 100

# 스킬 설정 (프레임 단위)
BLINK_COOLDOWN = 180     # 3초로 감소
BLINK_RANGE = 200        # 범위 확대
DASH_COOLDOWN = 600      # 10초
DASH_DURATION = 120      # 2초
EXPLOSION_COOLDOWN = 180 # 3초

# 무기 설정
WEAPON_TYPES = {
    'PISTOL': {
        'name': 'Pistol',
        'damage': 25,
        'speed': 8,
        'cooldown': 0,
        'bullets': 1,
        'spread': 0,
        'color': CYAN
    },
    'SHOTGUN': {
        'name': 'Shotgun',
        'damage': 15,
        'speed': 6,
        'cooldown': 30,  # 0.5초 쿨다운
        'bullets': 5,    # 5발 동시 발사
        'spread': 0.8,   # 퍼짐 각도
        'color': ORANGE
    },
    'SNIPER': {
        'name': 'Sniper',
        'damage': 250,   # 10배 데미지
        'speed': 12,
        'cooldown': 180, # 3초 쿨다운
        'bullets': 1,
        'spread': 0,
        'color': RED
    }
}

# 총알 설정
BULLET_SIZE = 4
BULLET_LIFETIME = 180    # 3초

# 적군 설정 (AI 강화)
ENEMY_SIZE = 25
ENEMY_SPEED = 2.0        # 속도 증가
ENEMY_HP = 80           # 체력 감소 (총이 강해졌으므로)
ENEMY_SPAWN_RATE = 240   # 4초마다 스폰 (더 어렵게)
ENEMY_ATTACK_DAMAGE = 15 # 적군 공격 데미지
ENEMY_ATTACK_RANGE = 35  # 공격 범위
ENEMY_SIGHT_RANGE = 200  # 시야 범위
ENEMY_SMART_MOVE_CHANCE = 0.3  # 30% 확률로 스마트 이동

# 폭발 설정
EXPLOSION_RADIUS = 80
EXPLOSION_DAMAGE = 60
EXPLOSION_DURATION = 30

# 카메라 설정
CAMERA_SMOOTH = 0.1      # 카메라 부드러움 (0.1 = 10% 씩 이동)
CAMERA_MOUSE_INFLUENCE = 0.3  # 마우스 영향도
CAMERA_MAX_OFFSET = 150  # 최대 오프셋

# 미니맵 설정
MINIMAP_SIZE = 150
MINIMAP_SCALE = 0.1      # 실제 맵 대비 축소 비율

# 물리 법칙 설정
GRAVITY = 0.5
FRICTION = 0.95
BOUNCE_DAMPING = 0.7
TERMINAL_VELOCITY = 15

# 레벨 시스템
LEVEL_UP_KILLS = 10  # 10킬마다 레벨업
ENEMY_SPAWN_BASE = 3  # 기본 적군 수
ENEMY_SPAWN_INCREASE = 2  # 레벨당 증가 수

# 아이템 설정
HEALTH_PACK_SPAWN_RATE = 600  # 10초마다 체크
HEALTH_PACK_HEAL_AMOUNT = 30
HEALTH_PACK_SIZE = 20

# 맵 환경 설정
MAP_THEME = "industrial"  # industrial, nature, sci-fi
DECORATION_COUNT = 30

# 장애물 설정
OBSTACLE_TYPES = {
    'WALL': {'destructible': False, 'hp': 0, 'color': GRAY},
    'CRATE': {'destructible': True, 'hp': 50, 'color': (139, 69, 19)},
    'METAL': {'destructible': True, 'hp': 100, 'color': (169, 169, 169)},
    'PILLAR': {'destructible': False, 'hp': 0, 'color': (105, 105, 105)}
}

# 애니메이션 설정
PARTICLE_COUNT_HIGH = 30
PARTICLE_COUNT_MEDIUM = 20
PARTICLE_COUNT_LOW = 10
SCREEN_SHAKE_INTENSITY = 5

# UI 설정
UI_HEIGHT = 120