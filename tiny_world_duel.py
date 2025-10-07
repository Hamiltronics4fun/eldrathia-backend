# Tiny World — Duel Edition (Visual + Touch)
# Explore mode: move around, pick up the Sword, press E next to the Knight to start a battle.
# Battle mode: Attack or Run. Sword makes you stronger so you can win reliably.
# Controls: Touch buttons OR keyboard (WASD/Arrows, E interact, Q quit, I inventory)

import pygame, sys, random, os

# ---------- WORLD ----------
WORLD_W, WORLD_H = 10, 6
TILE = 64
HUD_H = 140
SCREEN_W, SCREEN_H = WORLD_W*TILE, WORLD_H*TILE + HUD_H

world_map = [
    list(".........."),
    list("..~~~....."),
    list("..~~~....."),
    list("..~~~..##."),
    list("......##.."),
    list(".........."),
]

def passable(x, y):
    return (0 <= x < WORLD_W and 0 <= y < WORLD_H and world_map[y][x] not in ("#", "~"))

def adjacent(ax, ay, bx, by):
    return abs(ax - bx) + abs(ay - by) == 1

# ---------- ENTITIES & ITEMS ----------
player = {
    "x": 2, "y": 2, "hp": 40, "hp_max": 40,
    "bag": [], "gold": 0, "attack_bonus": 0
}
knight = {
    "x": 7, "y": 3, "hp": 60, "hp_max": 60,
    # Random-ish stats that are fair: without sword it's tough; with sword it's easy
    "min_dmg": random.randint(6, 7),   # 6–7
    "max_dmg": random.randint(8, 9),   # 8–9
    "acc": 0.80                         # 80% hit chance
}

sword = {"x": 4, "y": 1, "name": "Sword of Dawn"}  # safe grass tile

# ---------- GAME STATE ----------
mode = "explore"  # "explore" or "battle"
message = "Find the sword (*) and press E near the Knight (K) to battle."
log_lines = []

def add_log(text):
    log_lines.append(text)
    if len(log_lines) > 4:
        del log_lines[0]

# ---------- PYGAME ----------
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
pygame.display.set_caption("Tiny World — Duel Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
bigfont = pygame.font.SysFont(None, 30)
smallfont = pygame.font.SysFont(None, 22)

# Colors
C_GRASS=(34,139,34); C_WATER=(30,90,180); C_WALL=(90,90,90)
C_HUDBG=(15,15,20); C_TEXT=(230,230,230); C_HINT=(170,200,255)
C_PANEL=(25,25,35); C_HP_BG=(60,25,25); C_HP=(210,60,60); C_HP2=(60,160,60)
C_BTN=(45,45,55); C_BTN_TXT=(230,230,230); C_BTN_HI=(70,70,95)

# Try loading sprites (optional)
def load_scaled(name, w, h):
    if os.path.exists(name):
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.smoothscale(img, (w, h))
    return None

player_img = load_scaled("player.png", TILE, TILE)
knight_img = load_scaled("knight.png", TILE, TILE)
sword_img  = load_scaled("sword.png",  int(TILE*0.6), int(TILE*0.6))

# ---------- UI Layout ----------
PAD_Y = WORLD_H*TILE + 8
BTN = 56; GAP = 10
dp_cx = 10 + BTN + GAP
btn_up    = pygame.Rect(dp_cx, PAD_Y, BTN, BTN)
btn_down  = pygame.Rect(dp_cx, PAD_Y + BTN*2, BTN, BTN)
btn_left  = pygame.Rect(10, PAD_Y + BTN, BTN, BTN)
btn_right = pygame.Rect(10 + BTN*2, PAD_Y + BTN, BTN, BTN)
btn_e = pygame.Rect(SCREEN_W - (BTN*3 + GAP*3), PAD_Y, BTN, BTN)
btn_i = pygame.Rect(SCREEN_W - (BTN*2 + GAP*2), PAD_Y, BTN, BTN)
btn_q = pygame.Rect(SCREEN_W - (BTN + GAP), PAD_Y, BTN, BTN)

# Battle buttons (centered)
bBTN = 90
btn_atk = pygame.Rect(SCREEN_W//2 - bBTN - 10, PAD_Y, bBTN, BTN)
btn_run = pygame.Rect(SCREEN_W//2 + 10,       PAD_Y, bBTN, BTN)

def draw_button(r, label, hi=False):
    pygame.draw.rect(screen, C_BTN_HI if hi else C_BTN, r, border_radius=10)
    txt = font.render(label, True, C_BTN_TXT)
    screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))

# ---------- RENDER ----------
def draw_hp_bar(x, y, w, h, hp, hp_max, color):
    pygame.draw.rect(screen, C_HP_BG, (x, y, w, h), border_radius=6)
    ratio = max(0, min(1, hp/float(hp_max)))
    pygame.draw.rect(screen, color, (x, y, int(w*ratio), h), border_radius=6)

def wrap_text(text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.size(test)[0] > width and cur:
            lines.append(cur); cur = w
        else:
            cur = test
    if cur: lines.append(cur)
    return lines

def draw_world():
    # tiles
    for y in range(WORLD_H):
        for x in range(WORLD_W):
            r = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
            ch = world_map[y][x]
            pygame.draw.rect(screen, C_WATER if ch=="~" else C_WALL if ch=="#" else C_GRASS, r)
            pygame.draw.rect(screen, (0,0,0), r, 1)
    # sword
    if sword:
        if sword_img:
            screen.blit(sword_img, (sword["x"]*TILE + TILE*0.2, sword["y"]*TILE + TILE*0.2))
        else:
            cx, cy = sword["x"]*TILE + TILE//2, sword["y"]*TILE + TILE//2
            pygame.draw.circle(screen, (250,215,80), (cx,cy), TILE//6)
            pygame.draw.circle(screen, (140,110,30), (cx,cy), TILE//6, 2)
    # knight
    if knight_img:
        screen.blit(knight_img, (knight["x"]*TILE, knight["y"]*TILE))
    else:
        nx, ny = knight["x"]*TILE + TILE//2, knight["y"]*TILE + TILE//2
        pygame.draw.rect(screen, (200,60,60), (nx - TILE//4, ny - TILE//4, TILE//2, TILE//2), border_radius=8)
        ktxt = smallfont.render("K", True, (255,255,255))
        screen.blit(ktxt, (nx - ktxt.get_width()//2, ny - ktxt.get_height()//2))
    # player
    if player_img:
        screen.blit(player_img, (player["x"]*TILE, player["y"]*TILE))
    else:
        px, py = player["x"]*TILE + TILE//2, player["y"]*TILE + TILE//2
        pygame.draw.circle(screen, (240,220,60), (px, py), TILE//3)

def draw_hud():
    pygame.draw.rect(screen, C_HUDBG, (0, WORLD_H*TILE, SCREEN_W, HUD_H))
    # Left stats panel
    panel = pygame.Rect(8, WORLD_H*TILE + 8, 230, HUD_H - 16)
    pygame.draw.rect(screen, C_PANEL, panel, border_radius=10)
    # Player HP
    screen.blit(smallfont.render("YOU", True, C_TEXT), (panel.x+10, panel.y+6))
    draw_hp_bar(panel.x+10, panel.y+24, panel.width-20, 16, player["hp"], player["hp_max"], C_HP2)
    # Knight HP
    screen.blit(smallfont.render("KNIGHT", True, C_TEXT), (panel.x+10, panel.y+48))
    draw_hp_bar(panel.x+10, panel.y+66, panel.width-20, 16, knight["hp"], knight["hp_max"], C_HP)
    # Inventory
    inv_str = "Inv: " + (", ".join(player["bag"]) if player["bag"] else "(empty)")
    screen.blit(smallfont.render(inv_str, True, C_TEXT), (panel.x+10, panel.y+92))

    # Message panel
    msg_area = pygame.Rect(panel.right + 10, WORLD_H*TILE + 8, SCREEN_W - (panel.width + 18), 72)
    pygame.draw.rect(screen, C_PANEL, msg_area, border_radius=10)
    for i, line in enumerate(wrap_text(message, bigfont, msg_area.width - 12)[:2]):
        screen.blit(bigfont.render(line, True, C_TEXT), (msg_area.x+6, msg_area.y+6 + 28*i))

    # Log lines
    log_area = pygame.Rect(panel.right + 10, msg_area.bottom + 6, SCREEN_W - (panel.width + 18), 44)
    pygame.draw.rect(screen, C_PANEL, log_area, border_radius=10)
    for i, line in enumerate(log_lines[-2:]):
        screen.blit(smallfont.render(line, True, C_HINT), (log_area.x+6, log_area.y+6 + 18*i))

def draw_ui_explore():
    draw_button(btn_up, "▲"); draw_button(btn_down, "▼")
    draw_button(btn_left, "◀"); draw_button(btn_right, "▶")
    draw_button(btn_e, "E"); draw_button(btn_i, "I"); draw_button(btn_q, "Q")

def draw_ui_battle():
    draw_button(btn_atk, "ATK")
    draw_button(btn_run, "RUN")

def draw_all():
    screen.fill((0,0,0))
    draw_world()
    draw_hud()
    if mode == "explore":
        draw_ui_explore()
    else:
        draw_ui_battle()
    pygame.display.flip()

# ---------- GAMEPLAY ----------
def move_entity(ent, dx, dy):
    nx, ny = ent["x"] + dx, ent["y"] + dy
    if passable(nx, ny) and not (ent is not knight and nx == knight["x"] and ny == knight["y"]):
        ent["x"], ent["y"] = nx, ny
        return True
    return False

def npc_wander():
    for dx,dy in random.sample([(0,-1),(0,1),(-1,0),(1,0)], 4):
        nx, ny = knight["x"] + dx, knight["y"] + dy
        if passable(nx, ny) and not (nx == player["x"] and ny == player["y"]):
            knight["x"], knight["y"] = nx, ny
            break

def interact():
    global sword, mode, message
    # pick up sword
    if sword and (player["x"], player["y"]) == (sword["x"], sword["y"]):
        player["bag"].append(sword["name"])
        player["attack_bonus"] = 6  # big boost -> makes you stronger than knight
        add_log("You picked up the Sword of Dawn (+6 dmg)!")
        message = "You feel power surging through the blade."
        sword = None
        return
    # start battle if adjacent to knight
    if adjacent(player["x"], player["y"], knight["x"], knight["y"]):
        start_battle()
    else:
        message = "Nothing to interact with here."

def start_battle():
    global mode, message
    mode = "battle"
    message = "Battle started! Attack or Run."
    add_log("You face the Knight!")

def player_attack():
    """Player attacks Knight (with sword bonus if obtained)."""
    base_min, base_max = 4, 7  # without sword, you're weaker
    bonus = player["attack_bonus"]
    dmg = random.randint(base_min, base_max) + bonus
    hit_chance = 0.85  # 85% to hit
    if random.random() <= hit_chance:
        knight["hp"] = max(0, knight["hp"] - dmg)
        add_log(f"You hit for {dmg}!")
    else:
        add_log("You missed!")

def knight_attack():
    """Knight counterattacks."""
    if knight["hp"] <= 0:
        return
    if random.random() <= knight["acc"]:
        dmg = random.randint(knight["min_dmg"], knight["max_dmg"])
        player["hp"] = max(0, player["hp"] - dmg)
        add_log(f"Knight hits you for {dmg}!")
    else:
        add_log("Knight missed!")

def battle_turn():
    """One full round after player chooses ATK: you attack, then knight attacks if alive."""
    global mode, message
    player_attack()
    if knight["hp"] <= 0:
        message = "You defeated the Knight!"
        add_log("Victory! +20 gold.")
        player["gold"] += 20
        mode = "explore"
        return
    knight_attack()
    if player["hp"] <= 0:
        message = "You were defeated..."
        add_log("You fall. Game over (reload to try again).")
        mode = "explore"

def run_from_battle():
    global mode, message
    message = "You fled from the battle."
    add_log("You retreat to safety.")
    mode = "explore"

def inventory_text():
    return "Inv: " + (", ".join(player["bag"]) if player["bag"] else "(empty)")

# ---------- INPUT HELPERS ----------
def handle_explore_action(action):
    global message
    moved = False
    if action == "up":    moved = move_entity(player, 0, -1)
    elif action == "down":  moved = move_entity(player, 0,  1)
    elif action == "left":  moved = move_entity(player, -1, 0)
    elif action == "right": moved = move_entity(player,  1, 0)
    elif action == "e":
        interact(); npc_wander(); draw_all(); return
    elif action == "i":
        message = inventory_text(); draw_all(); return
    elif action == "q":
        pygame.quit(); sys.exit()
    if moved:
        # context message
        if sword and (player["x"], player["y"]) == (sword["x"], sword["y"]):
            message = "A sword lies here. Press E to pick it up."
        else:
            message = ""
        npc_wander()
    draw_all()

def handle_battle_action(action):
    if action == "atk":
        battle_turn(); draw_all()
    elif action == "run":
        run_from_battle(); draw_all()

# ---------- MAIN LOOP ----------
draw_all()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif e.type == pygame.KEYDOWN:
            if   e.key in (pygame.K_q, pygame.K_ESCAPE): handle_explore_action("q") if mode=="explore" else run_from_battle()
            elif mode == "explore":
                if e.key in (pygame.K_a, pygame.K_LEFT):   handle_explore_action("left")
                elif e.key in (pygame.K_d, pygame.K_RIGHT): handle_explore_action("right")
                elif e.key in (pygame.K_w, pygame.K_UP):    handle_explore_action("up")
                elif e.key in (pygame.K_s, pygame.K_DOWN):  handle_explore_action("down")
                elif e.key == pygame.K_e:                   handle_explore_action("e")
                elif e.key == pygame.K_i:                   handle_explore_action("i")
            else:  # battle
                if e.key == pygame.K_e or e.key == pygame.K_RETURN:
                    handle_battle_action("atk")
                elif e.key == pygame.K_r or e.key == pygame.K_BACKSPACE:
                    handle_battle_action("run")
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            x,y = e.pos
            if mode == "explore":
                if   btn_up.collidepoint(x,y):    handle_explore_action("up")
                elif btn_down.collidepoint(x,y):  handle_explore_action("down")
                elif btn_left.collidepoint(x,y):  handle_explore_action("left")
                elif btn_right.collidepoint(x,y): handle_explore_action("right")
                elif btn_e.collidepoint(x,y):     handle_explore_action("e")
                elif btn_i.collidepoint(x,y):     handle_explore_action("i")
                elif btn_q.collidepoint(x,y):     handle_explore_action("q")
            else:
                if   btn_atk.collidepoint(x,y): handle_battle_action("atk")
                elif btn_run.collidepoint(x,y): handle_battle_action("run")
    clock.tick(60)
