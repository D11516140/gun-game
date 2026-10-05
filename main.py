import sys
import math
import random
import pygame

# 1. 初始化 Pygame
pygame.init()

# --- 固定虛擬解析度 ---
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 1280, 720
game_canvas = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# 視野迷霧畫布
darkness = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
darkness.set_colorkey((0, 255, 0))  # 綠色作為透明挖空色
darkness.set_alpha(160)             # 半透明迷霧強度

# --- 實際視窗尺寸 ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("2D 戰術射擊 - 區域動態騷擾與仇恨控制")
clock = pygame.time.Clock()

def get_chinese_font(size, bold=False):
    chinese_fonts = ["microsoftjhenghei", "microsoftjhengheiui", "simhei", "arial"]
    for font_name in chinese_fonts:
        font_path = pygame.font.match_font(font_name)
        if font_path:
            font = pygame.font.Font(font_path, size)
            font.set_bold(bold)
            return font
    font = pygame.font.SysFont(None, size)
    font.set_bold(bold)
    return font

font_main = get_chinese_font(20)
font_small = get_chinese_font(16)
font_title = get_chinese_font(32, bold=True)
font_tab = get_chinese_font(22, bold=True)
font_hud = get_chinese_font(26, bold=True)

# 按鍵綁定
KEYBINDS = {
    "move_up": pygame.K_w,
    "move_down": pygame.K_s,
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "reload": pygame.K_r,
    "interact": pygame.K_e,
    "weapon_1": pygame.K_1,
    "weapon_2": pygame.K_2,
    "pause": pygame.K_ESCAPE,
    "fullscreen": pygame.K_F12
}

binding_key_target = None

LANGUAGES = {
    "zh": {
        "title": "遊戲暫停", "continue": "繼續遊戲", "quit_game": "離開遊戲",
        "tab_video": "畫面", "tab_general": "基礎", "tab_keybinds": "按鍵", "tab_audio": "聲音",
        "win_size": "視窗大小", "in_fullscreen": "(全螢幕模式中)", "mode": "顯示模式",
        "fullscreen": "全螢幕", "windowed": "視窗化", "lang": "語言 / Language",
        "lang_name": "繁體中文", "press_any_key": "請按下新按鍵...", "audio_coming_soon": "聲音設定 (即將推出)",
        "hud_info": "戰術訓練場 | [{w1}] [{w2}] 切換武器 | [{pick}] 拾取/替換武器",
        "reloading": "換彈中...", "no_ammo": "沒子彈了！(按 {reload_key} 換彈)",
        "pickup_prompt": "按 [{key}] 替換為 {weapon}",
        "weapon_depleted": "【{weapon}】子彈耗盡銷毀！",
        "auto_pistol": "【手槍】已自動補給至空欄位！",
        "dynamic_drop": "戰術空投已抵達，於附近投放【{weapon}】！",
        "loot_picked": "拾取戰術補給：恢復 25 HP 與補充彈藥！",
        "level_up": "【升級！】等級提升至 Lv.{level}！",
        "empty_slot": "空",
        "you_died": "你已陣亡！",
        "respawn_prompt": "按下 [R] 鍵重新部署任務",
        "weapons": {
            "pistol": "手槍", "shotgun": "霰彈槍", "sniper": "狙擊槍"
        },
        "key_names": {
            "move_up": "向上移動", "move_down": "向下移動", "move_left": "向左移動",
            "move_right": "向右移動", "reload": "重新裝填/重生", "interact": "拾取/替換",
            "weapon_1": "武器欄 1", "weapon_2": "武器欄 2",
            "pause": "暫停選單", "fullscreen": "切換全螢幕"
        }
    },
    "en": {
        "title": "GAME PAUSED", "continue": "Resume", "quit_game": "Quit Game",
        "tab_video": "Video", "tab_general": "General", "tab_keybinds": "Controls", "tab_audio": "Audio",
        "win_size": "Window Size", "in_fullscreen": "(In Fullscreen)", "mode": "Display Mode",
        "fullscreen": "Fullscreen", "windowed": "Windowed", "lang": "Language / 語言",
        "lang_name": "English", "press_any_key": "Press Any Key...", "audio_coming_soon": "Audio Settings (Coming Soon)",
        "hud_info": "Tactical Arena | [{w1}] [{w2}] Switch Guns | [{pick}] Pickup / Swap",
        "reloading": "RELOADING...", "no_ammo": "NO AMMO! (Press {reload_key})",
        "pickup_prompt": "Press [{key}] to swap with {weapon}",
        "weapon_depleted": "[{weapon}] depleted & destroyed!",
        "auto_pistol": "[Pistol] auto-supplied to empty slot!",
        "dynamic_drop": "Tactical Air-drop arrived! [{weapon}] nearby!",
        "loot_picked": "Loot Collected: +25 HP & Ammo Refilled!",
        "level_up": "[LEVEL UP!] Reached Lv.{level}!",
        "empty_slot": "EMPTY",
        "you_died": "YOU DIED!",
        "respawn_prompt": "Press [R] to Respawn",
        "weapons": {
            "pistol": "Pistol", "shotgun": "Shotgun", "sniper": "Sniper Rifle"
        },
        "key_names": {
            "move_up": "Move Up", "move_down": "Move Down", "move_left": "Move Left",
            "move_right": "Move Right", "reload": "Reload/Respawn", "interact": "Interact / Swap",
            "weapon_1": "Weapon Slot 1", "weapon_2": "Weapon Slot 2",
            "pause": "Pause Menu", "fullscreen": "Toggle Fullscreen"
        }
    }
}

current_lang = "zh"
current_tab = "video"

WORLD_WIDTH, WORLD_HEIGHT = 3200, 2400
GRID_COLOR = (45, 45, 55)
WHITE, BLUE, RED, YELLOW, GRAY, GREEN = (255, 255, 255), (50, 150, 255), (230, 50, 50), (255, 220, 50), (120, 120, 120), (50, 220, 100)
TACTICAL_GROUND = (32, 35, 42)
BUTTON_BG, BUTTON_HOVER = (50, 60, 75), (70, 85, 110)
TAB_BG, TAB_ACTIVE = (35, 42, 55), (70, 90, 120)
QUIT_BG, QUIT_HOVER = (120, 45, 45), (160, 55, 55)

COLOR_SOLID = (100, 110, 125)        # 實心牆
COLOR_PENETRABLE = (160, 110, 70)    # 可穿透薄牆
COLOR_DESTRUCTIBLE = (200, 150, 80)  # 可破壞牆/木箱
COLOR_MINIMAP_BG = (20, 22, 28)

# 中立單位小地圖顏色標籤 (琥珀橘色)
COLOR_NEUTRAL_MINIMAP_VISIBLE = (255, 160, 20)
COLOR_NEUTRAL_MINIMAP_LKP = (160, 110, 30)

# 地圖結構與物件資料
structures = []
scattered_covers = []
solid_walls = []
penetrable_walls = []
destructible_walls = []
ground_weapons = []
enemies = []             # 中立單位/騷擾敵人清單
loot_drops = []          # 擊殺產生的經驗包/補給箱

MINIMAP_WIDTH, MINIMAP_HEIGHT = 240, 180
scale_x, scale_y = MINIMAP_WIDTH / WORLD_WIDTH, MINIMAP_HEIGHT / WORLD_HEIGHT
static_minimap = pygame.Surface((MINIMAP_WIDTH, MINIMAP_HEIGHT))

PREFABS = [
    {
        "width": 300, "height": 300,
        "elements": [
            ('solid', 0, 0, 100, 16), ('solid', 200, 0, 100, 16),
            ('solid', 0, 284, 100, 16), ('solid', 200, 284, 100, 16),
            ('penetrable', 0, 0, 16, 100), ('penetrable', 0, 200, 16, 100),
            ('penetrable', 284, 0, 16, 100), ('penetrable', 284, 200, 16, 100),
            ('destructible', 120, 120, 60, 60)
        ]
    },
    {
        "width": 260, "height": 260,
        "elements": [
            ('solid', 0, 0, 260, 16), ('solid', 0, 0, 16, 260),
            ('penetrable', 100, 80, 12, 120), ('penetrable', 100, 200, 120, 12),
            ('destructible', 180, 50, 40, 40), ('destructible', 180, 100, 40, 40)
        ]
    },
    {
        "width": 220, "height": 220,
        "elements": [
            ('solid', 0, 0, 220, 16), ('solid', 204, 0, 16, 220),
            ('destructible', 80, 80, 60, 60)
        ]
    }
]

def create_structure(prefab, x, y):
    struct = {
        "rect": pygame.Rect(x, y, prefab["width"], prefab["height"]),
        "center": (x + prefab["width"] // 2, y + prefab["height"] // 2),
        "solids": [],
        "penetrables": [],
        "destructibles": []
    }
    for elem in prefab["elements"]:
        e_type, ex, ey, ew, eh = elem
        world_r = pygame.Rect(x + ex, y + ey, ew, eh)
        if e_type == 'solid': struct["solids"].append(world_r)
        elif e_type == 'penetrable': struct["penetrables"].append(world_r)
        elif e_type == 'destructible': struct["destructibles"].append({"rect": world_r, "hp": 100, "max_hp": 100})
    return struct

def create_enemy(e_type, x, y):
    if e_type == "melee":
        return {
            "type": "melee", "x": x, "y": y, "radius": 16,
            "hp": 80, "max_hp": 80, "speed": 2.2, "damage": 15,
            "attack_cd": 1000, "last_attack": 0,
            "last_known_pos": None, "is_visible": False,
            "is_aggro": False, "aggro_range": 380, "max_chase_dist": 480,
            "exp_reward": 35  # 擊殺獎勵經驗值
        }
    elif e_type == "ranged":
        return {
            "type": "ranged", "x": x, "y": y, "radius": 14,
            "hp": 60, "max_hp": 60, "speed": 1.6, "damage": 10,
            "attack_cd": 1800, "last_attack": 0,
            "last_known_pos": None, "is_visible": False,
            "is_aggro": False, "aggro_range": 380, "max_chase_dist": 480,
            "exp_reward": 50  # 擊殺獎勵經驗值
        }

def spawn_harassment_enemies_safely(p_pos):
    nearby_enemies = [
        e for e in enemies 
        if math.hypot(e["x"] - p_pos[0], e["y"] - p_pos[1]) <= 1200
    ]
    
    TARGET_LOCAL_ENEMIES = 5
    if len(nearby_enemies) >= TARGET_LOCAL_ENEMIES:
        return

    needed = TARGET_LOCAL_ENEMIES - len(nearby_enemies)
    for _ in range(needed):
        for _ in range(15):
            angle = random.uniform(0, math.tau)
            dist = random.uniform(600, 950)
            candidate_x = p_pos[0] + math.cos(angle) * dist
            candidate_y = p_pos[1] + math.sin(angle) * dist

            if not (60 <= candidate_x <= WORLD_WIDTH - 60 and 60 <= candidate_y <= WORLD_HEIGHT - 60):
                continue

            cand_rect = pygame.Rect(candidate_x - 16, candidate_y - 16, 32, 32)
            if any(cand_rect.colliderect(w) for w in solid_walls + penetrable_walls):
                continue
            if any(cand_rect.colliderect(d["rect"]) for d in destructible_walls):
                continue

            e_type = random.choice(["melee", "ranged"])
            enemies.append(create_enemy(e_type, candidate_x, candidate_y))
            break

def rebuild_collision_lists():
    global solid_walls, penetrable_walls, destructible_walls
    solid_walls = [
        pygame.Rect(0, 0, WORLD_WIDTH, 20),
        pygame.Rect(0, 0, 20, WORLD_HEIGHT),
        pygame.Rect(0, WORLD_HEIGHT - 20, WORLD_WIDTH, 20),
        pygame.Rect(WORLD_WIDTH - 20, 0, 20, WORLD_HEIGHT)
    ]
    penetrable_walls = []
    destructible_walls = []

    for s in structures:
        solid_walls.extend(s["solids"])
        penetrable_walls.extend(s["penetrables"])
        s["destructibles"] = [d for d in s["destructibles"] if d["hp"] > 0]
        destructible_walls.extend(s["destructibles"])

    for c in scattered_covers:
        if c.get("hp", 1) <= 0: continue
        if c["type"] == 'solid': solid_walls.append(c["rect"])
        elif c["type"] == 'penetrable': penetrable_walls.append(c["rect"])
        elif c["type"] == 'destructible': destructible_walls.append(c)

def draw_full_minimap():
    static_minimap.fill(COLOR_MINIMAP_BG)
    for wall in solid_walls:
        pygame.draw.rect(static_minimap, COLOR_SOLID, (wall.x * scale_x, wall.y * scale_y, max(1, wall.width * scale_x), max(1, wall.height * scale_y)))
    for wall in penetrable_walls:
        pygame.draw.rect(static_minimap, COLOR_PENETRABLE, (wall.x * scale_x, wall.y * scale_y, max(1, wall.width * scale_x), max(1, wall.height * scale_y)))
    for d_wall in destructible_walls:
        w = d_wall["rect"]
        pygame.draw.rect(static_minimap, COLOR_DESTRUCTIBLE, (w.x * scale_x, w.y * scale_y, max(1, w.width * scale_x), max(1, w.height * scale_y)))

def create_weapon(w_type):
    if w_type == "pistol":
        return {
            "id": "pistol", "name": "Pistol", "clip_size": 12, "current_ammo": 12,
            "reserve_ammo": float('inf'), "fire_rate": 180, "reload_time": 1200,
            "bullet_speed": 22, "base_damage": 35, "spread_min": 0.5, "spread_max": 3.0,
            "recoil_per_shot": 0.7, "pellets": 1, "pen_decay": 0.65
        }
    elif w_type == "shotgun":
        return {
            "id": "shotgun", "name": "Shotgun", "clip_size": 6, "current_ammo": 6,
            "reserve_ammo": 18, "fire_rate": 750, "reload_time": 2000,
            "bullet_speed": 18, "base_damage": 18, "spread_min": 6.0, "spread_max": 12.0,
            "recoil_per_shot": 2.5, "pellets": 7, "pen_decay": 0.40
        }
    elif w_type == "sniper":
        return {
            "id": "sniper", "name": "Sniper", "clip_size": 5, "current_ammo": 5,
            "reserve_ammo": 15, "fire_rate": 1100, "reload_time": 2500,
            "bullet_speed": 36, "base_damage": 110, "spread_min": 0.1, "spread_max": 6.0,
            "recoil_per_shot": 3.5, "pellets": 1, "pen_decay": 0.85
        }

def generate_random_map():
    global structures, scattered_covers, ground_weapons, enemies, loot_drops
    structures.clear()
    scattered_covers.clear()
    ground_weapons.clear()
    enemies.clear()
    loot_drops.clear()

    grid_cols, grid_rows = 4, 3
    cell_w, cell_h = WORLD_WIDTH // grid_cols, WORLD_HEIGHT // grid_rows
    player_spawn_zone = pygame.Rect(WORLD_WIDTH // 2 - 250, WORLD_HEIGHT // 2 - 250, 500, 500)

    for col in range(grid_cols):
        for row in range(grid_rows):
            cell_rect = pygame.Rect(col * cell_w + 40, row * cell_h + 40, cell_w - 80, cell_h - 80)
            if cell_rect.colliderect(player_spawn_zone):
                continue

            num_structures = random.randint(1, 2)
            for _ in range(num_structures):
                prefab = random.choice(PREFABS)
                pw, ph = prefab["width"], prefab["height"]
                for _ in range(15):
                    rx = random.randint(cell_rect.left, max(cell_rect.left + 1, cell_rect.right - pw))
                    ry = random.randint(cell_rect.top, max(cell_rect.top + 1, cell_rect.bottom - ph))
                    cand_rect = pygame.Rect(rx - 30, ry - 30, pw + 60, ph + 60)
                    if not any(cand_rect.colliderect(s["rect"]) for s in structures):
                        structures.append(create_structure(prefab, rx, ry))
                        break

            for _ in range(random.randint(2, 4)):
                cx = random.randint(cell_rect.left, cell_rect.right - 40)
                cy = random.randint(cell_rect.top, cell_rect.bottom - 40)
                cw, ch = random.choice([(40, 40), (60, 20), (20, 60), (50, 50)])
                c_rect = pygame.Rect(cx, cy, cw, ch)
                if not any(c_rect.colliderect(s["rect"]) for s in structures):
                    c_type = random.choice(['destructible', 'penetrable', 'solid'])
                    if c_type == 'destructible':
                        scattered_covers.append({"rect": c_rect, "hp": 80, "max_hp": 80, "type": 'destructible'})
                    else:
                        scattered_covers.append({"rect": c_rect, "type": c_type})

    rebuild_collision_lists()
    spawn_harassment_enemies_safely([WORLD_WIDTH // 2, WORLD_HEIGHT // 2])
    draw_full_minimap()

game_state = "PLAYING"
is_fullscreen = False
RESOLUTIONS = [(1024, 576), (1280, 720), (1600, 900), (1920, 1080)]
current_res_idx = 1

def set_display_mode(w, h, fullscreen=False):
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, is_fullscreen
    SCREEN_WIDTH, SCREEN_HEIGHT = w, h
    is_fullscreen = fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

generate_random_map()

# 玩家屬性與狀態
player_max_hp = 100
player_hp = 100
player_level = 1
player_exp = 0

player_pos = [WORLD_WIDTH // 2, WORLD_HEIGHT // 2]
player_speed = 6
player_radius = 16
fov_angle, fov_distance = 80, 480

weapon_slots = [create_weapon("pistol"), None]
active_slot_idx = 0

current_spread = weapon_slots[active_slot_idx]["spread_min"]
last_shot_time = 0
is_reloading = False
reload_start_time = 0

last_dynamic_spawn_check = 0
last_enemy_spawn_check = 0
last_map_regen_time = 0

hud_notification = ""
notification_timer = 0
bullets = []  # [x, y, dx, dy, speed, damage, penetrated_set, decay, is_enemy_bullet]

# --- 經驗值與等級系統邏輯 ---
def get_required_exp(level):
    """ 計算當前等級升到下一級所需的總經驗值（等級越高升級越慢） """
    return int(100 * (level ** 1.5))

def add_player_exp(amount):
    """ 為玩家增加經驗值，並處理連續升級邏輯 """
    global player_level, player_exp
    player_exp += amount
    req_exp = get_required_exp(player_level)
    while player_exp >= req_exp:
        player_exp -= req_exp
        player_level += 1
        show_notification(LANGUAGES[current_lang]["level_up"].format(level=player_level))
        req_exp = get_required_exp(player_level)

def respawn_player():
    global player_hp, player_pos, weapon_slots, active_slot_idx, is_reloading, game_state, bullets, enemies, loot_drops, player_level, player_exp
    player_hp = player_max_hp
    player_level = 1
    player_exp = 0
    player_pos = [WORLD_WIDTH // 2, WORLD_HEIGHT // 2]
    weapon_slots = [create_weapon("pistol"), None]
    active_slot_idx = 0
    is_reloading = False
    game_state = "PLAYING"
    bullets.clear()
    loot_drops.clear()
    enemies.clear()
    spawn_harassment_enemies_safely(player_pos)
    show_notification("任務重置，玩家已在中央區域重生！")

def check_line_of_sight(p1, p2):
    all_walls = solid_walls + penetrable_walls + [d["rect"] for d in destructible_walls]
    for wall in all_walls:
        if wall.clipline(p1, p2):
            return False
    return True

def check_in_fov(p_pos, facing_deg, e_pos, fov_deg, fov_dist):
    dx, dy = e_pos[0] - p_pos[0], e_pos[1] - p_pos[1]
    dist = math.hypot(dx, dy)
    if dist > fov_dist:
        return False
    angle_to_e = math.degrees(math.atan2(dy, dx))
    diff = (angle_to_e - facing_deg + 180) % 360 - 180
    if abs(diff) > fov_deg / 2:
        return False
    return check_line_of_sight(p_pos, e_pos)

def show_notification(text):
    global hud_notification, notification_timer
    hud_notification = text
    notification_timer = pygame.time.get_ticks() + 3000

def maintain_pistol_rules():
    has_pistol = any(w and w["id"] == "pistol" for w in weapon_slots)
    if not has_pistol:
        for i in range(2):
            if weapon_slots[i] is None:
                weapon_slots[i] = create_weapon("pistol")
                show_notification(LANGUAGES[current_lang]["auto_pistol"])
                break

def check_weapon_depletion():
    global is_reloading, active_slot_idx
    cur_w = weapon_slots[active_slot_idx]
    if cur_w and cur_w["id"] != "pistol" and cur_w["current_ammo"] <= 0 and cur_w["reserve_ammo"] <= 0:
        w_name = LANGUAGES[current_lang]["weapons"].get(cur_w["id"], cur_w["name"])
        show_notification(LANGUAGES[current_lang]["weapon_depleted"].format(weapon=w_name))
        
        weapon_slots[active_slot_idx] = None
        is_reloading = False

        has_pistol = any(w and w["id"] == "pistol" for w in weapon_slots)
        if has_pistol:
            for i, w in enumerate(weapon_slots):
                if w is not None:
                    active_slot_idx = i
                    break
        else:
            maintain_pistol_rules()

def update_dynamic_weapon_spawning(current_time):
    global last_dynamic_spawn_check
    has_special_weapon = any(w and w["id"] in ["shotgun", "sniper"] for w in weapon_slots)
    GROUND_DETECT_RADIUS = 400
    has_ground_weapon_nearby = any(
        math.hypot(gw["x"] - player_pos[0], gw["y"] - player_pos[1]) < GROUND_DETECT_RADIUS
        for gw in ground_weapons
    )

    current_interval = 60000 if (has_special_weapon or has_ground_weapon_nearby) else 20000
    if current_time - last_dynamic_spawn_check < current_interval: return

    last_dynamic_spawn_check = current_time

    for _ in range(10):
        angle = random.uniform(0, math.tau)
        dist = random.uniform(200, 450)
        candidate_x = player_pos[0] + math.cos(angle) * dist
        candidate_y = player_pos[1] + math.sin(angle) * dist

        if not (40 <= candidate_x <= WORLD_WIDTH - 40 and 40 <= candidate_y <= WORLD_HEIGHT - 40): continue
        if math.hypot(candidate_x - player_pos[0], candidate_y - player_pos[1]) < 120: continue

        cand_rect = pygame.Rect(candidate_x - 18, candidate_y - 18, 36, 36)
        if any(cand_rect.colliderect(w) for w in solid_walls + penetrable_walls): continue
        if any(cand_rect.colliderect(d["rect"]) for d in destructible_walls): continue

        w_type = random.choice(["shotgun", "sniper"])
        ground_weapons.append({"type": w_type, "x": candidate_x, "y": candidate_y})
        w_name = LANGUAGES[current_lang]["weapons"].get(w_type, w_type)
        show_notification(LANGUAGES[current_lang]["dynamic_drop"].format(weapon=w_name))
        break

def update_dynamic_map_regeneration(current_time):
    global last_map_regen_time, structures, scattered_covers

    MAP_REGEN_INTERVAL = 30000
    SAFE_DISTANCE = 1300

    if current_time - last_map_regen_time < MAP_REGEN_INTERVAL: return
    last_map_regen_time = current_time

    structures = [
        s for s in structures 
        if math.hypot(s["center"][0] - player_pos[0], s["center"][1] - player_pos[1]) <= SAFE_DISTANCE
    ]
    scattered_covers = [
        c for c in scattered_covers 
        if math.hypot(c["rect"].centerx - player_pos[0], c["rect"].centery - player_pos[1]) <= SAFE_DISTANCE
    ]

    grid_cols, grid_rows = 4, 3
    cell_w, cell_h = WORLD_WIDTH // grid_cols, WORLD_HEIGHT // grid_rows

    for col in range(grid_cols):
        for row in range(grid_rows):
            cell_rect = pygame.Rect(col * cell_w + 40, row * cell_h + 40, cell_w - 80, cell_h - 80)
            if math.hypot(cell_rect.centerx - player_pos[0], cell_rect.centery - player_pos[1]) > SAFE_DISTANCE:
                cell_structs = sum(1 for s in structures if cell_rect.colliderect(s["rect"]))
                if cell_structs < 2:
                    prefab = random.choice(PREFABS)
                    pw, ph = prefab["width"], prefab["height"]
                    for _ in range(10):
                        rx = random.randint(cell_rect.left, max(cell_rect.left + 1, cell_rect.right - pw))
                        ry = random.randint(cell_rect.top, max(cell_rect.top + 1, cell_rect.bottom - ph))
                        cand_rect = pygame.Rect(rx - 30, ry - 30, pw + 60, ph + 60)
                        if not any(cand_rect.colliderect(s["rect"]) for s in structures):
                            structures.append(create_structure(prefab, rx, ry))
                            break

                    for _ in range(2):
                        cx = random.randint(cell_rect.left, cell_rect.right - 40)
                        cy = random.randint(cell_rect.top, cell_rect.bottom - 40)
                        c_rect = pygame.Rect(cx, cy, 40, 40)
                        if not any(c_rect.colliderect(s["rect"]) for s in structures):
                            scattered_covers.append({"rect": c_rect, "hp": 80, "max_hp": 80, "type": 'destructible'})

    rebuild_collision_lists()

def move_enemy_with_collision(enemy, dx, dy, obstacle_rects):
    """ 處理敵人的分軸牆壁碰撞，避免穿牆 """
    r = enemy["radius"]
    if dx != 0:
        enemy["x"] += dx
        e_rect = pygame.Rect(enemy["x"] - r, enemy["y"] - r, r * 2, r * 2)
        for wall in obstacle_rects:
            if e_rect.colliderect(wall):
                if dx > 0: enemy["x"] = wall.left - r
                elif dx < 0: enemy["x"] = wall.right + r
                e_rect.x = enemy["x"] - r

    if dy != 0:
        enemy["y"] += dy
        e_rect = pygame.Rect(enemy["x"] - r, enemy["y"] - r, r * 2, r * 2)
        for wall in obstacle_rects:
            if e_rect.colliderect(wall):
                if dy > 0: enemy["y"] = wall.top - r
                elif dy < 0: enemy["y"] = wall.bottom + r
                e_rect.y = enemy["y"] - r

def update_enemies(facing_angle, current_time):
    global player_hp, game_state, last_enemy_spawn_check

    if game_state != "PLAYING": return

    if current_time - last_enemy_spawn_check > 8000:
        last_enemy_spawn_check = current_time
        spawn_harassment_enemies_safely(player_pos)

    all_obstacle_rects = solid_walls + penetrable_walls + [d["rect"] for d in destructible_walls]

    for enemy in enemies[:]:
        dist_to_player = math.hypot(player_pos[0] - enemy["x"], player_pos[1] - enemy["y"])

        if dist_to_player > 1600:
            enemies.remove(enemy)
            continue

        # 1. 視野與小地圖 LKP 標記
        is_in_view = check_in_fov(player_pos, facing_angle, (enemy["x"], enemy["y"]), fov_angle, fov_distance)
        enemy["is_visible"] = is_in_view
        if is_in_view:
            enemy["last_known_pos"] = (enemy["x"], enemy["y"])

        # 2. 仇恨引發與脫離機制
        if not enemy["is_aggro"]:
            if dist_to_player <= enemy["aggro_range"] and (is_in_view or dist_to_player < 220):
                enemy["is_aggro"] = True
        else:
            if dist_to_player > enemy["max_chase_dist"]:
                enemy["is_aggro"] = False

        # 3. AI 移動
        if enemy["is_aggro"]:
            dir_x = (player_pos[0] - enemy["x"]) / dist_to_player if dist_to_player > 0 else 0
            dir_y = (player_pos[1] - enemy["y"]) / dist_to_player if dist_to_player > 0 else 0

            if enemy["type"] == "melee":
                dx = dir_x * enemy["speed"]
                dy = dir_y * enemy["speed"]
                move_enemy_with_collision(enemy, dx, dy, all_obstacle_rects)

            elif enemy["type"] == "ranged":
                dx, dy = 0, 0
                if dist_to_player > 300:
                    dx, dy = dir_x * enemy["speed"], dir_y * enemy["speed"]
                elif dist_to_player < 180:
                    dx, dy = -dir_x * enemy["speed"], -dir_y * enemy["speed"]

                if dx != 0 or dy != 0:
                    move_enemy_with_collision(enemy, dx, dy, all_obstacle_rects)

                if dist_to_player <= 420 and check_line_of_sight((enemy["x"], enemy["y"]), player_pos):
                    if current_time - enemy["last_attack"] >= enemy["attack_cd"]:
                        enemy["last_attack"] = current_time
                        angle = math.atan2(player_pos[1] - enemy["y"], player_pos[0] - enemy["x"])
                        b_speed = 11.0
                        bullets.append([
                            enemy["x"], enemy["y"], math.cos(angle) * b_speed, math.sin(angle) * b_speed,
                            b_speed, enemy["damage"], set(), 0.5, True
                        ])

        # 4. 修正：敵人與玩家的硬體碰撞推開（防止重疊）與碰撞傷害
        updated_dist = math.hypot(player_pos[0] - enemy["x"], player_pos[1] - enemy["y"])
        min_dist = player_radius + enemy["radius"]
        if updated_dist < min_dist:
            if updated_dist > 0:
                overlap = min_dist - updated_dist
                nx = (enemy["x"] - player_pos[0]) / updated_dist
                ny = (enemy["y"] - player_pos[1]) / updated_dist
                enemy["x"] += nx * overlap
                enemy["y"] += ny * overlap
            else:
                enemy["x"] += min_dist

            # 被推開後再次檢查牆壁碰撞，避免被推入牆內
            move_enemy_with_collision(enemy, 0, 0, all_obstacle_rects)

            # 近戰敵人碰觸玩家產生碰撞傷害
            if enemy["type"] == "melee":
                if current_time - enemy["last_attack"] >= enemy["attack_cd"]:
                    enemy["last_attack"] = current_time
                    player_hp -= enemy["damage"]
                    if player_hp <= 0:
                        player_hp = 0
                        game_state = "DEAD"

def start_reload():
    global is_reloading, reload_start_time
    if is_reloading: return
    cur_w = weapon_slots[active_slot_idx]
    if cur_w and cur_w["current_ammo"] < cur_w["clip_size"] and cur_w["reserve_ammo"] > 0:
        is_reloading = True
        reload_start_time = pygame.time.get_ticks()

def finish_reload():
    global is_reloading
    cur_w = weapon_slots[active_slot_idx]
    if not cur_w: return
    needed = cur_w["clip_size"] - cur_w["current_ammo"]
    if cur_w["reserve_ammo"] == float('inf'):
        cur_w["current_ammo"] = cur_w["clip_size"]
    else:
        reload_amount = min(needed, cur_w["reserve_ammo"])
        cur_w["current_ammo"] += reload_amount
        cur_w["reserve_ammo"] -= reload_amount

    is_reloading = False
    check_weapon_depletion()

def shoot_active_weapon(target_world_x, target_world_y, gun_tip_x, gun_tip_y):
    global last_shot_time, current_spread
    current_time = pygame.time.get_ticks()
    cur_w = weapon_slots[active_slot_idx]

    if not cur_w or is_reloading or current_time - last_shot_time < cur_w["fire_rate"]: return

    if cur_w["current_ammo"] <= 0:
        if cur_w["reserve_ammo"] > 0: start_reload()
        else: check_weapon_depletion()
        return

    cur_w["current_ammo"] -= 1
    last_shot_time = current_time
    current_spread = min(cur_w["spread_max"], current_spread + cur_w["recoil_per_shot"])
    base_angle = math.atan2(target_world_y - gun_tip_y, target_world_x - gun_tip_x)

    pellet_count = cur_w.get("pellets", 1)
    for _ in range(pellet_count):
        offset_rad = math.radians(random.uniform(-current_spread, current_spread))
        final_angle = base_angle + offset_rad
        b_speed = cur_w["bullet_speed"]
        b_dx = math.cos(final_angle) * b_speed
        b_dy = math.sin(final_angle) * b_speed
        bullets.append([
            gun_tip_x, gun_tip_y, b_dx, b_dy, b_speed,
            cur_w["base_damage"], set(), cur_w["pen_decay"], False
        ])

    if cur_w["current_ammo"] == 0 and cur_w["reserve_ammo"] == 0:
        check_weapon_depletion()

def get_tab_rects(center_x):
    tab_keys = ["video", "general", "keybinds", "audio"]
    return [(key, pygame.Rect(center_x - 220 + i * 110, 120, 100, 35)) for i, key in enumerate(tab_keys)]

def draw_weapon_icon(surface, x, y, w_id):
    if w_id == "pistol":
        pygame.draw.rect(surface, WHITE, (x, y + 5, 24, 7), border_radius=1)
        pygame.draw.polygon(surface, WHITE, [(x + 5, y + 12), (x + 12, y + 12), (x + 9, y + 21), (x + 3, y + 21)])
    elif w_id == "shotgun":
        pygame.draw.rect(surface, (220, 180, 100), (x, y + 6, 32, 6), border_radius=1)
        pygame.draw.rect(surface, (140, 90, 40), (x + 6, y + 12, 12, 8), border_radius=1)
    elif w_id == "sniper":
        pygame.draw.rect(surface, (180, 200, 220), (x - 4, y + 6, 38, 5), border_radius=1)
        pygame.draw.rect(surface, (50, 50, 50), (x + 10, y + 2, 10, 4), border_radius=1)
        pygame.draw.rect(surface, (120, 120, 120), (x + 4, y + 11, 8, 10), border_radius=1)

def draw_held_weapon(surface, hand_x, hand_y, facing_rad, weapon_id):
    if not weapon_id: return

    fwd_x, fwd_y = math.cos(facing_rad), math.sin(facing_rad)
    perp_x, perp_y = -math.sin(facing_rad), math.cos(facing_rad)

    if weapon_id == "pistol":
        tip_x, tip_y = hand_x + fwd_x * 14, hand_y + fwd_y * 14
        pygame.draw.line(surface, (180, 190, 200), (hand_x, hand_y), (tip_x, tip_y), 4)
        pygame.draw.line(surface, (60, 60, 70), (hand_x, hand_y), (hand_x + fwd_x * 6, hand_y + fwd_y * 6), 5)
    elif weapon_id == "shotgun":
        tip_x, tip_y = hand_x + fwd_x * 24, hand_y + fwd_y * 24
        pygame.draw.line(surface, (130, 80, 30), (hand_x - fwd_x * 4, hand_y - fwd_y * 4), (hand_x + fwd_x * 4, hand_y + fwd_y * 4), 6)
        pygame.draw.line(surface, (80, 85, 95), (hand_x + fwd_x * 2, hand_y + fwd_y * 2), (tip_x, tip_y), 5)
        pump_x, pump_y = hand_x + fwd_x * 10, hand_y + fwd_y * 10
        pygame.draw.line(surface, (100, 60, 20), (pump_x, pump_y), (pump_x + fwd_x * 6, pump_y + fwd_y * 6), 7)
    elif weapon_id == "sniper":
        tip_x, tip_y = hand_x + fwd_x * 34, hand_y + fwd_y * 34
        pygame.draw.line(surface, (50, 55, 65), (hand_x - fwd_x * 4, hand_y - fwd_y * 4), (tip_x, tip_y), 4)
        sc_x, sc_y = hand_x + fwd_x * 10 + perp_x * 3, hand_y + fwd_y * 10 + perp_y * 3
        pygame.draw.line(surface, (30, 30, 35), (sc_x - fwd_x * 5, sc_y - fwd_y * 5), (sc_x + fwd_x * 5, sc_y + fwd_y * 5), 5)
        pygame.draw.line(surface, (200, 200, 210), (tip_x - fwd_x * 4, tip_y - fwd_y * 4), (tip_x, tip_y), 6)

def update_minimap_memory():
    px_mini = player_pos[0] * scale_x
    py_mini = player_pos[1] * scale_y
    vision_radius = 28
    vision_radius_world_x = vision_radius / scale_x
    vision_radius_world_y = vision_radius / scale_y
    margin = 30

    vision_rect = pygame.Rect(
        player_pos[0] - vision_radius_world_x - margin,
        player_pos[1] - vision_radius_world_y - margin,
        (vision_radius_world_x + margin) * 2,
        (vision_radius_world_y + margin) * 2
    )

    clip_area = pygame.Rect(px_mini - vision_radius, py_mini - vision_radius, vision_radius * 2, vision_radius * 2)
    static_minimap.set_clip(clip_area)

    pygame.draw.circle(static_minimap, COLOR_MINIMAP_BG, (int(px_mini), int(py_mini)), vision_radius)

    for wall in solid_walls:
        if vision_rect.colliderect(wall):
            pygame.draw.rect(static_minimap, COLOR_SOLID, (wall.x * scale_x, wall.y * scale_y, max(1, wall.width * scale_x), max(1, wall.height * scale_y)))

    for wall in penetrable_walls:
        if vision_rect.colliderect(wall):
            pygame.draw.rect(static_minimap, COLOR_PENETRABLE, (wall.x * scale_x, wall.y * scale_y, max(1, wall.width * scale_x), max(1, wall.height * scale_y)))

    for d_wall in destructible_walls:
        w = d_wall["rect"]
        if vision_rect.colliderect(w):
            pygame.draw.rect(static_minimap, COLOR_DESTRUCTIBLE, (w.x * scale_x, w.y * scale_y, max(1, w.width * scale_x), max(1, w.height * scale_y)))

    static_minimap.set_clip(None)

# 主迴圈
running = True
while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    raw_mouse_pos = pygame.mouse.get_pos()
    scale_factor_x, scale_factor_y = VIRTUAL_WIDTH / SCREEN_WIDTH, VIRTUAL_HEIGHT / SCREEN_HEIGHT
    virtual_mouse_x, virtual_mouse_y = raw_mouse_pos[0] * scale_factor_x, raw_mouse_pos[1] * scale_factor_y
    virtual_mouse_pos = (virtual_mouse_x, virtual_mouse_y)

    center_screen = (VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2)
    facing_angle = math.degrees(math.atan2(virtual_mouse_y - center_screen[1], virtual_mouse_x - center_screen[0]))

    lang_dict = LANGUAGES[current_lang]

    # --- A. 事件處理 ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.VIDEORESIZE and not is_fullscreen:
            SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
        elif event.type == pygame.KEYDOWN:
            if binding_key_target:
                KEYBINDS[binding_key_target] = event.key
                binding_key_target = None
                continue
            if event.key == KEYBINDS["pause"]:
                if game_state in ["PLAYING", "PAUSED"]:
                    game_state = "PAUSED" if game_state == "PLAYING" else "PLAYING"
                    binding_key_target = None
            elif event.key == KEYBINDS["fullscreen"]:
                is_fullscreen = not is_fullscreen
                set_display_mode(SCREEN_WIDTH, SCREEN_HEIGHT, is_fullscreen)
            elif game_state == "DEAD":
                if event.key == KEYBINDS["reload"]:
                    respawn_player()
            elif game_state == "PLAYING":
                if event.key == KEYBINDS["weapon_1"]:
                    active_slot_idx = 0
                    is_reloading = False
                elif event.key == KEYBINDS["weapon_2"]:
                    active_slot_idx = 1
                    is_reloading = False
                elif event.key == KEYBINDS["reload"]:
                    start_reload()
                elif event.key == KEYBINDS["interact"]:
                    nearest_dist = 60
                    target_gw = None
                    for gw in ground_weapons:
                        dist = math.hypot(player_pos[0] - gw["x"], player_pos[1] - gw["y"])
                        if dist < nearest_dist:
                            nearest_dist = dist
                            target_gw = gw

                    if target_gw:
                        weapon_slots[active_slot_idx] = create_weapon(target_gw["type"])
                        ground_weapons.remove(target_gw)
                        is_reloading = False
                        maintain_pistol_rules()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "PAUSED":
                center_x = VIRTUAL_WIDTH // 2
                if binding_key_target: binding_key_target = None; continue
                tab_rects = get_tab_rects(center_x)
                tab_clicked = False
                for tab_key, tab_rect in tab_rects:
                    if tab_rect.collidepoint(virtual_mouse_pos):
                        current_tab = tab_key
                        tab_clicked = True
                        break
                if tab_clicked: continue

                if current_tab == "video":
                    if pygame.Rect(center_x - 170, 200, 340, 45).collidepoint(virtual_mouse_pos) and not is_fullscreen:
                        current_res_idx = (current_res_idx + 1) % len(RESOLUTIONS)
                        rw, rh = RESOLUTIONS[current_res_idx]
                        set_display_mode(rw, rh, False)
                    elif pygame.Rect(center_x - 170, 260, 340, 45).collidepoint(virtual_mouse_pos):
                        is_fullscreen = not is_fullscreen
                        set_display_mode(SCREEN_WIDTH, SCREEN_HEIGHT, is_fullscreen)
                elif current_tab == "general":
                    if pygame.Rect(center_x - 170, 200, 340, 45).collidepoint(virtual_mouse_pos):
                        current_lang = "en" if current_lang == "zh" else "zh"
                elif current_tab == "keybinds":
                    for i, k in enumerate(list(KEYBINDS.keys())):
                        btn_y = 175 + i * 38
                        if pygame.Rect(center_x - 200, btn_y, 400, 32).collidepoint(virtual_mouse_pos):
                            binding_key_target = k

                if pygame.Rect(center_x - 170, 490, 160, 45).collidepoint(virtual_mouse_pos): game_state = "PLAYING"
                elif pygame.Rect(center_x + 10, 490, 160, 45).collidepoint(virtual_mouse_pos): running = False

    # --- B. 邏輯更新 ---
    if game_state == "PLAYING":
        update_dynamic_weapon_spawning(current_time)
        update_dynamic_map_regeneration(current_time)
        update_enemies(facing_angle, current_time)

        cur_weapon = weapon_slots[active_slot_idx]
        if is_reloading and cur_weapon and current_time - reload_start_time >= cur_weapon["reload_time"]:
            finish_reload()

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[KEYBINDS["move_left"]]: dx -= player_speed
        if keys[KEYBINDS["move_right"]]: dx += player_speed
        if keys[KEYBINDS["move_up"]]: dy -= player_speed
        if keys[KEYBINDS["move_down"]]: dy += player_speed

        is_moving = (dx != 0 or dy != 0)
        if dx != 0 and dy != 0: dx *= 0.7071; dy *= 0.7071

        all_obstacle_rects = solid_walls + penetrable_walls + [d["rect"] for d in destructible_walls]

        player_pos[0] += dx
        player_rect = pygame.Rect(player_pos[0] - player_radius, player_pos[1] - player_radius, player_radius * 2, player_radius * 2)
        for wall in all_obstacle_rects:
            if player_rect.colliderect(wall):
                if dx > 0: player_pos[0] = wall.left - player_radius
                elif dx < 0: player_pos[0] = wall.right + player_radius
                player_rect.x = player_pos[0] - player_radius

        player_pos[1] += dy
        player_rect = pygame.Rect(player_pos[0] - player_radius, player_pos[1] - player_radius, player_radius * 2, player_radius * 2)
        for wall in all_obstacle_rects:
            if player_rect.colliderect(wall):
                if dy > 0: player_pos[1] = wall.top - player_radius
                elif dy < 0: player_pos[1] = wall.bottom + player_radius
                player_rect.y = player_pos[1] - player_radius

        # 拾取戰術經驗/補給包
        for loot in loot_drops[:]:
            loot_rect = pygame.Rect(loot[0] - 12, loot[1] - 12, 24, 24)
            if player_rect.colliderect(loot_rect):
                loot_drops.remove(loot)
                player_hp = min(player_max_hp, player_hp + 25)
                cur_w = weapon_slots[active_slot_idx]
                if cur_w and cur_w["reserve_ammo"] != float('inf'):
                    cur_w["reserve_ammo"] += cur_w["clip_size"] * 2
                show_notification(lang_dict["loot_picked"])

        if cur_weapon:
            target_spread = cur_weapon["spread_max"] if is_moving else cur_weapon["spread_min"]
            current_spread += (target_spread - current_spread) * 0.1

        facing_rad = math.radians(facing_angle)
        gun_x_screen = center_screen[0] + 22 * math.cos(facing_rad) + 12 * math.cos(facing_rad + math.pi / 2)
        gun_y_screen = center_screen[1] + 22 * math.sin(facing_rad) + 12 * math.sin(facing_rad + math.pi / 2)

        cur_w_id = cur_weapon["id"] if cur_weapon else None
        barrel_len = 14
        if cur_w_id == "shotgun": barrel_len = 24
        elif cur_w_id == "sniper": barrel_len = 34

        gun_tip_x_screen = gun_x_screen + barrel_len * math.cos(facing_rad)
        gun_tip_y_screen = gun_y_screen + barrel_len * math.sin(facing_rad)

        gun_tip_world_x = player_pos[0] + (gun_tip_x_screen - center_screen[0])
        gun_tip_world_y = player_pos[1] + (gun_tip_y_screen - center_screen[1])

        # 修正：檢測槍口是否插進牆體，若插牆則將開槍點縮回牆外
        shoot_x, shoot_y = gun_tip_world_x, gun_tip_world_y
        ray_start = (player_pos[0], player_pos[1])
        ray_end = (gun_tip_world_x, gun_tip_world_y)
        max_dist = math.hypot(gun_tip_world_x - player_pos[0], gun_tip_world_y - player_pos[1])

        if max_dist > 0:
            for wall in all_obstacle_rects:
                clip = wall.clipline(ray_start, ray_end)
                if clip:
                    d1 = math.hypot(clip[0][0] - ray_start[0], clip[0][1] - ray_start[1])
                    d2 = math.hypot(clip[1][0] - ray_start[0], clip[1][1] - ray_start[1])
                    hit_dist = min(d1, d2)
                    if hit_dist < max_dist:
                        ratio = max(0.0, (hit_dist - 2) / max_dist)
                        shoot_x = ray_start[0] + (gun_tip_world_x - ray_start[0]) * ratio
                        shoot_y = ray_start[1] + (gun_tip_world_y - ray_start[1]) * ratio
                        max_dist = hit_dist

        if pygame.mouse.get_pressed()[0] and cur_weapon:
            world_mouse_x = player_pos[0] + (virtual_mouse_x - center_screen[0])
            world_mouse_y = player_pos[1] + (virtual_mouse_y - center_screen[1])
            shoot_active_weapon(world_mouse_x, world_mouse_y, shoot_x, shoot_y)

        # 彈道與碰撞處理
        for bullet in bullets[:]:
            bullet[0] += bullet[2]
            bullet[1] += bullet[3]
            bullet_rect = pygame.Rect(bullet[0] - 3, bullet[1] - 3, 6, 6)
            is_enemy_bullet = bullet[8]

            if any(bullet_rect.colliderect(w) for w in solid_walls) or not (0 <= bullet[0] <= WORLD_WIDTH and 0 <= bullet[1] <= WORLD_HEIGHT):
                bullets.remove(bullet)
                continue

            # 敵方子彈擊中玩家
            if is_enemy_bullet:
                if bullet_rect.colliderect(player_rect):
                    player_hp -= bullet[5]
                    if bullet in bullets: bullets.remove(bullet)
                    if player_hp <= 0:
                        player_hp = 0
                        game_state = "DEAD"
                    continue

            # 玩家子彈擊中敵人/中立單位
            else:
                for enemy in enemies[:]:
                    e_rect = pygame.Rect(enemy["x"] - enemy["radius"], enemy["y"] - enemy["radius"], enemy["radius"] * 2, enemy["radius"] * 2)
                    if bullet_rect.colliderect(e_rect):
                        enemy["hp"] -= bullet[5]
                        enemy["is_aggro"] = True
                        if bullet in bullets: bullets.remove(bullet)

                        if enemy["hp"] <= 0:
                            # 擊殺單位獎勵經驗值
                            add_player_exp(enemy.get("exp_reward", 30))
                            loot_drops.append((enemy["x"], enemy["y"]))
                            enemies.remove(enemy)
                        break

            for i, p_wall in enumerate(penetrable_walls):
                if bullet_rect.colliderect(p_wall) and i not in bullet[6]:
                    bullet[6].add(i)
                    decay = bullet[7]
                    bullet[2] *= decay
                    bullet[3] *= decay
                    bullet[5] *= (decay - 0.1)

            for d_wall in destructible_walls[:]:
                if bullet_rect.colliderect(d_wall["rect"]):
                    d_wall["hp"] -= bullet[5]
                    if d_wall["hp"] <= 0: 
                        destructible_walls.remove(d_wall)
                        rebuild_collision_lists()
                    if bullet in bullets: bullets.remove(bullet)
                    break

        update_minimap_memory()

    # --- C. 畫面繪製 ---
    cam_x = player_pos[0] - VIRTUAL_WIDTH // 2
    cam_y = player_pos[1] - VIRTUAL_HEIGHT // 2

    game_canvas.fill(TACTICAL_GROUND)

    # 地面格紋
    grid_size = 100
    for x in range(int(-cam_x % grid_size), VIRTUAL_WIDTH, grid_size):
        pygame.draw.line(game_canvas, GRID_COLOR, (x, 0), (x, VIRTUAL_HEIGHT))
    for y in range(int(-cam_y % grid_size), VIRTUAL_HEIGHT, grid_size):
        pygame.draw.line(game_canvas, GRID_COLOR, (0, y), (VIRTUAL_WIDTH, y))

    # 地面武器
    near_ground_weapon = None
    for gw in ground_weapons:
        gx_scr, gy_scr = gw["x"] - cam_x, gw["y"] - cam_y
        if -40 <= gx_scr <= VIRTUAL_WIDTH + 40 and -40 <= gy_scr <= VIRTUAL_HEIGHT + 40:
            pygame.draw.circle(game_canvas, (60, 80, 110), (int(gx_scr), int(gy_scr)), 18)
            pygame.draw.circle(game_canvas, YELLOW, (int(gx_scr), int(gy_scr)), 18, 2)
            draw_weapon_icon(game_canvas, gx_scr - 12, gy_scr - 10, gw["type"])
            if math.hypot(player_pos[0] - gw["x"], player_pos[1] - gw["y"]) < 60:
                near_ground_weapon = gw

    # 擊殺掉落的經驗/補給包
    for lx, ly in loot_drops:
        lx_scr, ly_scr = lx - cam_x, ly - cam_y
        if -20 <= lx_scr <= VIRTUAL_WIDTH + 20 and -20 <= ly_scr <= VIRTUAL_HEIGHT + 20:
            pygame.draw.rect(game_canvas, GREEN, (lx_scr - 8, ly_scr - 8, 16, 16), border_radius=3)
            pygame.draw.rect(game_canvas, WHITE, (lx_scr - 8, ly_scr - 8, 16, 16), 2, border_radius=3)
            pygame.draw.line(game_canvas, WHITE, (lx_scr - 4, ly_scr), (lx_scr + 4, ly_scr), 2)
            pygame.draw.line(game_canvas, WHITE, (lx_scr, ly_scr - 4), (lx_scr, ly_scr + 4), 2)

    # 牆壁
    for wall in solid_walls: pygame.draw.rect(game_canvas, COLOR_SOLID, pygame.Rect(wall.x - cam_x, wall.y - cam_y, wall.width, wall.height))
    for wall in penetrable_walls: pygame.draw.rect(game_canvas, COLOR_PENETRABLE, pygame.Rect(wall.x - cam_x, wall.y - cam_y, wall.width, wall.height))
    for d_wall in destructible_walls:
        w_rect = d_wall["rect"]
        draw_r = pygame.Rect(w_rect.x - cam_x, w_rect.y - cam_y, w_rect.width, w_rect.height)
        pygame.draw.rect(game_canvas, COLOR_DESTRUCTIBLE, draw_r)
        pygame.draw.rect(game_canvas, WHITE, draw_r, 1)
        hp_pct = max(0, d_wall["hp"] / d_wall["max_hp"])
        pygame.draw.rect(game_canvas, RED, (draw_r.x, draw_r.y - 6, draw_r.width, 4))
        pygame.draw.rect(game_canvas, (50, 220, 50), (draw_r.x, draw_r.y - 6, int(draw_r.width * hp_pct), 4))

    # 中立單位/騷擾怪 (視野內繪製)
    for enemy in enemies:
        if enemy["is_visible"]:
            ex_scr, ey_scr = enemy["x"] - cam_x, enemy["y"] - cam_y
            e_color = (230, 100, 30) if enemy["type"] == "melee" else (220, 160, 40)
            pygame.draw.circle(game_canvas, e_color, (int(ex_scr), int(ey_scr)), enemy["radius"])
            
            border_col = RED if enemy["is_aggro"] else WHITE
            pygame.draw.circle(game_canvas, border_col, (int(ex_scr), int(ey_scr)), enemy["radius"], 2)

            ehp_pct = max(0, enemy["hp"] / enemy["max_hp"])
            pygame.draw.rect(game_canvas, RED, (ex_scr - 14, ey_scr - 20, 28, 4))
            pygame.draw.rect(game_canvas, (50, 220, 50), (ex_scr - 14, ey_scr - 20, int(28 * ehp_pct), 4))

    # 子彈
    for bullet in bullets:
        bullet_color = RED if bullet[8] else ((255, 120, 50) if len(bullet[6]) > 0 else YELLOW)
        pygame.draw.circle(game_canvas, bullet_color, (int(bullet[0] - cam_x), int(bullet[1] - cam_y)), 3)

    # 玩家與持槍
    if game_state != "DEAD":
        pygame.draw.circle(game_canvas, BLUE, center_screen, player_radius)
        cur_w = weapon_slots[active_slot_idx]
        if cur_w:
            draw_held_weapon(game_canvas, gun_x_screen, gun_y_screen, facing_rad, cur_w["id"])
        pygame.draw.circle(game_canvas, BLUE, (int(gun_x_screen), int(gun_y_screen)), 4)

    # 視野迷霧 (Raycasting 動態牆壁遮擋)
    darkness.fill((10, 10, 15))
    fov_points = [center_screen]
    left_a = math.radians(facing_angle - fov_angle / 2)
    right_a = math.radians(facing_angle + fov_angle / 2)
    num_rays = 90
    all_obstacle_rects = solid_walls + penetrable_walls + [d["rect"] for d in destructible_walls]

    for i in range(num_rays + 1):
        mid_a = left_a + (right_a - left_a) * (i / num_rays)
        cos_a = math.cos(mid_a)
        sin_a = math.sin(mid_a)

        p1 = player_pos
        p2 = (player_pos[0] + fov_distance * cos_a, player_pos[1] + fov_distance * sin_a)

        closest_dist = fov_distance
        for wall in all_obstacle_rects:
            clip = wall.clipline(p1, p2)
            if clip:
                d1 = math.hypot(clip[0][0] - p1[0], clip[0][1] - p1[1])
                d2 = math.hypot(clip[1][0] - p1[0], clip[1][1] - p1[1])
                d = min(d1, d2)
                if d < closest_dist:
                    closest_dist = d

        fov_points.append((center_screen[0] + closest_dist * cos_a, center_screen[1] + closest_dist * sin_a))

    pygame.draw.polygon(darkness, (0, 255, 0), fov_points)
    game_canvas.blit(darkness, (0, 0))

    # 小地圖繪製
    minimap_x, minimap_y = VIRTUAL_WIDTH - MINIMAP_WIDTH - 20, 20
    game_canvas.blit(static_minimap, (minimap_x, minimap_y))

    # 小地圖中立單位 (琥珀橘標籤 / LKP)
    for enemy in enemies:
        if enemy["is_visible"]:
            em_x = minimap_x + enemy["x"] * scale_x
            em_y = minimap_y + enemy["y"] * scale_y
            pygame.draw.circle(game_canvas, COLOR_NEUTRAL_MINIMAP_VISIBLE, (int(em_x), int(em_y)), 3)
        elif enemy["last_known_pos"] is not None:
            lkp_x = minimap_x + enemy["last_known_pos"][0] * scale_x
            lkp_y = minimap_y + enemy["last_known_pos"][1] * scale_y
            pygame.draw.circle(game_canvas, COLOR_NEUTRAL_MINIMAP_LKP, (int(lkp_x), int(lkp_y)), 3, 1)

    pygame.draw.rect(game_canvas, WHITE, (minimap_x, minimap_y, MINIMAP_WIDTH, MINIMAP_HEIGHT), 2)
    px_m, py_m = int(minimap_x + player_pos[0] * scale_x), int(minimap_y + player_pos[1] * scale_y)
    pygame.draw.circle(game_canvas, (100, 200, 255), (px_m, py_m), 28, 1)
    pygame.draw.circle(game_canvas, BLUE, (px_m, py_m), 3)

    # 玩家 HP UI
    pygame.draw.rect(game_canvas, (40, 40, 50), (20, 50, 200, 16), border_radius=4)
    hp_ratio = player_hp / player_max_hp
    pygame.draw.rect(game_canvas, RED if hp_ratio < 0.3 else (50, 220, 80), (20, 50, int(200 * hp_ratio), 16), border_radius=4)
    pygame.draw.rect(game_canvas, WHITE, (20, 50, 200, 16), 2, border_radius=4)
    hp_txt = font_small.render(f"HP: {int(player_hp)} / {player_max_hp}", True, WHITE)
    game_canvas.blit(hp_txt, (25, 49))

    # 玩家 經驗條 & 等級 UI
    req_exp = get_required_exp(player_level)
    exp_ratio = min(1.0, player_exp / req_exp)
    pygame.draw.rect(game_canvas, (30, 35, 50), (20, 72, 200, 14), border_radius=4)
    pygame.draw.rect(game_canvas, (0, 200, 255), (20, 72, int(200 * exp_ratio), 14), border_radius=4)
    pygame.draw.rect(game_canvas, WHITE, (20, 72, 200, 14), 2, border_radius=4)
    exp_txt = font_small.render(f"Lv.{player_level}  EXP: {player_exp} / {req_exp}", True, WHITE)
    game_canvas.blit(exp_txt, (25, 70))

    w1_k = pygame.key.name(KEYBINDS["weapon_1"]).upper()
    w2_k = pygame.key.name(KEYBINDS["weapon_2"]).upper()
    pick_k = pygame.key.name(KEYBINDS["interact"]).upper()
    game_canvas.blit(font_main.render(lang_dict["hud_info"].format(w1=w1_k, w2=w2_k, pick=pick_k), True, WHITE), (20, 20))

    if near_ground_weapon:
        w_name = lang_dict["weapons"].get(near_ground_weapon["type"], near_ground_weapon["type"])
        p_surf = font_main.render(lang_dict["pickup_prompt"].format(key=pick_k, weapon=w_name), True, YELLOW)
        game_canvas.blit(p_surf, (center_screen[0] - p_surf.get_width() // 2, center_screen[1] - 45))

    if current_time < notification_timer:
        n_surf = font_main.render(hud_notification, True, YELLOW)
        game_canvas.blit(n_surf, (center_screen[0] - n_surf.get_width() // 2, 98))

    # 右下角武器欄 UI
    for idx in range(2):
        slot_w = weapon_slots[idx]
        is_active = (idx == active_slot_idx)

        hud_x = VIRTUAL_WIDTH - 240 + (idx * 115)
        hud_y = VIRTUAL_HEIGHT - 90

        bg_col = (40, 50, 70, 220) if is_active else (20, 25, 35, 180)
        border_col = YELLOW if is_active else (70, 80, 100)

        pygame.draw.rect(game_canvas, bg_col, (hud_x, hud_y, 105, 70), border_radius=6)
        pygame.draw.rect(game_canvas, border_col, (hud_x, hud_y, 105, 70), 2 if is_active else 1, border_radius=6)

        slot_num_txt = font_small.render(f"[{idx + 1}]", True, YELLOW if is_active else GRAY)
        game_canvas.blit(slot_num_txt, (hud_x + 6, hud_y + 4))

        if slot_w:
            draw_weapon_icon(game_canvas, hud_x + 35, hud_y + 10, slot_w["id"])
            ammo_str = f"{slot_w['current_ammo']} / ∞" if slot_w["reserve_ammo"] == float('inf') else f"{slot_w['current_ammo']} / {slot_w['reserve_ammo']}"
            ammo_col = RED if slot_w["current_ammo"] == 0 else WHITE
            game_canvas.blit(font_hud.render(ammo_str, True, ammo_col), (hud_x + 10, hud_y + 38))
        else:
            emp_txt = font_main.render(lang_dict["empty_slot"], True, GRAY)
            game_canvas.blit(emp_txt, (hud_x + 52 - emp_txt.get_width() // 2, hud_y + 32))

    # 換彈狀態提示
    cur_weapon = weapon_slots[active_slot_idx]
    if cur_weapon and game_state == "PLAYING":
        if is_reloading:
            progress = min(1.0, (current_time - reload_start_time) / cur_weapon["reload_time"])
            bar_rect = pygame.Rect(center_screen[0] - 40, center_screen[1] + 32, 80, 6)
            pygame.draw.rect(game_canvas, (50, 50, 50), bar_rect, border_radius=3)
            pygame.draw.rect(game_canvas, YELLOW, (center_screen[0] - 40, center_screen[1] + 32, int(80 * progress), 6), border_radius=3)
            rel_txt = font_main.render(lang_dict["reloading"], True, YELLOW)
            game_canvas.blit(rel_txt, (center_screen[0] - rel_txt.get_width() // 2, center_screen[1] + 42))
        elif cur_weapon["current_ammo"] == 0 and cur_weapon["reserve_ammo"] > 0:
            no_ammo_txt = font_main.render(lang_dict["no_ammo"].format(reload_key=pygame.key.name(KEYBINDS["reload"]).upper()), True, RED)
            game_canvas.blit(no_ammo_txt, (center_screen[0] - no_ammo_txt.get_width() // 2, center_screen[1] + 35))

    # 死亡與暫停介面
    if game_state == "DEAD":
        dead_overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dead_overlay.fill((100, 0, 0, 160))
        game_canvas.blit(dead_overlay, (0, 0))

        d_title = font_title.render(lang_dict["you_died"], True, RED)
        d_prompt = font_main.render(lang_dict["respawn_prompt"], True, WHITE)

        game_canvas.blit(d_title, (VIRTUAL_WIDTH // 2 - d_title.get_width() // 2, VIRTUAL_HEIGHT // 2 - 50))
        game_canvas.blit(d_prompt, (VIRTUAL_WIDTH // 2 - d_prompt.get_width() // 2, VIRTUAL_HEIGHT // 2 + 10))

    if game_state == "PAUSED":
        pause_overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        pause_overlay.fill((0, 0, 0, 190))
        game_canvas.blit(pause_overlay, (0, 0))
        center_x = VIRTUAL_WIDTH // 2

        title_txt = font_title.render(lang_dict["title"], True, WHITE)
        game_canvas.blit(title_txt, (center_x - title_txt.get_width() // 2, 60))

        for tab_key, tab_rect in get_tab_rects(center_x):
            is_active = (current_tab == tab_key)
            pygame.draw.rect(game_canvas, TAB_ACTIVE if is_active else TAB_BG, tab_rect, border_top_left_radius=6, border_top_right_radius=6)
            pygame.draw.rect(game_canvas, WHITE if is_active else (80, 90, 110), tab_rect, 2, border_top_left_radius=6, border_top_right_radius=6)
            t_surf = font_tab.render(lang_dict[f"tab_{tab_key}"], True, WHITE if is_active else (150, 160, 180))
            game_canvas.blit(t_surf, (tab_rect.centerx - t_surf.get_width() // 2, tab_rect.centery - t_surf.get_height() // 2))

        panel_rect = pygame.Rect(center_x - 240, 160, 480, 310)
        pygame.draw.rect(game_canvas, (30, 35, 45), panel_rect, border_radius=8)
        pygame.draw.rect(game_canvas, (70, 80, 100), panel_rect, 2, border_radius=8)

        if current_tab == "video":
            mode_str = lang_dict["fullscreen"] if is_fullscreen else lang_dict["windowed"]
            size_txt = f"{lang_dict['win_size']}: {SCREEN_WIDTH}x{SCREEN_HEIGHT}" if not is_fullscreen else f"{lang_dict['win_size']}: {lang_dict['in_fullscreen']}"
            for text, btn_y, enabled in [(size_txt, 200, not is_fullscreen), (f"{lang_dict['mode']}: {mode_str}", 260, True)]:
                btn_rect = pygame.Rect(center_x - 170, btn_y, 340, 45)
                is_hover = btn_rect.collidepoint(virtual_mouse_pos) and enabled
                pygame.draw.rect(game_canvas, BUTTON_HOVER if is_hover else BUTTON_BG, btn_rect, border_radius=6)
                pygame.draw.rect(game_canvas, WHITE if is_hover else (100, 100, 120), btn_rect, 2, border_radius=6)
                txt_surf = font_main.render(text, True, WHITE if enabled else (130, 130, 140))
                game_canvas.blit(txt_surf, (center_x - txt_surf.get_width() // 2, btn_y + 10))

        elif current_tab == "general":
            btn_rect = pygame.Rect(center_x - 170, 200, 340, 45)
            is_hover = btn_rect.collidepoint(virtual_mouse_pos)
            pygame.draw.rect(game_canvas, BUTTON_HOVER if is_hover else BUTTON_BG, btn_rect, border_radius=6)
            pygame.draw.rect(game_canvas, WHITE if is_hover else (100, 100, 120), btn_rect, 2, border_radius=6)
            txt_surf = font_main.render(f"{lang_dict['lang']}: {lang_dict['lang_name']}", True, WHITE)
            game_canvas.blit(txt_surf, (center_x - txt_surf.get_width() // 2, 210))

        elif current_tab == "keybinds":
            for i, (action, key_code) in enumerate(list(KEYBINDS.items())):
                btn_y = 175 + i * 32
                btn_rect = pygame.Rect(center_x - 200, btn_y, 400, 28)
                is_binding_this = (binding_key_target == action)
                is_hover = btn_rect.collidepoint(virtual_mouse_pos) and not binding_key_target

                pygame.draw.rect(game_canvas, (90, 70, 30) if is_binding_this else (BUTTON_HOVER if is_hover else BUTTON_BG), btn_rect, border_radius=4)
                pygame.draw.rect(game_canvas, WHITE if (is_hover or is_binding_this) else (80, 90, 110), btn_rect, 1, border_radius=4)

                txt_action = font_small.render(lang_dict["key_names"].get(action, action), True, WHITE)
                txt_key = font_small.render(lang_dict["press_any_key"] if is_binding_this else pygame.key.name(key_code).upper(), True, (255, 220, 100) if is_binding_this else WHITE)

                game_canvas.blit(txt_action, (center_x - 180, btn_y + 4))
                game_canvas.blit(txt_key, (center_x + 180 - txt_key.get_width(), btn_y + 4))

        elif current_tab == "audio":
            txt_surf = font_main.render(lang_dict["audio_coming_soon"], True, (150, 160, 180))
            game_canvas.blit(txt_surf, (center_x - txt_surf.get_width() // 2, 280))

        btn_resume, btn_quit = pygame.Rect(center_x - 170, 490, 160, 45), pygame.Rect(center_x + 10, 490, 160, 45)
        pygame.draw.rect(game_canvas, BUTTON_HOVER if btn_resume.collidepoint(virtual_mouse_pos) else BUTTON_BG, btn_resume, border_radius=6)
        pygame.draw.rect(game_canvas, WHITE if btn_resume.collidepoint(virtual_mouse_pos) else (100, 100, 120), btn_resume, 2, border_radius=6)
        txt_res = font_main.render(lang_dict["continue"], True, WHITE)
        game_canvas.blit(txt_res, (btn_resume.centerx - txt_res.get_width() // 2, btn_resume.centery - txt_res.get_height() // 2))

        pygame.draw.rect(game_canvas, QUIT_HOVER if btn_quit.collidepoint(virtual_mouse_pos) else QUIT_BG, btn_quit, border_radius=6)
        pygame.draw.rect(game_canvas, WHITE if btn_quit.collidepoint(virtual_mouse_pos) else (150, 80, 80), btn_quit, 2, border_radius=6)
        txt_quit = font_main.render(lang_dict["quit_game"], True, WHITE)
        game_canvas.blit(txt_quit, (btn_quit.centerx - txt_quit.get_width() // 2, btn_quit.centery - txt_quit.get_height() // 2))

    scaled_surface = pygame.transform.scale(game_canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()